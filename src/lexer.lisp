;;;; Clython Lexer — Python 3.12 tokenizer
;;;;
;;;; Implements the token stream defined in Python 3.12 Language Reference
;;;; Section 2: Lexical Analysis (https://docs.python.org/3.12/reference/lexical_analysis.html)

(defpackage :clython.lexer
  (:use :cl)
  (:export
   ;; Main entry point
   #:tokenize
   ;; Token struct accessors
   #:token
   #:token-type
   #:token-value
   #:token-line
   #:token-column
   ;; Token type keywords (for documentation / introspection)
   ;; :NAME :NUMBER :STRING :NEWLINE :INDENT :DEDENT :ENDMARKER :OP
   ;; Condition
   #:lexer-error
   #:lexer-error-message
   #:lexer-error-line
   #:lexer-error-column))

(in-package :clython.lexer)

;;;; ─── Conditions ────────────────────────────────────────────────────────────

(define-condition lexer-error (error)
  ((message :initarg :message :reader lexer-error-message)
   (line    :initarg :line    :reader lexer-error-line    :initform 0)
   (column  :initarg :column  :reader lexer-error-column  :initform 0))
  (:report (lambda (c stream)
             (format stream "LexerError at line ~A col ~A: ~A"
                     (lexer-error-line c)
                     (lexer-error-column c)
                     (lexer-error-message c)))))

;;;; ─── Token struct ──────────────────────────────────────────────────────────

(defstruct token
  "A lexical token with type (keyword), string value, 1-based line, 0-based column."
  (type   nil :type symbol)
  (value  ""  :type string)
  (line   1   :type fixnum)
  (column 0   :type fixnum))

;;;; ─── Keyword sets ──────────────────────────────────────────────────────────

(defparameter *keywords*
  '("False" "None" "True"
    "and" "as" "assert" "async" "await"
    "break" "class" "continue"
    "def" "del" "elif" "else" "except"
    "finally" "for" "from" "global"
    "if" "import" "in" "is"
    "lambda" "nonlocal" "not" "or"
    "pass" "raise" "return"
    "try" "while" "with" "yield")
  "Hard keywords in Python 3.12.")

(defparameter *soft-keywords*
  '("match" "case" "type" "_")
  "Soft keywords in Python 3.12 (context-sensitive; emitted as NAME).")

(defparameter *keyword-set*
  (let ((ht (make-hash-table :test #'equal)))
    (dolist (kw *keywords*)
      (setf (gethash kw ht) t))
    ht)
  "Hash-set for O(1) keyword lookup.")

;;;; ─── Operator / delimiter tables ──────────────────────────────────────────
;;;;
;;;; Ordered longest-first so greedy matching works correctly.

(defparameter *operators*
  '(;; 3-char
    "**=" "//=" "<<=" ">>=" "..."
    ;; 2-char
    "+=" "-=" "*=" "/=" "%=" "&=" "|=" "^=" "@="
    "**" "//" "<<" ">>" "<=" ">=" "==" "!=" "->"
    ":=" "~"
    ;; 1-char
    "+" "-" "*" "/" "%" "&" "|" "^" "~" "<" ">" "=" "@"
    "." "," ";" ":" "(" ")" "[" "]" "{" "}" "!")
  "All Python operators and delimiters, longest-first.")

;;;; ─── Lexer state ───────────────────────────────────────────────────────────

(defstruct lexer-state
  "Mutable state threaded through the tokenizer."
  (source      ""  :type string)
  (pos         0   :type fixnum)   ; current character index
  (line        1   :type fixnum)
  (column      0   :type fixnum)
  (indent-stack (list 0))          ; stack of indentation levels
  (paren-depth 0   :type fixnum)   ; ( [ { nesting depth
  (tokens      '())                ; accumulated token list (reversed)
  (pending-nl  nil)                ; deferred NEWLINE token
  )

(defun ls-char (ls &optional (offset 0))
  "Return the character at pos+offset, or NIL at end-of-source."
  (let ((i (+ (lexer-state-pos ls) offset)))
    (when (< i (length (lexer-state-source ls)))
      (char (lexer-state-source ls) i))))

(defun ls-advance (ls)
  "Consume one character; return it."
  (let ((ch (ls-char ls)))
    (incf (lexer-state-pos ls))
    (if (eql ch #\Newline)
        (progn (incf (lexer-state-line ls))
               (setf (lexer-state-column ls) 0))
        (incf (lexer-state-column ls)))
    ch))

(defun ls-peek-string (ls len)
  "Return the next LEN characters as a string without advancing."
  (let* ((src (lexer-state-source ls))
         (start (lexer-state-pos ls))
         (end (min (+ start len) (length src))))
    (subseq src start end)))

(defun ls-at-end-p (ls)
  (>= (lexer-state-pos ls) (length (lexer-state-source ls))))

(defun ls-emit (ls type value &optional (line (lexer-state-line ls))
                                         (col  (lexer-state-column ls)))
  "Push a token onto the reversed token list."
  (push (make-token :type type :value value :line line :column col)
        (lexer-state-tokens ls)))

;;;; ─── Character predicates ──────────────────────────────────────────────────

(defun identifier-start-p (ch)
  "True if CH can begin a Python identifier (letter or underscore)."
  (and ch (or (alpha-char-p ch) (char= ch #\_)
              ;; Accept non-ASCII for full Unicode ident support
              (> (char-code ch) 127))))

(defun identifier-continue-p (ch)
  "True if CH can continue a Python identifier."
  (and ch (or (alphanumericp ch) (char= ch #\_)
              (> (char-code ch) 127))))

(defun digit-p (ch &optional (radix 10))
  (and ch (digit-char-p ch radix)))

(defun hex-digit-p (ch) (digit-p ch 16))
(defun octal-digit-p (ch) (digit-p ch 8))
(defun binary-digit-p (ch) (and ch (or (char= ch #\0) (char= ch #\1))))

;;;; ─── Helper: read characters while predicate holds ─────────────────────────

(defun read-while (ls pred)
  "Consume characters while PRED returns true; return the collected string."
  (with-output-to-string (s)
    (loop while (funcall pred (ls-char ls))
          do (write-char (ls-advance ls) s))))

;;;; ─── Indentation handling ───────────────────────────────────────────────────

(defun compute-indent (line)
  "Return the column of the first non-space, non-tab character.
   Tabs expand to the next multiple of 8 (Python standard)."
  (let ((col 0))
    (loop for ch across line do
      (cond ((char= ch #\Space) (incf col))
            ((char= ch #\Tab)   (setf col (* 8 (1+ (floor col 8)))))
            (t (return))))
    col))

(defun process-indent (ls indent-level line col)
  "Emit INDENT/DEDENT tokens as needed to match INDENT-LEVEL."
  (let ((stack (lexer-state-indent-stack ls)))
    (cond
      ;; Increase: push one INDENT
      ((> indent-level (car stack))
       (push indent-level (lexer-state-indent-stack ls))
       (ls-emit ls :indent "" line col))
      ;; Decrease: pop DEDENTs until we match
      ((< indent-level (car stack))
       (loop while (and (cdr (lexer-state-indent-stack ls))
                        (> (car (lexer-state-indent-stack ls)) indent-level))
             do (pop (lexer-state-indent-stack ls))
                (ls-emit ls :dedent "" line col))
       (unless (= (car (lexer-state-indent-stack ls)) indent-level)
         (error 'lexer-error
                :message "Inconsistent indentation"
                :line line :column col)))
      ;; Same level: nothing
      (t nil))))

;;;; ─── Logical-line scanner ───────────────────────────────────────────────────
;;;;
;;;; Python source is first pre-split into physical lines. Explicit line
;;;; joining (trailing \) and implicit line joining (inside brackets) are
;;;; handled during tokenization, not pre-processing.

(defun scan-string (ls)
  "Scan a string/bytes/f-string literal; emit a :STRING token."
  (let* ((save-line   (lexer-state-line ls))
         (save-col    (lexer-state-column ls))
         (buf         (make-string-output-stream))
         ;; Collect optional prefix characters (r, b, f, u — case-insensitive)
         (prefix      (with-output-to-string (p)
                        (loop for ch = (ls-char ls)
                              while (and ch (member (char-downcase ch)
                                                    '(#\r #\b #\f #\u)))
                              do (write-char (ls-advance ls) p))))
         (ch          (ls-char ls)))

    ;; Validate prefix — f and b cannot be combined (fb or bf are invalid)
    (let ((lp (string-downcase prefix)))
      (when (and (find #\f lp) (find #\b lp))
        (error 'lexer-error :message "SyntaxError: cannot combine 'f' prefix with 'b' prefix"
               :line save-line :column save-col)))

    ;; Determine quote style
    (unless (and ch (or (char= ch #\') (char= ch #\")))
      (error 'lexer-error :message "Expected quote character"
             :line save-line :column save-col))

    (write-string prefix buf)
    (let* ((quote-char ch)
           (triple-p   (string= (ls-peek-string ls 3)
                                (make-string 3 :initial-element quote-char)))
           (close-str  (if triple-p
                           (make-string 3 :initial-element quote-char)
                           (string quote-char)))
)

      ;; Consume opening quote(s)
      (write-string (ls-peek-string ls (if triple-p 3 1)) buf)
      (dotimes (_ (if triple-p 3 1)) (ls-advance ls))

      ;; Scan until matching close
      (loop
        (when (ls-at-end-p ls)
          (error 'lexer-error :message "Unterminated string literal"
                 :line save-line :column save-col))
        (let ((s (ls-peek-string ls (if triple-p 3 1))))
          (when (string= s close-str)
            ;; Consume closing quote(s)
            (write-string close-str buf)
            (dotimes (_ (if triple-p 3 1)) (ls-advance ls))
            (return)))
        ;; Handle escape sequences
        (if (char= (ls-char ls) #\\)
            (let ((esc-ch (progn (write-char (ls-advance ls) buf)
                                 (ls-advance ls))))
              (when esc-ch
                (write-char esc-ch buf)))
            (write-char (ls-advance ls) buf)))

            ;; Emit with appropriate type based on prefix
      (let ((token-type (if (find #\f (string-downcase prefix))
                            :fstring
                            :string)))
        (ls-emit ls token-type (get-output-stream-string buf) save-line save-col)))))

(defun scan-number (ls)
  "Scan a numeric literal (int/float/complex); emit a :NUMBER token."
  (let ((save-line (lexer-state-line ls))
        (save-col  (lexer-state-column ls)))
    (with-output-to-string (buf)
      (let ((value
              (with-output-to-string (buf)
                ;; Determine radix
                (cond
                  ;; 0x / 0X — hex
                  ((and (char= (ls-char ls) #\0)
                        (member (ls-char ls 1) '(#\x #\X)))
                   (write-char (ls-advance ls) buf)  ; 0
                   (write-char (ls-advance ls) buf)  ; x/X
                   ;; hex digits with optional underscores
                   (loop do
                     (when (hex-digit-p (ls-char ls))
                       (write-char (ls-advance ls) buf))
                     (when (and (eql (ls-char ls) #\_)
                                (hex-digit-p (ls-char ls 1)))
                       (write-char (ls-advance ls) buf))
                     while (hex-digit-p (ls-char ls))))
                  ;; 0o / 0O — octal
                  ((and (char= (ls-char ls) #\0)
                        (member (ls-char ls 1) '(#\o #\O)))
                   (write-char (ls-advance ls) buf)
                   (write-char (ls-advance ls) buf)
                   (loop do
                     (when (octal-digit-p (ls-char ls))
                       (write-char (ls-advance ls) buf))
                     (when (and (eql (ls-char ls) #\_)
                                (octal-digit-p (ls-char ls 1)))
                       (write-char (ls-advance ls) buf))
                     while (octal-digit-p (ls-char ls))))
                  ;; 0b / 0B — binary
                  ((and (char= (ls-char ls) #\0)
                        (member (ls-char ls 1) '(#\b #\B)))
                   (write-char (ls-advance ls) buf)
                   (write-char (ls-advance ls) buf)
                   (loop do
                     (when (binary-digit-p (ls-char ls))
                       (write-char (ls-advance ls) buf))
                     (when (and (eql (ls-char ls) #\_)
                                (binary-digit-p (ls-char ls 1)))
                       (write-char (ls-advance ls) buf))
                     while (binary-digit-p (ls-char ls))))
                  ;; Decimal (possibly float/complex)
                  (t
                   ;; Integer part (may be empty for .5 style)
                   (unless (char= (ls-char ls) #\.)
                     (let ((first-digit (ls-char ls)))
                       (loop do
                         (when (digit-p (ls-char ls))
                           (write-char (ls-advance ls) buf))
                         (when (and (eql (ls-char ls) #\_)
                                    (digit-p (ls-char ls 1)))
                           (write-char (ls-advance ls) buf))
                         while (digit-p (ls-char ls)))
                       ;; Check for leading zeros (e.g. 01, 007)
                       (let ((int-part (get-output-stream-string buf)))
                         ;; Reset buffer with the int-part content
                         (write-string int-part buf)
                         (when (and (char= first-digit #\0)
                                    (> (length int-part) 1)
                                    ;; Allow all-zeros (00, 000, 0_0, etc.)
                                    (find-if (lambda (c) (and (digit-char-p c) (char/= c #\0))) int-part)
                                    (not (eql (ls-char ls) #\.))  ;; allow 0.5
                                    (not (eql (ls-char ls) #\e))  ;; allow 0e1
                                    (not (eql (ls-char ls) #\E))
                                    (not (eql (ls-char ls) #\j))  ;; allow 0j
                                    (not (eql (ls-char ls) #\J)))
                           (error 'lexer-error
                                  :message "leading zeros in decimal integer literals are not permitted"
                                  :line save-line :column save-col)))))
                   ;; Fractional part
                   (when (and (eql (ls-char ls) #\.)
                              ;; avoid consuming .. or .identifier
                              (not (eql (ls-char ls 1) #\.))
                              (or (digit-p (ls-char ls 1))
                                  ;; allow trailing dot: 1.
                                  (not (identifier-start-p (ls-char ls 1)))))
                     (write-char (ls-advance ls) buf) ; .
                     (loop do
                       (when (digit-p (ls-char ls))
                         (write-char (ls-advance ls) buf))
                       (when (and (eql (ls-char ls) #\_)
                                  (digit-p (ls-char ls 1)))
                         (write-char (ls-advance ls) buf))
                       while (digit-p (ls-char ls))))
                   ;; Exponent
                   (when (member (ls-char ls) '(#\e #\E))
                     (write-char (ls-advance ls) buf)
                     (when (member (ls-char ls) '(#\+ #\-))
                       (write-char (ls-advance ls) buf))
                     (loop do
                       (when (digit-p (ls-char ls))
                         (write-char (ls-advance ls) buf))
                       (when (and (eql (ls-char ls) #\_)
                                  (digit-p (ls-char ls 1)))
                         (write-char (ls-advance ls) buf))
                       while (digit-p (ls-char ls))))
                   ;; Complex suffix j/J
                   (when (member (ls-char ls) '(#\j #\J))
                     (write-char (ls-advance ls) buf)))))))
        ;; Reject digit-start identifiers like 1invalid (SyntaxError in CPython)
        (when (and (ls-char ls)
                   (identifier-start-p (ls-char ls))
                   ;; Don't reject j/J — already consumed as complex suffix
                   )
          (error 'lexer-error
                 :message "invalid decimal literal"
                 :line save-line :column save-col))
        (ls-emit ls :number value save-line save-col)))))

(defun scan-identifier (ls)
  "Scan an identifier or keyword; emit :name or :keyword token."
  (let ((save-line (lexer-state-line ls))
        (save-col  (lexer-state-column ls))
        (name      (with-output-to-string (buf)
                     (loop while (identifier-continue-p (ls-char ls))
                           do (write-char (ls-advance ls) buf)))))
    (if (gethash name *keyword-set*)
        (ls-emit ls :keyword name save-line save-col)
        (ls-emit ls :name    name save-line save-col))))

(defun scan-operator (ls)
  "Match the longest operator/delimiter at current position; emit :OP."
  (let ((save-line (lexer-state-line ls))
        (save-col  (lexer-state-column ls)))
    ;; Try operators longest-first
    (dolist (op *operators*)
      (let ((len (length op)))
        (when (string= (ls-peek-string ls len) op)
          ;; Advance past operator
          (dotimes (_ len) (ls-advance ls))
          ;; Track bracket depth
          (cond ((member op '("(" "[" "{") :test #'equal)
                 (incf (lexer-state-paren-depth ls)))
                ((member op '(")" "]" "}") :test #'equal)
                 (when (> (lexer-state-paren-depth ls) 0)
                   (decf (lexer-state-paren-depth ls)))))
          (ls-emit ls :op op save-line save-col)
          (return-from scan-operator t))))
    ;; Unknown character — skip and emit error token
    (let ((ch (ls-advance ls)))
      (error 'lexer-error
             :message (format nil "Unknown character: ~S (~A)"
                              ch (char-code ch))
             :line save-line :column save-col))))

;;;; ─── Handle a physical line of source ──────────────────────────────────────

(defun scan-logical-line (ls)
  "Scan tokens from the current position up to (but not emitting) NEWLINE.
   Handles implicit line continuation inside brackets.
   Returns T if a physical newline was consumed."
  (loop
    (cond
      ;; End of source
      ((ls-at-end-p ls) (return t))

      ;; Newline
      ((eql (ls-char ls) #\Newline)
       (let ((nl-line (lexer-state-line ls))
             (nl-col  (lexer-state-column ls)))
         (ls-advance ls)   ; consume the newline
         ;; Emit NEWLINE only when not inside brackets
         (when (zerop (lexer-state-paren-depth ls))
           (ls-emit ls :newline "" nl-line nl-col))
         (return t)))

      ;; Explicit line continuation: backslash before newline
      ((and (eql (ls-char ls) #\\)
            (eql (ls-char ls 1) #\Newline))
       (ls-advance ls) ; \
       (ls-advance ls) ; newline
       ;; Continue scanning on next physical line — no NEWLINE token
       )

      ;; Carriage return (Windows CRLF)
      ((eql (ls-char ls) #\Return)
       (ls-advance ls)
       (when (eql (ls-char ls) #\Newline)
         (ls-advance ls))
       (when (zerop (lexer-state-paren-depth ls))
         (ls-emit ls :newline "" (lexer-state-line ls) (lexer-state-column ls)))
       (return t))

      ;; Comment — consume to end of line but don't emit
      ((eql (ls-char ls) #\#)
       (loop while (and (ls-char ls)
                        (not (eql (ls-char ls) #\Newline)))
             do (ls-advance ls)))

      ;; Null bytes — skip silently (CPython's functools.py has one at line 1013)
      ((eql (ls-char ls) #\Nul)
       (ls-advance ls))

      ;; Whitespace (spaces/tabs within a line — not leading)
      ((and (eql (ls-char ls) #\Space))
       (ls-advance ls))
      ((and (eql (ls-char ls) #\Tab))
       (ls-advance ls))

      ;; String literal
      ((or (and (ls-char ls)
                (or (char= (ls-char ls) #\')
                    (char= (ls-char ls) #\")))
           ;; String prefix characters
           (and (ls-char ls)
                (member (char-downcase (ls-char ls)) '(#\r #\b #\f #\u))
                (ls-char ls 1)
                (or (char= (ls-char ls 1) #\')
                    (char= (ls-char ls 1) #\")
                    (and (member (char-downcase (ls-char ls 1)) '(#\r #\b #\f))
                         (ls-char ls 2)
                         (or (char= (ls-char ls 2) #\')
                             (char= (ls-char ls 2) #\"))))))
       (scan-string ls))

      ;; Number — digit, or .digit
      ((or (digit-p (ls-char ls))
           (and (eql (ls-char ls) #\.)
                (digit-p (ls-char ls 1))))
       (scan-number ls))

      ;; Identifier or keyword
      ((identifier-start-p (ls-char ls))
       (scan-identifier ls))

      ;; Operator / delimiter
      (t
       (scan-operator ls)))))

;;;; ─── Full source tokenizer ─────────────────────────────────────────────────

(defun tokenize (source)
  "Tokenize Python 3.12 SOURCE string.
   Returns a list of TOKEN structs in source order.
   Token types: :NAME :KEYWORD :NUMBER :STRING :NEWLINE :INDENT :DEDENT :ENDMARKER :OP
   Note: hard keywords are emitted as :KEYWORD; soft keywords (match/case/type/_)
         are emitted as :NAME (context-sensitivity is for the parser)."
  (let ((ls (make-lexer-state :source source)))
    ;; Split source into physical lines for indentation processing.
    ;; We drive per-line: measure indent, possibly emit INDENT/DEDENT,
    ;; then call scan-logical-line for the rest.
    (loop until (ls-at-end-p ls) do
      (let* ((line-start-pos  (lexer-state-pos ls))
             (line-num        (lexer-state-line ls))
             ;; Measure leading whitespace for indentation
             (indent-str      (with-output-to-string (buf)
                                (loop while (member (ls-char ls) '(#\Space #\Tab))
                                      do (write-char (ls-advance ls) buf))))
             (indent-level    (compute-indent indent-str)))
        (declare (ignore line-start-pos))

        (cond
          ;; Blank / comment-only / null-byte-only line: skip without INDENT/DEDENT/NEWLINE
          ((or (ls-at-end-p ls)
               (eql (ls-char ls) #\Newline)
               (eql (ls-char ls) #\Return)
               (eql (ls-char ls) #\#)
               (eql (ls-char ls) #\Nul))
           ;; Just consume the rest of the line
           (scan-logical-line ls))

          ;; Inside brackets — ignore indentation entirely
          ((> (lexer-state-paren-depth ls) 0)
           (scan-logical-line ls))

          ;; Normal line — process indentation
          (t
           (process-indent ls indent-level line-num 0)
           (scan-logical-line ls)))))

    ;; Emit any remaining DEDENTs back to column 0
    (loop while (> (car (lexer-state-indent-stack ls)) 0) do
      (pop (lexer-state-indent-stack ls))
      (ls-emit ls :dedent "" (lexer-state-line ls) (lexer-state-column ls)))

    ;; Final NEWLINE if source didn't end with one
    ;; (ENDMARKER comes after it, so we leave it to the parser)

    ;; ENDMARKER
    (ls-emit ls :endmarker "" (lexer-state-line ls) (lexer-state-column ls))

    ;; Return tokens in source order (we accumulated in reverse)
    (nreverse (lexer-state-tokens ls))))
