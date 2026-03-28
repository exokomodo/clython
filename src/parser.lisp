;;;; parser.lisp — PEG parser for Python 3.12
;;;;
;;;; A packrat PEG parser that consumes token structs from clython.lexer
;;;; and produces AST nodes from clython.ast.
;;;;
;;;; Design:
;;;;   - Parser state is a struct holding the token vector, current position,
;;;;     and a packrat memo table keyed by (rule-name . position).
;;;;   - Core PEG combinators operate on this state and return
;;;;     (values result new-pos) on success, or (values nil nil) on failure.
;;;;   - Named rules are memoized automatically via DEFRULE macro.
;;;;   - Expression rules follow Python 3.12 operator precedence.

(defpackage :clython.parser
  (:use :cl)
  (:export #:parse-module
           #:parse-expression
           #:parser-error
           #:parser-error-message
           #:parser-error-line
           #:parser-error-column))

(in-package :clython.parser)

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Section 1: Parser State & Conditions
;;;; ═══════════════════════════════════════════════════════════════════════════

(define-condition parser-error (error)
  ((message :initarg :message :reader parser-error-message :initform "Parse error")
   (line    :initarg :line    :reader parser-error-line    :initform 0)
   (column  :initarg :column  :reader parser-error-column  :initform 0))
  (:report (lambda (c stream)
             (format stream "ParseError at line ~A col ~A: ~A"
                     (parser-error-line c)
                     (parser-error-column c)
                     (parser-error-message c)))))

(defstruct pstate
  "Parser state: token vector, position, and memo table."
  (tokens  #() :type simple-vector)    ; vector of token structs
  (pos     0   :type fixnum)           ; current index into tokens
  (memo    nil))                       ; hash-table for packrat memoization

(defun make-parser-state (token-list)
  "Create a fresh parser state from a list of tokens."
  (make-pstate :tokens (coerce token-list 'simple-vector)
               :pos 0
               :memo (make-hash-table :test #'equal)))

(defun ps-token (ps &optional (offset 0))
  "Return the token at pos+offset, or NIL if past end."
  (let ((i (+ (pstate-pos ps) offset)))
    (if (< i (length (pstate-tokens ps)))
        (aref (pstate-tokens ps) i)
        nil)))

(defun ps-at-end-p (ps)
  (>= (pstate-pos ps) (length (pstate-tokens ps))))

(defun ps-save (ps)
  "Save current position for backtracking."
  (pstate-pos ps))

(defun ps-restore (ps saved)
  "Restore position for backtracking."
  (setf (pstate-pos ps) saved))

(defun ps-advance (ps)
  "Consume one token and return it."
  (let ((tok (ps-token ps)))
    (when tok (incf (pstate-pos ps)))
    tok))

(defun current-line (ps)
  "Line number of current token, or 0."
  (let ((tok (ps-token ps)))
    (if tok (clython.lexer:token-line tok) 0)))

(defun current-col (ps)
  "Column of current token, or 0."
  (let ((tok (ps-token ps)))
    (if tok (clython.lexer:token-column tok) 0)))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Section 2: PEG Combinator Core
;;;; ═══════════════════════════════════════════════════════════════════════════
;;;;
;;;; Convention: A "parser function" is (lambda (ps) ...) that returns
;;;; the parsed value on success (advancing ps), or the symbol :FAIL
;;;; on failure (ps position restored).

(defconstant +fail+ :fail)

(defun failp (result)
  (eq result +fail+))

;;; --- Token matchers ---

(defun match-type (type)
  "Return a parser that matches a token of the given TYPE."
  (lambda (ps)
    (let ((tok (ps-token ps)))
      (if (and tok (eq (clython.lexer:token-type tok) type))
          (progn (ps-advance ps) tok)
          +fail+))))

(defun match-type-value (type value)
  "Return a parser that matches a token of TYPE with VALUE."
  (lambda (ps)
    (let ((tok (ps-token ps)))
      (if (and tok
               (eq (clython.lexer:token-type tok) type)
               (string= (clython.lexer:token-value tok) value))
          (progn (ps-advance ps) tok)
          +fail+))))

(defun match-op (value)
  "Match an :OP token with the given value string."
  (match-type-value :op value))

(defun match-keyword (value)
  "Match a :KEYWORD token with the given value string."
  (match-type-value :keyword value))

(defun match-name ()
  "Match any :NAME token."
  (match-type :name))

(defun match-name-value (value)
  "Match a :NAME token with specific value (for soft keywords)."
  (match-type-value :name value))

;;; --- Core combinators ---

(defun peg-seq (&rest parsers)
  "Sequence: run all PARSERS in order. Returns list of results.
   Fails (backtracking) if any parser fails."
  (lambda (ps)
    (let ((saved (ps-save ps))
          (results '()))
      (dolist (p parsers (nreverse results))
        (let ((r (funcall p ps)))
          (when (failp r)
            (ps-restore ps saved)
            (return +fail+))
          (push r results))))))

(defun peg-or (&rest parsers)
  "Ordered choice: try each parser in order, return first success."
  (lambda (ps)
    (dolist (p parsers +fail+)
      (let ((r (funcall p ps)))
        (unless (failp r)
          (return r))))))

(defun peg-many (parser)
  "Zero or more: greedily apply PARSER, return list of results."
  (lambda (ps)
    (let ((results '()))
      (loop
        (let ((r (funcall parser ps)))
          (when (failp r)
            (return (nreverse results)))
          (push r results))))))

(defun peg-many1 (parser)
  "One or more: like peg-many but must match at least once."
  (lambda (ps)
    (block peg-many1-body
      (let ((first (funcall parser ps)))
        (when (failp first)
          (return-from peg-many1-body +fail+))
        (let ((results (list first)))
          (loop
            (let ((r (funcall parser ps)))
              (when (failp r) (return-from peg-many1-body (nreverse results)))
              (push r results))))))))

(defun peg-opt (parser)
  "Optional: try PARSER, return result or NIL (never fails)."
  (lambda (ps)
    (let ((r (funcall parser ps)))
      (if (failp r) nil r))))

(defun peg-lookahead (parser)
  "Positive lookahead: succeed if PARSER matches but don't consume."
  (lambda (ps)
    (let ((saved (ps-save ps)))
      (let ((r (funcall parser ps)))
        (ps-restore ps saved)
        (if (failp r) +fail+ t)))))

(defun peg-not (parser)
  "Negative lookahead: succeed (returning T) if PARSER fails."
  (lambda (ps)
    (let ((saved (ps-save ps)))
      (let ((r (funcall parser ps)))
        (ps-restore ps saved)
        (if (failp r) t +fail+)))))

(defun peg-action (parser action)
  "Transform: apply PARSER, then call ACTION on the result."
  (lambda (ps)
    (let ((r (funcall parser ps)))
      (if (failp r)
          +fail+
          (funcall action r)))))

;;; --- Packrat memoization via DEFRULE ---

(defmacro defrule (name &body body)
  "Define a memoized parsing rule. BODY receives PS and should return
   the parse result or +fail+. Results are cached by (name . position).
   BODY is wrapped in (block nil ...) so (return-from nil ...) works."
  (let ((ps-var (gensym "PS")))
    `(defun ,name (,ps-var)
       (let* ((memo-key (cons ',name (pstate-pos ,ps-var)))
              (cached (gethash memo-key (pstate-memo ,ps-var) :no-entry)))
         (if (not (eq cached :no-entry))
             ;; Cache hit: restore position and return
             (progn
               (setf (pstate-pos ,ps-var) (car cached))
               (cdr cached))
             ;; Cache miss: run rule and store result
             (let* ((start-pos (pstate-pos ,ps-var))
                    (result (block nil
                              (let ((ps ,ps-var))
                                (declare (ignorable ps))
                                ,@body)))
                    (end-pos (pstate-pos ,ps-var)))
               ;; On failure, restore position
               (when (failp result)
                 (setf (pstate-pos ,ps-var) start-pos)
                 (setf end-pos start-pos))
               (setf (gethash memo-key (pstate-memo ,ps-var))
                     (cons end-pos result))
               result))))))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Section 3: Utility helpers
;;;; ═══════════════════════════════════════════════════════════════════════════

(defun tok-line (tok)
  (if tok (clython.lexer:token-line tok) 0))

(defun tok-col (tok)
  (if tok (clython.lexer:token-column tok) 0))

(defun tok-value (tok)
  (if tok (clython.lexer:token-value tok) ""))

(defun tok-type (tok)
  (if tok (clython.lexer:token-type tok) nil))

(defun make-node (class &rest initargs)
  "Convenience: create an AST node."
  (apply #'make-instance class initargs))

(defun skip-newlines (ps)
  "Skip any :NEWLINE tokens at the current position."
  (loop while (let ((tok (ps-token ps)))
                (and tok (eq (tok-type tok) :newline)))
        do (ps-advance ps)))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Section 4: Expression Rules
;;;; ═══════════════════════════════════════════════════════════════════════════

;;; --- Atoms ---

(defrule parse-name-expr
  ;; NAME -> name-node
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :name))
        (progn
          (ps-advance ps)
          (make-node 'clython.ast:name-node
                     :id (tok-value tok)
                     :ctx :load
                     :line (tok-line tok)
                     :col (tok-col tok)))
        +fail+)))

(defrule parse-number
  ;; NUMBER -> constant-node
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :number))
        (progn
          (ps-advance ps)
          (let* ((text (tok-value tok))
                 (value (parse-number-value text)))
            (make-node 'clython.ast:constant-node
                       :value value
                       :line (tok-line tok)
                       :col (tok-col tok))))
        +fail+)))

(defun parse-number-value (text)
  "Convert a Python numeric literal string to a Lisp number."
  (let ((lower (string-downcase text))
        (clean ""))
    ;; Remove underscores
    (setf clean (remove #\_ lower))
    (cond
      ;; Complex
      ((and (> (length clean) 0)
            (char= (char clean (1- (length clean))) #\j))
       (let* ((*read-default-float-format* 'double-float)
              (base (subseq clean 0 (1- (length clean)))))
         (if (string= base "")
             (complex 0 1.0d0)
             (complex 0 (read-from-string base)))))
      ;; Hex
      ((and (>= (length clean) 2) (string= (subseq clean 0 2) "0x"))
       (parse-integer (subseq clean 2) :radix 16))
      ;; Octal
      ((and (>= (length clean) 2) (string= (subseq clean 0 2) "0o"))
       (parse-integer (subseq clean 2) :radix 8))
      ;; Binary
      ((and (>= (length clean) 2) (string= (subseq clean 0 2) "0b"))
       (parse-integer (subseq clean 2) :radix 2))
      ;; Float (contains . or e)
      ((or (find #\. clean) (find #\e clean))
       (let ((*read-default-float-format* 'double-float))
         (read-from-string clean)))
      ;; Integer
      (t
       (parse-integer clean)))))

(defrule parse-string-literal
  ;; STRING or FSTRING -> constant-node or joined-str-node
  (let ((tok (ps-token ps)))
    (cond
      ((and tok (eq (tok-type tok) :string))
       (ps-advance ps)
       (make-node 'clython.ast:constant-node
                  :value (tok-value tok)
                  :line (tok-line tok)
                  :col (tok-col tok)))
      ((and tok (eq (tok-type tok) :fstring))
       (ps-advance ps)
       (%parse-fstring-value (tok-value tok) (tok-line tok) (tok-col tok)))
      (t +fail+))))

;; Concatenated strings: multiple adjacent STRING tokens
;; Each part keeps its raw token value; concatenation happens at eval time
;; by unquoting each part individually. For single strings, the raw value
;; is kept as-is. For adjacent strings, we store a special marker list.
(defun %parse-fstring-value (raw-value line col)
  "Parse an f-string token value into a joined-str-node.
   RAW-VALUE is like f'text {expr} more' — includes the prefix and quotes."
  (let* ((stripped (%unquote-fstring-raw raw-value))
         (parts (%split-fstring stripped line col)))
    (if (= (length parts) 1)
        (first parts)
        (make-instance 'clython.ast:joined-str-node
                       :values parts
                       :line line :col col))))

(defun %unquote-fstring-raw (raw)
  "Strip the f-string prefix and quotes from the raw token value.
   e.g. f'hello {x}' → hello {x}"
  (let* ((s raw)
         ;; Skip prefix characters (f, r, b, etc.)
         (start 0))
    (loop while (and (< start (length s))
                     (member (char-downcase (char s start)) '(#\f #\r #\b #\u)))
          do (incf start))
    (setf s (subseq s start))
    ;; Strip quotes
    (cond
      ((and (>= (length s) 6)
            (string= (subseq s 0 3) "\"\"\"")
            (string= (subseq s (- (length s) 3)) "\"\"\""))
       (subseq s 3 (- (length s) 3)))
      ((and (>= (length s) 6)
            (string= (subseq s 0 3) "'''")
            (string= (subseq s (- (length s) 3)) "'''"))
       (subseq s 3 (- (length s) 3)))
      ((and (>= (length s) 2)
            (or (char= (char s 0) #\') (char= (char s 0) #\"))
            (char= (char s 0) (char s (1- (length s)))))
       (subseq s 1 (1- (length s))))
      (t s))))

(defun %split-fstring (body line col)
  "Split an f-string body into a list of constant-node and formatted-value-node parts.
   Handles { and } delimiters, {{ and }} escapes."
  (let ((parts '())
        (text (make-string-output-stream))
        (i 0)
        (len (length body)))
    (flet ((flush-text ()
             (let ((s (get-output-stream-string text)))
               (when (plusp (length s))
                 (push (make-instance 'clython.ast:constant-node
                                      :value (format nil "'~A'" s)
                                      :line line :col col)
                       parts)))))
      (loop while (< i len) do
        (let ((ch (char body i)))
          (cond
            ;; Escaped {{ → literal {
            ((and (char= ch #\{) (< (1+ i) len) (char= (char body (1+ i)) #\{))
             (write-char #\{ text)
             (incf i 2))
            ;; Escaped }} → literal }
            ((and (char= ch #\}) (< (1+ i) len) (char= (char body (1+ i)) #\}))
             (write-char #\} text)
             (incf i 2))
            ;; Start of expression
            ((char= ch #\{)
             (flush-text)
             ;; Find the matching }
             (let ((depth 1)
                   (start (1+ i))
                   (j (1+ i)))
               (loop while (and (< j len) (plusp depth)) do
                 (case (char body j)
                   (#\{ (incf depth))
                   (#\} (decf depth)))
                 (when (plusp depth) (incf j)))
               ;; body[start..j-1] is the expression (j points past closing })
               (let* ((expr-src (subseq body start (max start j)))
                      (expr-node (%parse-fstring-expr expr-src line col)))
                 (push expr-node parts))
               (setf i (1+ j))))
            ;; Normal character
            (t
             (write-char ch text)
             (incf i)))))
      (flush-text))
    (nreverse parts)))

(defun %parse-fstring-expr (source line col)
  "Parse an f-string expression source into a formatted-value-node."
  (handler-case
      (let* ((tokens (clython.lexer:tokenize source))
             (ps (make-parser-state tokens))
             (expr (parse-expression-internal ps)))
        (if (failp expr)
            ;; Fallback: treat as literal
            (make-instance 'clython.ast:constant-node
                           :value (format nil "'~A'" source)
                           :line line :col col)
            (make-instance 'clython.ast:formatted-value-node
                           :value expr
                           :line line :col col)))
    (error ()
      (make-instance 'clython.ast:constant-node
                     :value (format nil "'~A'" source)
                     :line line :col col))))

(defrule parse-strings
  (let ((first (parse-string-literal ps)))
    (if (failp first)
        +fail+
        ;; Check for more adjacent strings
        (let ((rest-parts nil))
          (loop
            (let ((next (parse-string-literal ps)))
              (when (failp next) (return))
              (push (clython.ast:constant-node-value next) rest-parts)))
          (if (null rest-parts)
              first
              ;; Store all parts as a list so eval can unquote each individually
              (make-node 'clython.ast:constant-node
                         :value (cons :concat-strings
                                      (cons (clython.ast:constant-node-value first)
                                            (nreverse rest-parts)))
                         :line (clython.ast:node-line first)
                         :col (clython.ast:node-col first)))))))

(defrule parse-keyword-constant
  ;; True, False, None, ... (Ellipsis)
  (let ((tok (ps-token ps)))
    (cond
      ((and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "True"))
       (ps-advance ps)
       (make-node 'clython.ast:constant-node :value t
                  :line (tok-line tok) :col (tok-col tok)))
      ((and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "False"))
       (ps-advance ps)
       (make-node 'clython.ast:constant-node :value nil
                  :line (tok-line tok) :col (tok-col tok)))
      ((and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "None"))
       (ps-advance ps)
       (make-node 'clython.ast:constant-node :value :none
                  :line (tok-line tok) :col (tok-col tok)))
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "..."))
       (ps-advance ps)
       (make-node 'clython.ast:constant-node :value :ellipsis
                  :line (tok-line tok) :col (tok-col tok)))
      (t +fail+))))

(defrule parse-paren-expr
  ;;; Parses parenthesized expressions: (), (expr), (expr, ...), (genexpr)
  (let* ((saved (ps-save ps))
         (tok (ps-token ps))
         (line (tok-line tok))
         (col (tok-col tok)))
    (unless (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "("))
      (return-from nil +fail+))

    ;; Consume initial opening parenthesis
    (ps-advance ps)

    ;; Check for empty tuple ()
    (when (let ((c (ps-token ps)))
            (and c (eq (tok-type c) :op) (string= (tok-value c) ")")))
      (ps-advance ps)
      (return-from nil
        (make-node 'clython.ast:tuple-node :elts nil :ctx :load :line line :col col)))

    ;; Attempt to parse first expression inside parentheses
    (let ((first-expr (parse-star-expr-or-expr ps)))
      (when (failp first-expr)
        (ps-restore ps saved)
        (return-from nil +fail+))

      ;; Check for generator expression syntax (expr comp_for)
      (let ((comp-result (parse-comp-for ps)))
        (unless (failp comp-result)
          (let ((c (ps-token ps)))
            (if (and c (eq (tok-type c) :op) (string= (tok-value c) ")"))
                (progn
                  (ps-advance ps)
                  (return-from nil
                    (make-node 'clython.ast:generator-exp-node
                               :elt first-expr
                               :generators comp-result
                               :line line :col col)))
              (progn (ps-restore ps saved) (return-from nil +fail+))))))

      ;; Handle parenthesized single expr or tuple
      (let ((next (ps-token ps)))
        (cond
          ;; Case: single expression with closing )
          ((and next (eq (tok-type next) :op) (string= (tok-value next) ")"))
           (ps-advance ps)
           first-expr)
          ;; Case: tuple -> consume additional elements
          ((and next (eq (tok-type next) :op) (string= (tok-value next) ","))
           (return-from nil (parse-tuple-from ps saved first-expr line col)))
          ;; Case: invalid parenthesized expression
          (t
           (ps-restore ps saved)
           +fail+))))))

(defun parse-tuple-from (ps saved first-expr line col)
  "Continue parsing tuple elements starting with first-expr."
  (let ((elts (list first-expr)))
    (loop
      (let ((tok (ps-token ps)))
        (cond
          ;; Closing ) for tuple
          ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) ")"))
           (ps-advance ps)
           (return
             (make-node 'clython.ast:tuple-node
                        :elts (nreverse elts) :ctx :load
                        :line line :col col)))
          ;; Comma separating elements
          ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) ","))
           (ps-advance ps)
           ;; Parse and push next element
           (let ((elt (parse-star-expr-or-expr ps)))
             (if (failp elt)
                 (progn (ps-restore ps saved) (return +fail+))
                 (push elt elts))))
          (t
           ;; Neither comma nor closing, invalid tuple syntax
           (ps-restore ps saved)
           (return +fail+)))))))

(defrule parse-list-expr
  ;; [ ] | [ expr, ... ] | [ expr comp_for ]
  (let ((saved (ps-save ps))
        (tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "["))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((line (tok-line tok))
          (col (tok-col tok)))
      ;; Empty list
      (let ((close (ps-token ps)))
        (when (and close (eq (tok-type close) :op) (string= (tok-value close) "]"))
          (ps-advance ps)
          (return-from nil
            (make-node 'clython.ast:list-node :elts nil :ctx :load
                       :line line :col col))))
      ;; First element
      (let ((first-expr (parse-star-expr-or-expr ps)))
        (when (failp first-expr)
          (ps-restore ps saved)
          (return-from nil +fail+))
        ;; List comprehension?
        (let ((comp-result (parse-comp-for ps)))
          (unless (failp comp-result)
            (let ((close-tok (ps-token ps)))
              (if (and close-tok (eq (tok-type close-tok) :op) (string= (tok-value close-tok) "]"))
                  (progn
                    (ps-advance ps)
                    (return-from nil
                      (make-node 'clython.ast:list-comp-node
                                 :elt first-expr
                                 :generators comp-result
                                 :line line :col col)))
                  (progn (ps-restore ps saved) (return-from nil +fail+))))))
        ;; Regular list
        (let ((elts (list first-expr)))
          (loop
            (let ((comma (ps-token ps)))
              (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
                (return))
              (ps-advance ps))
            ;; Trailing comma before ]
            (let ((close-check (ps-token ps)))
              (when (and close-check (eq (tok-type close-check) :op)
                         (string= (tok-value close-check) "]"))
                (return)))
            (let ((elt (parse-star-expr-or-expr ps)))
              (when (failp elt) (return))
              (push elt elts)))
          (let ((close-tok (ps-token ps)))
            (if (and close-tok (eq (tok-type close-tok) :op) (string= (tok-value close-tok) "]"))
                (progn
                  (ps-advance ps)
                  (make-node 'clython.ast:list-node
                             :elts (nreverse elts) :ctx :load
                             :line line :col col))
                (progn (ps-restore ps saved) +fail+))))))))

(defun expect-close-brace (ps)
  (let ((tok (ps-token ps)))
    (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "}"))))

(defrule parse-dict-or-set
  ;; { } | { k:v, ... } | { expr, ... } | comprehensions
  (let* ((saved (ps-save ps))
         (tok (ps-token ps))
         (line (tok-line tok))
         (col (tok-col tok)))
    (unless (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "{"))
      (return-from nil +fail+))
    (ps-advance ps)
    ;; Empty dict
    (when (expect-close-brace ps)
      (ps-advance ps)
      (return-from nil
        (make-node 'clython.ast:dict-node :keys nil :values nil
                   :line line :col col)))
    ;; First expression
    (let ((first-expr (parse-expression-internal ps)))
      (when (failp first-expr)
        (ps-restore ps saved)
        (return-from nil +fail+))
      (let ((next (ps-token ps)))
        (cond
          ;; Dict: first-expr : value ...
          ((and next (eq (tok-type next) :op) (string= (tok-value next) ":"))
           (ps-advance ps)
           (parse-dict-after-first-colon ps saved first-expr line col))
          ;; Set comprehension: first-expr comp_for }
          ((let ((s2 (ps-save ps)))
             (let ((cr (parse-comp-for ps)))
               (if (failp cr)
                   (progn (ps-restore ps s2) nil)
                   (if (expect-close-brace ps)
                       (progn (ps-advance ps)
                              (return-from nil
                                (make-node 'clython.ast:set-comp-node
                                           :elt first-expr :generators cr
                                           :line line :col col)))
                       (progn (ps-restore ps s2) nil)))))
           ;; Already returned above if successful
           (ps-restore ps saved) +fail+)
          ;; Set literal: { expr, ... }
          (t
           (parse-set-after-first ps saved first-expr line col)))))))

(defun parse-dict-after-first-colon (ps saved first-key line col)
  "Parse rest of dict after we've seen { first-key : (pos is after colon)."
  (let ((first-val (parse-expression-internal ps)))
    (when (failp first-val)
      (ps-restore ps saved)
      (return-from parse-dict-after-first-colon +fail+))
    ;; Dict comprehension?
    (let ((comp-result (parse-comp-for ps)))
      (unless (failp comp-result)
        (if (expect-close-brace ps)
            (progn
              (ps-advance ps)
              (return-from parse-dict-after-first-colon
                (make-node 'clython.ast:dict-comp-node
                           :key first-key :value first-val
                           :generators comp-result
                           :line line :col col)))
            (progn (ps-restore ps saved)
                   (return-from parse-dict-after-first-colon +fail+)))))
    ;; Regular dict - parse remaining key:value pairs
    (let ((keys (list first-key))
          (vals (list first-val)))
      (loop
        (let ((comma (ps-token ps)))
          (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
            (return))
          (ps-advance ps))
        (when (expect-close-brace ps) (return))
        ;; ** unpacking
        (let ((star (ps-token ps)))
          (if (and star (eq (tok-type star) :op) (string= (tok-value star) "**"))
              (progn
                (ps-advance ps)
                (let ((expr (parse-expression-internal ps)))
                  (when (failp expr) (return))
                  (push nil keys)
                  (push expr vals)))
              (progn
                (let ((k (parse-expression-internal ps)))
                  (when (failp k) (return))
                  (let ((colon (ps-token ps)))
                    (unless (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
                      (return))
                    (ps-advance ps))
                  (let ((v (parse-expression-internal ps)))
                    (when (failp v) (return))
                    (push k keys)
                    (push v vals)))))))
      (if (expect-close-brace ps)
          (progn
            (ps-advance ps)
            (make-node 'clython.ast:dict-node
                       :keys (nreverse keys) :values (nreverse vals)
                       :line line :col col))
          (progn (ps-restore ps saved) +fail+)))))

(defun parse-set-after-first (ps saved first-expr line col)
  "Parse rest of set literal after first element."
  (let ((elts (list first-expr)))
    (loop
      (let ((comma (ps-token ps)))
        (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
          (return))
        (ps-advance ps))
      (when (expect-close-brace ps) (return))
      (let ((elt (parse-expression-internal ps)))
        (when (failp elt) (return))
        (push elt elts)))
    (if (expect-close-brace ps)
        (progn
          (ps-advance ps)
          (make-node 'clython.ast:set-node
                     :elts (nreverse elts)
                     :line line :col col))
        (progn (ps-restore ps saved) +fail+))))

;;; --- Comprehension helpers ---

(defrule parse-comp-for
  ;; comp_for: [async] 'for' target 'in' or_expr comp_iter*
  (let ((saved (ps-save ps))
        (generators '()))
    (loop
      (let ((is-async nil)
            (tok (ps-token ps)))
        ;; Optional async
        (when (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "async"))
          (setf is-async t)
          (ps-advance ps)
          (setf tok (ps-token ps)))
        ;; Must have 'for'
        (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "for"))
          (if generators
              (return (nreverse generators))
              (progn (ps-restore ps saved) (return +fail+))))
        (ps-advance ps) ; consume 'for'
        ;; target
        (let ((target (parse-target-list ps)))
          (when (failp target)
            (if generators
                (return (nreverse generators))
                (progn (ps-restore ps saved) (return +fail+))))
          ;; 'in'
          (let ((in-tok (ps-token ps)))
            (unless (and in-tok (eq (tok-type in-tok) :keyword) (string= (tok-value in-tok) "in"))
              (ps-restore ps saved)
              (return +fail+))
            (ps-advance ps))
          ;; iter expression (use or-test to avoid confusion with commas)
          (let ((iter (parse-or-test ps)))
            (when (failp iter)
              (ps-restore ps saved)
              (return +fail+))
            ;; Optional 'if' clauses
            (let ((ifs '()))
              (loop
                (let ((if-tok (ps-token ps)))
                  (unless (and if-tok (eq (tok-type if-tok) :keyword) (string= (tok-value if-tok) "if"))
                    (return))
                  (ps-advance ps)
                  (let ((test (parse-or-test ps)))
                    (when (failp test) (return))
                    (push test ifs))))
              (push (make-instance 'clython.ast:py-comprehension
                                   :target target
                                   :iter iter
                                   :ifs (nreverse ifs)
                                   :is-async is-async)
                    generators))))))))

(defrule parse-target-list
  ;; Simple target for comprehensions - a name or tuple of names
  (let ((first (parse-star-target-atom ps)))
    (when (failp first) (return-from nil +fail+))
    ;; Check for comma (tuple target)
    (let ((next (ps-token ps)))
      (if (and next (eq (tok-type next) :op) (string= (tok-value next) ","))
          (let ((elts (list first)))
            (loop
              (let ((comma (ps-token ps)))
                (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
                  (return))
                (ps-advance ps))
              (let ((elt (parse-star-target-atom ps)))
                (when (failp elt) (return))
                (push elt elts)))
            (make-node 'clython.ast:tuple-node
                       :elts (nreverse elts) :ctx :store
                       :line (clython.ast:node-line first)
                       :col (clython.ast:node-col first)))
          first))))

(defrule parse-star-target-atom
  ;; A single target: name, *, attribute, subscript
  (let ((tok (ps-token ps)))
    (cond
      ;; *name
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "*"))
       (ps-advance ps)
       (let ((target (parse-atom ps)))
         (if (failp target) +fail+
             (make-node 'clython.ast:starred-node :value target :ctx :store
                        :line (tok-line tok) :col (tok-col tok)))))
      ;; name
      ((and tok (eq (tok-type tok) :name))
       (ps-advance ps)
       (make-node 'clython.ast:name-node :id (tok-value tok) :ctx :store
                  :line (tok-line tok) :col (tok-col tok)))
      ;; ( target-list )
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "("))
       (ps-advance ps)
       (let ((target (parse-target-list ps)))
         (when (failp target) (return-from nil +fail+))
         (let ((close (ps-token ps)))
           (if (and close (eq (tok-type close) :op) (string= (tok-value close) ")"))
               (progn (ps-advance ps) target)
               +fail+))))
      ;; [ target-list ]
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "["))
       (ps-advance ps)
       (let ((target (parse-target-list ps)))
         (when (failp target) (return-from nil +fail+))
         (let ((close (ps-token ps)))
           (if (and close (eq (tok-type close) :op) (string= (tok-value close) "]"))
               (progn (ps-advance ps) target)
               +fail+))))
      (t +fail+))))

;;; --- Atom ---

(defrule parse-atom
  (funcall (peg-or
            #'parse-keyword-constant
            #'parse-strings
            #'parse-number
            #'parse-name-expr
            #'parse-paren-expr
            #'parse-list-expr
            #'parse-dict-or-set)
           ps))

;;; --- Primary: atom + trailers (call, subscript, attribute) ---

(defrule parse-primary
  (let ((atom (parse-atom ps)))
    (when (failp atom) (return-from nil +fail+))
    ;; Apply trailers
    (let ((result atom))
      (loop
        (let ((tok (ps-token ps)))
          (cond
            ;; Function call: (
            ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "("))
             (ps-advance ps)
             (multiple-value-bind (args keywords)
                 (parse-arglist ps)
               (let ((close (ps-token ps)))
                 (unless (and close (eq (tok-type close) :op) (string= (tok-value close) ")"))
                   (return +fail+))
                 (ps-advance ps)
                 (setf result
                       (make-node 'clython.ast:call-node
                                  :func result
                                  :args args
                                  :keywords keywords
                                  :line (clython.ast:node-line result)
                                  :col (clython.ast:node-col result))))))
            ;; Subscript: [
            ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "["))
             (ps-advance ps)
             (let ((slice (parse-slice-list ps)))
               (when (failp slice) (return +fail+))
               (let ((close (ps-token ps)))
                 (unless (and close (eq (tok-type close) :op) (string= (tok-value close) "]"))
                   (return +fail+))
                 (ps-advance ps)
                 (setf result
                       (make-node 'clython.ast:subscript-node
                                  :value result :slice slice :ctx :load
                                  :line (clython.ast:node-line result)
                                  :col (clython.ast:node-col result))))))
            ;; Attribute: .name
            ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "."))
             (ps-advance ps)
             (let ((name-tok (ps-token ps)))
               (unless (and name-tok (eq (tok-type name-tok) :name))
                 (return +fail+))
               (ps-advance ps)
               (setf result
                     (make-node 'clython.ast:attribute-node
                                :value result
                                :attr (tok-value name-tok)
                                :ctx :load
                                :line (clython.ast:node-line result)
                                :col (clython.ast:node-col result)))))
            ;; No more trailers
            (t (return result))))))))

;;; --- Argument list parsing ---

(defun parse-arglist (ps)
  "Parse call arguments. Returns (values args-list keywords-list)."
  (let ((args '())
        (keywords '()))
    ;; Empty arglist
    (let ((tok (ps-token ps)))
      (when (and tok (eq (tok-type tok) :op) (string= (tok-value tok) ")"))
        (return-from parse-arglist (values nil nil))))
    ;; Parse arguments
    (block argloop
      (tagbody
       :next-arg
        (let ((tok (ps-token ps)))
          ;; **kwargs
          (when (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "**"))
            (ps-advance ps)
            (let ((expr (parse-expression-internal ps)))
              (unless (failp expr)
                (push (make-instance 'clython.ast:py-keyword :arg nil :value expr) keywords)))
            (let ((comma (ps-token ps)))
              (if (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
                  (progn (ps-advance ps) (go :next-arg))
                  (return-from argloop))))
          ;; *args
          (when (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "*"))
            (ps-advance ps)
            (let ((expr (parse-expression-internal ps)))
              (unless (failp expr)
                (push (make-node 'clython.ast:starred-node :value expr :ctx :load
                                 :line (clython.ast:node-line expr)
                                 :col (clython.ast:node-col expr))
                      args)))
            (let ((comma (ps-token ps)))
              (if (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
                  (progn (ps-advance ps) (go :next-arg))
                  (return-from argloop)))))
        ;; Regular arg or keyword arg
        (let* ((saved (ps-save ps))
               (expr (parse-expression-internal ps)))
          (when (failp expr)
            (return-from argloop))
          ;; Check for = (keyword argument)
          (let ((eq-tok (ps-token ps)))
            (if (and eq-tok (eq (tok-type eq-tok) :op) (string= (tok-value eq-tok) "=")
                     (typep expr 'clython.ast:name-node))
                (progn
                  (ps-advance ps) ; consume =
                  (let ((val (parse-expression-internal ps)))
                    (if (failp val)
                        (progn
                          (ps-restore ps saved)
                          (return-from argloop))
                        (push (make-instance 'clython.ast:py-keyword
                                             :arg (clython.ast:name-node-id expr)
                                             :value val)
                              keywords))))
                ;; Comprehension in call: f(x for x in y)
                (let ((comp-result (parse-comp-for ps)))
                  (if (failp comp-result)
                      (push expr args)
                      (push (make-node 'clython.ast:generator-exp-node
                                       :elt expr :generators comp-result
                                       :line (clython.ast:node-line expr)
                                       :col (clython.ast:node-col expr))
                            args))))))
        ;; Comma or end
        (let ((comma (ps-token ps)))
          (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
            (return-from argloop))
          (ps-advance ps))
        ;; Check if next is close paren (trailing comma)
        (let ((close-check (ps-token ps)))
          (when (and close-check (eq (tok-type close-check) :op) (string= (tok-value close-check) ")"))
            (return-from argloop)))
        (go :next-arg)))
    (values (nreverse args) (nreverse keywords))))

;;; --- Slice parsing ---

(defrule parse-slice-list
  ;; Simple index or slice
  (let ((result (parse-slice ps)))
    (when (failp result) (return-from nil +fail+))
    ;; Check for comma -> tuple of slices
    (let ((comma (ps-token ps)))
      (if (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
          (let ((elts (list result)))
            (loop
              (let ((c (ps-token ps)))
                (unless (and c (eq (tok-type c) :op) (string= (tok-value c) ","))
                  (return))
                (ps-advance ps))
              (let ((close-check (ps-token ps)))
                (when (and close-check (eq (tok-type close-check) :op)
                           (string= (tok-value close-check) "]"))
                  (return)))
              (let ((s (parse-slice ps)))
                (when (failp s) (return))
                (push s elts)))
            (make-node 'clython.ast:tuple-node
                       :elts (nreverse elts) :ctx :load
                       :line (clython.ast:node-line result)
                       :col (clython.ast:node-col result)))
          result))))

(defrule parse-slice
  ;; expr? : expr? [: expr?] | expr
  (let ((saved (ps-save ps))
        (line (current-line ps))
        (col (current-col ps)))
    ;; Try to detect if this is a slice (has a colon at the right level)
    (let ((lower nil)
          (upper nil)
          (step nil))
      ;; Try parsing lower
      (let ((colon-check (ps-token ps)))
        (if (and colon-check (eq (tok-type colon-check) :op) (string= (tok-value colon-check) ":"))
            ;; No lower, starts with :
            (progn
              (ps-advance ps)
              ;; upper?
              (let ((next (ps-token ps)))
                (unless (or (null next)
                            (and (eq (tok-type next) :op)
                                 (or (string= (tok-value next) "]")
                                     (string= (tok-value next) ":")
                                     (string= (tok-value next) ","))))
                  (let ((u (parse-expression-internal ps)))
                    (unless (failp u) (setf upper u)))))
              ;; step?
              (let ((colon2 (ps-token ps)))
                (when (and colon2 (eq (tok-type colon2) :op) (string= (tok-value colon2) ":"))
                  (ps-advance ps)
                  (let ((next (ps-token ps)))
                    (unless (or (null next)
                                (and (eq (tok-type next) :op)
                                     (or (string= (tok-value next) "]")
                                         (string= (tok-value next) ","))))
                      (let ((s (parse-expression-internal ps)))
                        (unless (failp s) (setf step s)))))))
              (return-from nil
                (make-node 'clython.ast:slice-node
                           :lower lower :upper upper :step step
                           :line line :col col)))
            ;; Has a lower expression
            (let ((expr (parse-expression-internal ps)))
              (when (failp expr)
                (ps-restore ps saved)
                (return-from nil +fail+))
              ;; Check for colon
              (let ((colon (ps-token ps)))
                (if (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
                    (progn
                      (ps-advance ps)
                      (setf lower expr)
                      ;; upper?
                      (let ((next (ps-token ps)))
                        (unless (or (null next)
                                    (and (eq (tok-type next) :op)
                                         (or (string= (tok-value next) "]")
                                             (string= (tok-value next) ":")
                                             (string= (tok-value next) ","))))
                          (let ((u (parse-expression-internal ps)))
                            (unless (failp u) (setf upper u)))))
                      ;; step?
                      (let ((colon2 (ps-token ps)))
                        (when (and colon2 (eq (tok-type colon2) :op) (string= (tok-value colon2) ":"))
                          (ps-advance ps)
                          (let ((next (ps-token ps)))
                            (unless (or (null next)
                                        (and (eq (tok-type next) :op)
                                             (or (string= (tok-value next) "]")
                                                 (string= (tok-value next) ","))))
                              (let ((s (parse-expression-internal ps)))
                                (unless (failp s) (setf step s)))))))
                      (make-node 'clython.ast:slice-node
                                 :lower lower :upper upper :step step
                                 :line line :col col))
                    ;; Just an expression, not a slice
                    expr))))))))

;;; --- Await expression ---

(defrule parse-await-expr
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "await"))
        (progn
          (ps-advance ps)
          (let ((expr (parse-primary ps)))
            (if (failp expr) +fail+
                (make-node 'clython.ast:await-node :value expr
                           :line (tok-line tok) :col (tok-col tok)))))
        (parse-primary ps))))

;;; --- Unary: +, -, ~  ---

(defrule parse-unary
  (let ((tok (ps-token ps)))
    (cond
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "+"))
       (ps-advance ps)
       (let ((operand (parse-unary ps)))
         (if (failp operand) +fail+
             (make-node 'clython.ast:unary-op-node :op :u-add :operand operand
                        :line (tok-line tok) :col (tok-col tok)))))
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "-"))
       (ps-advance ps)
       (let ((operand (parse-unary ps)))
         (if (failp operand) +fail+
             (make-node 'clython.ast:unary-op-node :op :u-sub :operand operand
                        :line (tok-line tok) :col (tok-col tok)))))
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "~"))
       (ps-advance ps)
       (let ((operand (parse-unary ps)))
         (if (failp operand) +fail+
             (make-node 'clython.ast:unary-op-node :op :invert :operand operand
                        :line (tok-line tok) :col (tok-col tok)))))
      ;; Non-unary: fall through to power (** binds tighter than unary -)
      (t (parse-power ps)))))

;;; --- Power: base ** exp (right-associative) ---
;;; Grammar: power ::= (await_expr | primary) ["**" u_expr]
;;; Note: base is NOT a unary expr — this ensures -2**2 == -(2**2) == -4

(defrule parse-power
  (let ((base (parse-await-expr ps)))
    (when (failp base) (return-from nil +fail+))
    (let ((tok (ps-token ps)))
      (if (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "**"))
          (progn
            (ps-advance ps)
            ;; Exponent is a u_expr (unary), allowing -2**-2
            (let ((exp (parse-unary ps)))
              (if (failp exp) +fail+
                  (make-node 'clython.ast:bin-op-node
                             :left base :op :pow :right exp
                             :line (clython.ast:node-line base)
                             :col (clython.ast:node-col base)))))
          base))))

;;; --- Binary operators (left-associative, by precedence) ---

(defmacro def-left-binop (name child-rule &rest op-specs)
  "Define a left-associative binary operator rule.
   OP-SPECS are (operator-string ast-keyword) pairs."
  `(defrule ,name
     (let ((left (,child-rule ps)))
       (when (failp left) (return-from nil +fail+))
       (loop
         (let ((tok (ps-token ps)))
           (cond
             ,@(mapcar (lambda (spec)
                         (destructuring-bind (op-str ast-op) spec
                           `((and tok (eq (tok-type tok) :op) (string= (tok-value tok) ,op-str))
                             (ps-advance ps)
                             (let ((right (,child-rule ps)))
                               (when (failp right) (return left))
                               (setf left
                                     (make-node 'clython.ast:bin-op-node
                                                :left left :op ,ast-op :right right
                                                :line (clython.ast:node-line left)
                                                :col (clython.ast:node-col left)))))))
                       op-specs)
             (t (return left))))))))

;; Precedence from lowest to highest (among multiplicative/additive/shift/bitwise):
;; Note: power and unary are already defined above

;; Multiplicative: * / // % @
;; Calls parse-unary (not parse-power) — unary sits between * and **
(def-left-binop parse-mul-expr parse-unary
  ("*" :mult) ("/" :div) ("//" :floor-div) ("%" :mod) ("@" :mat-mult))

;; Additive: + -
(def-left-binop parse-add-expr parse-mul-expr
  ("+" :add) ("-" :sub))

;; Shift: << >>
(def-left-binop parse-shift-expr parse-add-expr
  ("<<" :l-shift) (">>" :r-shift))

;; Bitwise AND: &
(def-left-binop parse-bitand-expr parse-shift-expr
  ("&" :bit-and))

;; Bitwise XOR: ^
(def-left-binop parse-bitxor-expr parse-bitand-expr
  ("^" :bit-xor))

;; Bitwise OR: |
(def-left-binop parse-bitor-expr parse-bitxor-expr
  ("|" :bit-or))

;;; --- Comparison operators (chained) ---

(defrule parse-comparison
  (let ((left (parse-bitor-expr ps)))
    (when (failp left) (return-from nil +fail+))
    (let ((ops '())
          (comparators '()))
      (loop
        (let* ((tok (ps-token ps))
               (comp-op (identify-comparison-op ps tok)))
          (when (null comp-op) (return))
          ;; Consume the operator token(s)
          (consume-comparison-op ps comp-op)
          (let ((right (parse-bitor-expr ps)))
            (when (failp right) (return))
            (push comp-op ops)
            (push right comparators))))
      (if ops
          (make-node 'clython.ast:compare-node
                     :left left
                     :ops (nreverse ops)
                     :comparators (nreverse comparators)
                     :line (clython.ast:node-line left)
                     :col (clython.ast:node-col left))
          left))))

(defun identify-comparison-op (ps tok)
  "Identify if current token(s) form a comparison operator. Returns keyword or NIL."
  (when (null tok) (return-from identify-comparison-op nil))
  (cond
    ((and (eq (tok-type tok) :op) (string= (tok-value tok) "==")) :eq)
    ((and (eq (tok-type tok) :op) (string= (tok-value tok) "!=")) :not-eq)
    ((and (eq (tok-type tok) :op) (string= (tok-value tok) "<"))  :lt)
    ((and (eq (tok-type tok) :op) (string= (tok-value tok) "<=")) :lt-e)
    ((and (eq (tok-type tok) :op) (string= (tok-value tok) ">"))  :gt)
    ((and (eq (tok-type tok) :op) (string= (tok-value tok) ">=")) :gt-e)
    ((and (eq (tok-type tok) :keyword) (string= (tok-value tok) "in")) :in)
    ((and (eq (tok-type tok) :keyword) (string= (tok-value tok) "is"))
     ;; Check for 'is not'
     (let ((next (ps-token ps 1)))
       (if (and next (eq (tok-type next) :keyword) (string= (tok-value next) "not"))
           :is-not
           :is)))
    ((and (eq (tok-type tok) :keyword) (string= (tok-value tok) "not"))
     ;; 'not in'
     (let ((next (ps-token ps 1)))
       (if (and next (eq (tok-type next) :keyword) (string= (tok-value next) "in"))
           :not-in
           nil)))
    (t nil)))

(defun consume-comparison-op (ps op)
  "Consume the token(s) for the comparison operator."
  (case op
    ((:is-not :not-in)
     (ps-advance ps) (ps-advance ps)) ; two tokens
    (t
     (ps-advance ps)))) ; one token

;;; --- Not (unary boolean) ---

(defrule parse-not-test
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "not"))
        (progn
          (ps-advance ps)
          (let ((operand (parse-not-test ps)))
            (if (failp operand) +fail+
                (make-node 'clython.ast:unary-op-node
                           :op :not :operand operand
                           :line (tok-line tok) :col (tok-col tok)))))
        (parse-comparison ps))))

;;; --- And ---

(defrule parse-and-test
  (let ((left (parse-not-test ps)))
    (when (failp left) (return-from nil +fail+))
    (let ((values (list left)))
      (loop
        (let ((tok (ps-token ps)))
          (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "and"))
            (return))
          (ps-advance ps)
          (let ((right (parse-not-test ps)))
            (when (failp right) (return))
            (push right values))))
      (if (= (length values) 1)
          left
          (make-node 'clython.ast:bool-op-node
                     :op :and
                     :values (nreverse values)
                     :line (clython.ast:node-line left)
                     :col (clython.ast:node-col left))))))

;;; --- Or ---

(defrule parse-or-test
  (let ((left (parse-and-test ps)))
    (when (failp left) (return-from nil +fail+))
    (let ((values (list left)))
      (loop
        (let ((tok (ps-token ps)))
          (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "or"))
            (return))
          (ps-advance ps)
          (let ((right (parse-and-test ps)))
            (when (failp right) (return))
            (push right values))))
      (if (= (length values) 1)
          left
          (make-node 'clython.ast:bool-op-node
                     :op :or
                     :values (nreverse values)
                     :line (clython.ast:node-line left)
                     :col (clython.ast:node-col left))))))

;;; --- Conditional expression: X if C else Y ---

(defrule parse-conditional
  (let ((body (parse-or-test ps)))
    (when (failp body) (return-from nil +fail+))
    (let ((tok (ps-token ps)))
      (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "if"))
          (progn
            (ps-advance ps)
            (let ((test (parse-or-test ps)))
              (when (failp test) (return-from nil body)) ; just the body expr
              (let ((else-tok (ps-token ps)))
                (unless (and else-tok (eq (tok-type else-tok) :keyword)
                             (string= (tok-value else-tok) "else"))
                  (return-from nil body))
                (ps-advance ps)
                (let ((orelse (parse-expression-internal ps)))
                  (if (failp orelse) body
                      (make-node 'clython.ast:if-exp-node
                                 :test test :body body :orelse orelse
                                 :line (clython.ast:node-line body)
                                 :col (clython.ast:node-col body)))))))
          body))))

;;; --- Lambda ---

(defrule parse-lambda
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "lambda"))
        (progn
          (ps-advance ps)
          (let ((args (parse-lambda-params ps)))
            ;; Expect :
            (let ((colon (ps-token ps)))
              (unless (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
                (return-from nil +fail+))
              (ps-advance ps))
            (let ((body (parse-expression-internal ps)))
              (if (failp body) +fail+
                  (make-node 'clython.ast:lambda-node
                             :args args :body body
                             :line (tok-line tok) :col (tok-col tok))))))
        (parse-conditional ps))))

(defun parse-lambda-params (ps)
  "Parse lambda parameters (simplified). Returns a py-arguments instance."
  ;; For now, parse a simple comma-separated list of names
  (let ((args '()))
    (loop
      (let ((tok (ps-token ps)))
        (unless (and tok (eq (tok-type tok) :name))
          (return))
        (ps-advance ps)
        (push (make-instance 'clython.ast:py-arg :arg (tok-value tok)) args)
        (let ((comma (ps-token ps)))
          (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
            (return))
          (ps-advance ps))))
    (make-instance 'clython.ast:py-arguments :args (nreverse args))))

;;; --- Named expression (:=) ---

(defrule parse-named-expr
  (let ((saved (ps-save ps))
        (expr (parse-lambda ps)))
    (when (failp expr) (return-from nil +fail+))
    ;; Check for :=
    (let ((tok (ps-token ps)))
      (if (and tok (eq (tok-type tok) :op) (string= (tok-value tok) ":=")
               (typep expr 'clython.ast:name-node))
          (progn
            (ps-advance ps)
            (let ((value (parse-named-expr ps)))
              (if (failp value)
                  (progn (ps-restore ps saved) +fail+)
                  (make-node 'clython.ast:named-expr-node
                             :target expr :value value
                             :line (clython.ast:node-line expr)
                             :col (clython.ast:node-col expr)))))
          expr))))

;;; --- Yield / yield from ---

(defrule parse-yield-expr
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "yield"))
        (progn
          (ps-advance ps)
          ;; Check for 'from'
          (let ((from-tok (ps-token ps)))
            (if (and from-tok (eq (tok-type from-tok) :keyword) (string= (tok-value from-tok) "from"))
                (progn
                  (ps-advance ps)
                  (let ((expr (parse-expression-internal ps)))
                    (if (failp expr) +fail+
                        (make-node 'clython.ast:yield-from-node :value expr
                                   :line (tok-line tok) :col (tok-col tok)))))
                ;; yield [expr]
                (let ((expr (parse-expression-list-opt ps)))
                  (make-node 'clython.ast:yield-node :value expr
                             :line (tok-line tok) :col (tok-col tok))))))
        +fail+)))

(defun parse-expression-list-opt (ps)
  "Parse an optional expression list (for yield, return, etc.)."
  (let ((expr (parse-star-expr-or-expr ps)))
    (if (failp expr) nil expr)))

;;; --- Star expression ---

(defrule parse-star-expr
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "*"))
        (progn
          (ps-advance ps)
          (let ((expr (parse-or-test ps)))
            (if (failp expr) +fail+
                (make-node 'clython.ast:starred-node :value expr :ctx :load
                           :line (tok-line tok) :col (tok-col tok)))))
        +fail+)))

(defrule parse-star-expr-or-expr
  (funcall (peg-or #'parse-star-expr #'parse-expression-internal) ps))

;;; --- Main expression entry point ---

(defrule parse-expression-internal
  ;; expression = yield_expr | named_expr
  (funcall (peg-or #'parse-yield-expr #'parse-named-expr) ps))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Section 5: Statement Rules
;;;; ═══════════════════════════════════════════════════════════════════════════

;;; --- Suite (block) parsing ---

(defrule parse-suite
  ;; suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
  (let ((tok (ps-token ps)))
    ;; Inline suite (simple statement on same line)
    ;; This is after the colon, check if next is NEWLINE
    (if (and tok (eq (tok-type tok) :newline))
        (progn
          (ps-advance ps) ; consume NEWLINE
          ;; Expect INDENT
          (let ((indent-tok (ps-token ps)))
            (unless (and indent-tok (eq (tok-type indent-tok) :indent))
              (return-from nil +fail+))
            (ps-advance ps))
          ;; Parse statements until DEDENT
          (let ((stmts '()))
            (loop
              (let ((dtok (ps-token ps)))
                (when (or (null dtok) (eq (tok-type dtok) :dedent))
                  (when dtok (ps-advance ps)) ; consume DEDENT
                  (return)))
              (let ((stmt (parse-statement ps)))
                (when (failp stmt)
                  ;; Skip problematic token and try to continue
                  (return))
                (if (listp stmt)
                    (setf stmts (append stmts stmt))
                    (push stmt stmts))))
            (if (listp (car stmts))
                stmts ; already in order from append
                (nreverse stmts))))
        ;; Inline suite: simple statements on same line
        (parse-simple-stmt-list ps))))

(defrule parse-simple-stmt-list
  ;; simple_stmt (';' simple_stmt)* [';'] NEWLINE
  (let ((stmts '()))
    (let ((s (parse-simple-statement ps)))
      (when (failp s) (return-from nil +fail+))
      (push s stmts))
    (loop
      (let ((tok (ps-token ps)))
        (unless (and tok (eq (tok-type tok) :op) (string= (tok-value tok) ";"))
          (return))
        (ps-advance ps)
        ;; Check if next is newline (trailing semicolon)
        (let ((next (ps-token ps)))
          (when (or (null next) (eq (tok-type next) :newline) (eq (tok-type next) :endmarker))
            (return)))
        (let ((s (parse-simple-statement ps)))
          (when (failp s) (return))
          (push s stmts))))
    ;; Consume optional newline
    (let ((nl (ps-token ps)))
      (when (and nl (eq (tok-type nl) :newline))
        (ps-advance ps)))
    (nreverse stmts)))

;;; --- Simple statements ---

(defrule parse-simple-statement
  (funcall (peg-or
            #'parse-return-stmt
            #'parse-raise-stmt
            #'parse-pass-stmt
            #'parse-break-stmt
            #'parse-continue-stmt
            #'parse-del-stmt
            #'parse-assert-stmt
            #'parse-import-stmt
            #'parse-from-import-stmt
            #'parse-global-stmt
            #'parse-nonlocal-stmt
            #'parse-assignment-or-expr)
           ps))

(defrule parse-pass-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "pass"))
        (progn (ps-advance ps)
               (make-node 'clython.ast:pass-node :line (tok-line tok) :col (tok-col tok)))
        +fail+)))

(defrule parse-break-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "break"))
        (progn (ps-advance ps)
               (make-node 'clython.ast:break-node :line (tok-line tok) :col (tok-col tok)))
        +fail+)))

(defrule parse-continue-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "continue"))
        (progn (ps-advance ps)
               (make-node 'clython.ast:continue-node :line (tok-line tok) :col (tok-col tok)))
        +fail+)))

(defrule parse-return-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "return"))
        (progn
          (ps-advance ps)
          (let ((value (parse-expression-list-opt ps)))
            (make-node 'clython.ast:return-node :value value
                       :line (tok-line tok) :col (tok-col tok))))
        +fail+)))

(defrule parse-raise-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "raise"))
        (progn
          (ps-advance ps)
          (let ((exc nil) (cause nil))
            ;; Optional exception
            (let ((e (parse-expression-internal ps)))
              (unless (failp e)
                (setf exc e)
                ;; Optional 'from'
                (let ((from-tok (ps-token ps)))
                  (when (and from-tok (eq (tok-type from-tok) :keyword) (string= (tok-value from-tok) "from"))
                    (ps-advance ps)
                    (let ((c (parse-expression-internal ps)))
                      (unless (failp c) (setf cause c)))))))
            (make-node 'clython.ast:raise-node :exc exc :cause cause
                       :line (tok-line tok) :col (tok-col tok))))
        +fail+)))

(defrule parse-del-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "del"))
        (progn
          (ps-advance ps)
          (let ((targets '()))
            (loop
              (let ((t1 (parse-primary ps)))
                (when (failp t1) (return))
                (push t1 targets))
              (let ((comma (ps-token ps)))
                (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
                  (return))
                (ps-advance ps)))
            (make-node 'clython.ast:delete-node :targets (nreverse targets)
                       :line (tok-line tok) :col (tok-col tok))))
        +fail+)))

(defrule parse-assert-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "assert"))
        (progn
          (ps-advance ps)
          (let ((test (parse-expression-internal ps)))
            (when (failp test) (return-from nil +fail+))
            (let ((msg nil))
              (let ((comma (ps-token ps)))
                (when (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
                  (ps-advance ps)
                  (let ((m (parse-expression-internal ps)))
                    (unless (failp m) (setf msg m)))))
              (make-node 'clython.ast:assert-node :test test :msg msg
                         :line (tok-line tok) :col (tok-col tok)))))
        +fail+)))

;;; --- Import statements ---

(defrule parse-import-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "import"))
        (progn
          (ps-advance ps)
          (let ((names (parse-dotted-as-names ps)))
            (make-node 'clython.ast:import-node :names names
                       :line (tok-line tok) :col (tok-col tok))))
        +fail+)))

(defun parse-dotted-as-names (ps)
  "Parse import names: dotted_name ['as' NAME] (',' dotted_name ['as' NAME])*"
  (let ((names '()))
    (loop
      (let ((dotted (parse-dotted-name ps)))
        (when (null dotted) (return))
        (let ((asname nil))
          (let ((as-tok (ps-token ps)))
            (when (and as-tok (eq (tok-type as-tok) :keyword) (string= (tok-value as-tok) "as"))
              (ps-advance ps)
              (let ((name-tok (ps-token ps)))
                (when (and name-tok (eq (tok-type name-tok) :name))
                  (ps-advance ps)
                  (setf asname (tok-value name-tok))))))
          (push (make-instance 'clython.ast:py-alias :name dotted :asname asname) names)))
      (let ((comma (ps-token ps)))
        (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
          (return))
        (ps-advance ps)))
    (nreverse names)))

(defun parse-dotted-name (ps)
  "Parse a dotted name like 'os.path.join'. Returns a string or nil."
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :name))
      (return-from parse-dotted-name nil))
    (ps-advance ps)
    (let ((parts (list (tok-value tok))))
      (loop
        (let ((dot (ps-token ps)))
          (unless (and dot (eq (tok-type dot) :op) (string= (tok-value dot) "."))
            (return))
          (ps-advance ps)
          (let ((name (ps-token ps)))
            (unless (and name (eq (tok-type name) :name))
              (return))
            (ps-advance ps)
            (push (tok-value name) parts))))
      (format nil "~{~A~^.~}" (nreverse parts)))))

(defrule parse-from-import-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "from"))
        (progn
          (ps-advance ps)
          ;; Count leading dots for relative imports
          (let ((level 0) (module nil))
            (loop
              (let ((dot (ps-token ps)))
                (cond
                  ((and dot (eq (tok-type dot) :op) (string= (tok-value dot) "."))
                   (ps-advance ps) (incf level))
                  ((and dot (eq (tok-type dot) :op) (string= (tok-value dot) "..."))
                   (ps-advance ps) (incf level 3))
                  (t (return)))))
            ;; Module name (optional if we have dots)
            (let ((mod-name (parse-dotted-name ps)))
              (setf module mod-name))
            ;; 'import'
            (let ((imp-tok (ps-token ps)))
              (unless (and imp-tok (eq (tok-type imp-tok) :keyword) (string= (tok-value imp-tok) "import"))
                (return-from nil +fail+))
              (ps-advance ps))
            ;; Names: * or name-list
            (let ((names nil))
              (let ((star (ps-token ps)))
                (if (and star (eq (tok-type star) :op) (string= (tok-value star) "*"))
                    (progn
                      (ps-advance ps)
                      (setf names (list (make-instance 'clython.ast:py-alias :name "*" :asname nil))))
                    ;; ( names ) or names
                    (let ((paren nil))
                      (when (and (ps-token ps) (eq (tok-type (ps-token ps)) :op)
                                 (string= (tok-value (ps-token ps)) "("))
                        (ps-advance ps) (setf paren t))
                      (setf names (parse-import-as-names ps))
                      (when paren
                        (let ((close (ps-token ps)))
                          (when (and close (eq (tok-type close) :op) (string= (tok-value close) ")"))
                            (ps-advance ps)))))))
              (make-node 'clython.ast:import-from-node
                         :module module :names names :level level
                         :line (tok-line tok) :col (tok-col tok)))))
        +fail+)))

(defun parse-import-as-names (ps)
  "Parse NAME ['as' NAME] (',' NAME ['as' NAME])*"
  (let ((names '()))
    (loop
      (let ((name-tok (ps-token ps)))
        (unless (and name-tok (eq (tok-type name-tok) :name))
          (return))
        (ps-advance ps)
        (let ((asname nil))
          (let ((as-tok (ps-token ps)))
            (when (and as-tok (eq (tok-type as-tok) :keyword) (string= (tok-value as-tok) "as"))
              (ps-advance ps)
              (let ((alias-tok (ps-token ps)))
                (when (and alias-tok (eq (tok-type alias-tok) :name))
                  (ps-advance ps)
                  (setf asname (tok-value alias-tok))))))
          (push (make-instance 'clython.ast:py-alias
                               :name (tok-value name-tok) :asname asname)
                names)))
      (let ((comma (ps-token ps)))
        (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
          (return))
        (ps-advance ps)))
    (nreverse names)))

;;; --- Global / Nonlocal ---

(defrule parse-global-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "global"))
        (progn
          (ps-advance ps)
          (let ((names (parse-name-list ps)))
            (make-node 'clython.ast:global-node :names names
                       :line (tok-line tok) :col (tok-col tok))))
        +fail+)))

(defrule parse-nonlocal-stmt
  (let ((tok (ps-token ps)))
    (if (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "nonlocal"))
        (progn
          (ps-advance ps)
          (let ((names (parse-name-list ps)))
            (make-node 'clython.ast:nonlocal-node :names names
                       :line (tok-line tok) :col (tok-col tok))))
        +fail+)))

(defun parse-name-list (ps)
  "Parse comma-separated NAME tokens, return list of strings."
  (let ((names '()))
    (loop
      (let ((tok (ps-token ps)))
        (unless (and tok (eq (tok-type tok) :name))
          (return))
        (ps-advance ps)
        (push (tok-value tok) names))
      (let ((comma (ps-token ps)))
        (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
          (return))
        (ps-advance ps)))
    (nreverse names)))

;;; --- Assignment or expression statement ---

(defrule parse-assignment-or-expr
  ;; This handles: expr_stmt | assignment | aug_assign | ann_assign
  (let ((saved (ps-save ps))
        (first-expr (parse-star-expr-or-expr ps)))
    (when (failp first-expr)
      (return-from nil +fail+))
    (let ((tok (ps-token ps)))
      (cond
        ;; Augmented assignment: +=, -=, *=, etc.
        ((and tok (eq (tok-type tok) :op)
              (member (tok-value tok) '("+=" "-=" "*=" "/=" "//=" "%=" "**=" ">>=" "<<=" "&=" "^=" "|=" "@=")
                      :test #'string=))
         (let ((op-str (tok-value tok)))
           (ps-advance ps)
           (let ((value (parse-expression-internal ps)))
             (if (failp value)
                 (progn (ps-restore ps saved) +fail+)
                 (make-node 'clython.ast:aug-assign-node
                            :target first-expr
                            :op (aug-assign-op op-str)
                            :value value
                            :line (clython.ast:node-line first-expr)
                            :col (clython.ast:node-col first-expr))))))
        ;; Simple assignment: =
        ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "="))
         (let ((targets (list first-expr))
               (final-value nil))
           ;; Handle chained assignment: a = b = c = expr
           (loop
             (let ((eq-tok (ps-token ps)))
               (unless (and eq-tok (eq (tok-type eq-tok) :op) (string= (tok-value eq-tok) "="))
                 (return))
               (ps-advance ps)
               (let ((next (parse-star-expr-or-expr ps)))
                 (when (failp next) (return))
                 ;; Check if there's another = after this
                 (let ((peek (ps-token ps)))
                   (if (and peek (eq (tok-type peek) :op) (string= (tok-value peek) "="))
                       (push next targets)
                       (progn (setf final-value next) (return)))))))
           (if final-value
               (make-node 'clython.ast:assign-node
                          :targets (nreverse targets)
                          :value final-value
                          :line (clython.ast:node-line first-expr)
                          :col (clython.ast:node-col first-expr))
               (progn (ps-restore ps saved) +fail+))))
        ;; Annotation: : type [= value]
        ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) ":"))
         (ps-advance ps)
         (let ((annotation (parse-expression-internal ps)))
           (when (failp annotation)
             ;; Just expression statement
             (ps-restore ps saved)
             (let ((e (parse-star-expr-or-expr ps)))
               (if (failp e) +fail+
                   (make-node 'clython.ast:expr-stmt-node :value e
                              :line (clython.ast:node-line e) :col (clython.ast:node-col e)))))
           (let ((value nil))
             (let ((eq-tok (ps-token ps)))
               (when (and eq-tok (eq (tok-type eq-tok) :op) (string= (tok-value eq-tok) "="))
                 (ps-advance ps)
                 (let ((v (parse-expression-internal ps)))
                   (unless (failp v) (setf value v)))))
             (make-node 'clython.ast:ann-assign-node
                        :target first-expr :annotation annotation :value value
                        :simple (if (typep first-expr 'clython.ast:name-node) 1 0)
                        :line (clython.ast:node-line first-expr)
                        :col (clython.ast:node-col first-expr)))))
        ;; Expression statement
        (t
         (make-node 'clython.ast:expr-stmt-node
                    :value first-expr
                    :line (clython.ast:node-line first-expr)
                    :col (clython.ast:node-col first-expr)))))))

(defun aug-assign-op (str)
  "Convert augmented assignment operator string to AST keyword."
  (cond
    ((string= str "+=")  :add)
    ((string= str "-=")  :sub)
    ((string= str "*=")  :mult)
    ((string= str "/=")  :div)
    ((string= str "//=") :floor-div)
    ((string= str "%=")  :mod)
    ((string= str "**=") :pow)
    ((string= str ">>=") :r-shift)
    ((string= str "<<=") :l-shift)
    ((string= str "&=")  :bit-and)
    ((string= str "^=")  :bit-xor)
    ((string= str "|=")  :bit-or)
    ((string= str "@=")  :mat-mult)
    (t :add)))

;;; --- Compound statements ---

(defrule parse-compound-statement
  (funcall (peg-or
            #'parse-if-stmt
            #'parse-while-stmt
            #'parse-for-stmt
            #'parse-try-stmt
            #'parse-with-stmt
            #'parse-funcdef
            #'parse-classdef
            #'parse-async-stmt
            #'parse-match-stmt
            #'parse-decorated)
           ps))

;;; --- If statement ---

(defrule parse-if-stmt
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "if"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((test (parse-expression-internal ps)))
      (when (failp test) (return-from nil +fail+))
      ;; Expect :
      (let ((colon (ps-token ps)))
        (unless (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
          (return-from nil +fail+))
        (ps-advance ps))
      (let ((body (parse-suite ps)))
        (when (failp body) (return-from nil +fail+))
        ;; elif / else
        (let ((orelse (parse-elif-else ps)))
          (make-node 'clython.ast:if-node
                     :test test :body body :orelse orelse
                     :line (tok-line tok) :col (tok-col tok)))))))

(defun parse-elif-else (ps)
  "Parse elif/else chains. Returns list of statements or nil."
  (let ((tok (ps-token ps)))
    (cond
      ((and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "elif"))
       (ps-advance ps)
       (let ((test (parse-expression-internal ps)))
         (when (failp test) (return-from parse-elif-else nil))
         (let ((colon (ps-token ps)))
           (unless (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
             (return-from parse-elif-else nil))
           (ps-advance ps))
         (let ((body (parse-suite ps)))
           (when (failp body) (return-from parse-elif-else nil))
           (let ((orelse (parse-elif-else ps)))
             (list (make-node 'clython.ast:if-node
                              :test test :body body :orelse orelse
                              :line (tok-line tok) :col (tok-col tok)))))))
      ((and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "else"))
       (ps-advance ps)
       (let ((colon (ps-token ps)))
         (unless (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
           (return-from parse-elif-else nil))
         (ps-advance ps))
       (let ((body (parse-suite ps)))
         (if (failp body) nil body)))
      (t nil))))

;;; --- While statement ---

(defrule parse-while-stmt
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "while"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((test (parse-expression-internal ps)))
      (when (failp test) (return-from nil +fail+))
      (expect-colon ps)
      (let ((body (parse-suite ps)))
        (when (failp body) (return-from nil +fail+))
        (let ((orelse nil))
          (let ((else-tok (ps-token ps)))
            (when (and else-tok (eq (tok-type else-tok) :keyword) (string= (tok-value else-tok) "else"))
              (ps-advance ps)
              (expect-colon ps)
              (let ((eb (parse-suite ps)))
                (unless (failp eb) (setf orelse eb)))))
          (make-node 'clython.ast:while-node
                     :test test :body body :orelse orelse
                     :line (tok-line tok) :col (tok-col tok)))))))

(defun expect-colon (ps)
  "Consume a : token, or do nothing if not present."
  (let ((tok (ps-token ps)))
    (when (and tok (eq (tok-type tok) :op) (string= (tok-value tok) ":"))
      (ps-advance ps))))

;;; --- For statement ---

(defrule parse-for-stmt
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "for"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((target (parse-target-list ps)))
      (when (failp target) (return-from nil +fail+))
      ;; 'in'
      (let ((in-tok (ps-token ps)))
        (unless (and in-tok (eq (tok-type in-tok) :keyword) (string= (tok-value in-tok) "in"))
          (return-from nil +fail+))
        (ps-advance ps))
      (let ((iter (parse-expression-list ps)))
        (when (failp iter) (return-from nil +fail+))
        (expect-colon ps)
        (let ((body (parse-suite ps)))
          (when (failp body) (return-from nil +fail+))
          (let ((orelse nil))
            (let ((else-tok (ps-token ps)))
              (when (and else-tok (eq (tok-type else-tok) :keyword) (string= (tok-value else-tok) "else"))
                (ps-advance ps)
                (expect-colon ps)
                (let ((eb (parse-suite ps)))
                  (unless (failp eb) (setf orelse eb)))))
            (make-node 'clython.ast:for-node
                       :target target :iter iter :body body :orelse orelse
                       :line (tok-line tok) :col (tok-col tok))))))))

(defun parse-expression-list (ps)
  "Parse an expression list (comma-separated), wrapping in tuple if multiple."
  (let ((first (parse-star-expr-or-expr ps)))
    (when (failp first) (return-from parse-expression-list +fail+))
    (let ((elts (list first)))
      (loop
        (let ((comma (ps-token ps)))
          (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
            (return))
          (ps-advance ps)
          ;; Trailing comma -> tuple
          (let ((next-tok (ps-token ps)))
            (when (or (null next-tok)
                      (eq (tok-type next-tok) :newline)
                      (eq (tok-type next-tok) :indent)
                      (and (eq (tok-type next-tok) :op) (string= (tok-value next-tok) ":")))
              (return)))
          (let ((e (parse-star-expr-or-expr ps)))
            (when (failp e) (return))
            (push e elts))))
      (if (= (length elts) 1)
          first
          (make-node 'clython.ast:tuple-node
                     :elts (nreverse elts) :ctx :load
                     :line (clython.ast:node-line first)
                     :col (clython.ast:node-col first))))))

;;; --- Try statement ---

(defrule parse-try-stmt
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "try"))
      (return-from nil +fail+))
    (ps-advance ps)
    (expect-colon ps)
    (let ((body (parse-suite ps)))
      (when (failp body) (return-from nil +fail+))
      (let ((handlers '())
            (orelse nil)
            (finalbody nil))
        ;; except clauses
        (loop
          (let ((exc-tok (ps-token ps)))
            (unless (and exc-tok (eq (tok-type exc-tok) :keyword) (string= (tok-value exc-tok) "except"))
              (return))
            (ps-advance ps)
            (let ((exc-type nil) (exc-name nil))
              ;; Optional exception type
              (let ((next (ps-token ps)))
                (unless (and next (eq (tok-type next) :op) (string= (tok-value next) ":"))
                  (let ((t1 (parse-expression-internal ps)))
                    (unless (failp t1)
                      (setf exc-type t1)
                      ;; Optional 'as' name
                      (let ((as-tok (ps-token ps)))
                        (when (and as-tok (eq (tok-type as-tok) :keyword) (string= (tok-value as-tok) "as"))
                          (ps-advance ps)
                          (let ((name-tok (ps-token ps)))
                            (when (and name-tok (eq (tok-type name-tok) :name))
                              (ps-advance ps)
                              (setf exc-name (tok-value name-tok))))))))))
              (expect-colon ps)
              (let ((handler-body (parse-suite ps)))
                (push (make-instance 'clython.ast:py-exception-handler
                                     :type exc-type :name exc-name
                                     :body (if (failp handler-body) nil handler-body))
                      handlers)))))
        ;; else clause
        (let ((else-tok (ps-token ps)))
          (when (and else-tok (eq (tok-type else-tok) :keyword) (string= (tok-value else-tok) "else"))
            (ps-advance ps)
            (expect-colon ps)
            (let ((eb (parse-suite ps)))
              (unless (failp eb) (setf orelse eb)))))
        ;; finally clause
        (let ((fin-tok (ps-token ps)))
          (when (and fin-tok (eq (tok-type fin-tok) :keyword) (string= (tok-value fin-tok) "finally"))
            (ps-advance ps)
            (expect-colon ps)
            (let ((fb (parse-suite ps)))
              (unless (failp fb) (setf finalbody fb)))))
        (make-node 'clython.ast:try-node
                   :body body
                   :handlers (nreverse handlers)
                   :orelse orelse
                   :finalbody finalbody
                   :line (tok-line tok) :col (tok-col tok))))))

;;; --- With statement ---

(defrule parse-with-stmt
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "with"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((items '()))
      ;; Parse with items
      (loop
        (let ((ctx (parse-expression-internal ps)))
          (when (failp ctx) (return))
          (let ((opt-var nil))
            (let ((as-tok (ps-token ps)))
              (when (and as-tok (eq (tok-type as-tok) :keyword) (string= (tok-value as-tok) "as"))
                (ps-advance ps)
                (let ((target (parse-primary ps)))
                  (unless (failp target) (setf opt-var target)))))
            (push (make-instance 'clython.ast:py-with-item
                                 :context-expr ctx :optional-vars opt-var)
                  items)))
        (let ((comma (ps-token ps)))
          (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
            (return))
          (ps-advance ps)))
      (expect-colon ps)
      (let ((body (parse-suite ps)))
        (when (failp body) (return-from nil +fail+))
        (make-node 'clython.ast:with-node
                   :items (nreverse items) :body body
                   :line (tok-line tok) :col (tok-col tok))))))

;;; --- Function definition ---

(defrule parse-funcdef
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "def"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((name-tok (ps-token ps)))
      (unless (and name-tok (eq (tok-type name-tok) :name))
        (return-from nil +fail+))
      (ps-advance ps)
      ;; Parameters
      (let ((open-tok (ps-token ps)))
        (unless (and open-tok (eq (tok-type open-tok) :op) (string= (tok-value open-tok) "("))
          (return-from nil +fail+))
        (ps-advance ps))
      (let ((args (parse-func-params ps)))
        (let ((close-tok (ps-token ps)))
          (unless (and close-tok (eq (tok-type close-tok) :op) (string= (tok-value close-tok) ")"))
            (return-from nil +fail+))
          (ps-advance ps))
        ;; Optional return annotation: -> expr
        (let ((returns nil))
          (let ((arrow (ps-token ps)))
            (when (and arrow (eq (tok-type arrow) :op) (string= (tok-value arrow) "->"))
              (ps-advance ps)
              (let ((ret-expr (parse-expression-internal ps)))
                (unless (failp ret-expr) (setf returns ret-expr)))))
          (expect-colon ps)
          (let ((body (parse-suite ps)))
            (when (failp body) (return-from nil +fail+))
            (make-node 'clython.ast:function-def-node
                       :name (tok-value name-tok)
                       :args args
                       :body body
                       :returns returns
                       :line (tok-line tok) :col (tok-col tok))))))))

(defun parse-func-params (ps)
  "Parse function parameters. Returns a py-arguments instance."
  (let ((args '())
        (defaults '())
        (vararg nil)
        (kwonlyargs '())
        (kw-defaults '())
        (kwarg nil)
        (posonlyargs '())
        (seen-star nil)
        (seen-slash nil))
    (declare (ignore seen-slash))
    ;; Empty params
    (let ((tok (ps-token ps)))
      (when (and tok (eq (tok-type tok) :op) (string= (tok-value tok) ")"))
        (return-from parse-func-params
          (make-instance 'clython.ast:py-arguments))))
    (loop
      (let ((tok (ps-token ps)))
        (cond
          ;; **kwargs
          ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "**"))
           (ps-advance ps)
           (let ((name-tok (ps-token ps)))
             (when (and name-tok (eq (tok-type name-tok) :name))
               (ps-advance ps)
               (let ((ann nil))
                 (let ((colon (ps-token ps)))
                   (when (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
                     (ps-advance ps)
                     (let ((a (parse-expression-internal ps)))
                       (unless (failp a) (setf ann a)))))
                 (setf kwarg (make-instance 'clython.ast:py-arg
                                            :arg (tok-value name-tok) :annotation ann))))))
          ;; *args or bare *
          ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "*"))
           (ps-advance ps)
           (setf seen-star t)
           (let ((next (ps-token ps)))
             (when (and next (eq (tok-type next) :name))
               (ps-advance ps)
               (let ((ann nil))
                 (let ((colon (ps-token ps)))
                   (when (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
                     (ps-advance ps)
                     (let ((a (parse-expression-internal ps)))
                       (unless (failp a) (setf ann a)))))
                 (setf vararg (make-instance 'clython.ast:py-arg
                                             :arg (tok-value next) :annotation ann))))))
          ;; / (positional-only separator)
          ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "/"))
           (ps-advance ps)
           (setf posonlyargs args)
           (setf args '()))
          ;; Regular parameter
          ((and tok (eq (tok-type tok) :name))
           (ps-advance ps)
           (let ((ann nil) (default nil))
             ;; Optional annotation
             (let ((colon (ps-token ps)))
               (when (and colon (eq (tok-type colon) :op) (string= (tok-value colon) ":"))
                 (ps-advance ps)
                 (let ((a (parse-expression-internal ps)))
                   (unless (failp a) (setf ann a)))))
             ;; Optional default
             (let ((eq-tok (ps-token ps)))
               (when (and eq-tok (eq (tok-type eq-tok) :op) (string= (tok-value eq-tok) "="))
                 (ps-advance ps)
                 (let ((d (parse-expression-internal ps)))
                   (unless (failp d) (setf default d)))))
             (let ((arg (make-instance 'clython.ast:py-arg
                                       :arg (tok-value tok) :annotation ann)))
               (if seen-star
                   (progn
                     (push arg kwonlyargs)
                     (push default kw-defaults))
                   (progn
                     (push arg args)
                     (when default (push default defaults)))))))
          (t (return))))
      ;; Comma or end
      (let ((comma (ps-token ps)))
        (unless (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
          (return))
        (ps-advance ps))
      ;; Check for close paren (trailing comma)
      (let ((close-check (ps-token ps)))
        (when (and close-check (eq (tok-type close-check) :op) (string= (tok-value close-check) ")"))
          (return))))
    (make-instance 'clython.ast:py-arguments
                   :posonlyargs (nreverse posonlyargs)
                   :args (nreverse args)
                   :vararg vararg
                   :kwonlyargs (nreverse kwonlyargs)
                   :kw-defaults (nreverse kw-defaults)
                   :kwarg kwarg
                   :defaults (nreverse defaults))))

;;; --- Class definition ---

(defrule parse-classdef
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "class"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((name-tok (ps-token ps)))
      (unless (and name-tok (eq (tok-type name-tok) :name))
        (return-from nil +fail+))
      (ps-advance ps)
      ;; Optional base classes
      (let ((bases nil) (keywords nil))
        (let ((open-tok (ps-token ps)))
          (when (and open-tok (eq (tok-type open-tok) :op) (string= (tok-value open-tok) "("))
            (ps-advance ps)
            (multiple-value-bind (a kw) (parse-arglist ps)
              (setf bases a)
              (setf keywords kw))
            (let ((close (ps-token ps)))
              (when (and close (eq (tok-type close) :op) (string= (tok-value close) ")"))
                (ps-advance ps)))))
        (expect-colon ps)
        (let ((body (parse-suite ps)))
          (when (failp body) (return-from nil +fail+))
          (make-node 'clython.ast:class-def-node
                     :name (tok-value name-tok)
                     :bases bases
                     :keywords keywords
                     :body body
                     :line (tok-line tok) :col (tok-col tok)))))))

;;; --- Async statement (async def, async for, async with) ---

(defrule parse-async-stmt
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :keyword) (string= (tok-value tok) "async"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((next (ps-token ps)))
      (cond
        ;; async def
        ((and next (eq (tok-type next) :keyword) (string= (tok-value next) "def"))
         (let ((func (parse-funcdef ps)))
           (if (failp func) +fail+
               ;; Convert function-def-node to async-function-def-node
               (make-node 'clython.ast:async-function-def-node
                          :name (clython.ast:function-def-node-name func)
                          :args (clython.ast:function-def-node-args func)
                          :body (clython.ast:function-def-node-body func)
                          :returns (clython.ast:function-def-node-returns func)
                          :decorator-list (clython.ast:function-def-node-decorator-list func)
                          :line (tok-line tok) :col (tok-col tok)))))
        ;; async for
        ((and next (eq (tok-type next) :keyword) (string= (tok-value next) "for"))
         (let ((for-node (parse-for-stmt ps)))
           (if (failp for-node) +fail+
               (make-node 'clython.ast:async-for-node
                          :target (clython.ast:for-node-target for-node)
                          :iter (clython.ast:for-node-iter for-node)
                          :body (clython.ast:for-node-body for-node)
                          :orelse (clython.ast:for-node-orelse for-node)
                          :line (tok-line tok) :col (tok-col tok)))))
        ;; async with
        ((and next (eq (tok-type next) :keyword) (string= (tok-value next) "with"))
         (let ((with-node (parse-with-stmt ps)))
           (if (failp with-node) +fail+
               (make-node 'clython.ast:async-with-node
                          :items (clython.ast:with-node-items with-node)
                          :body (clython.ast:with-node-body with-node)
                          :line (tok-line tok) :col (tok-col tok)))))
        (t +fail+)))))

;;; --- Decorated definitions ---

(defrule parse-decorated
  ;; @ expr NEWLINE (repeated) then funcdef or classdef
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :op) (string= (tok-value tok) "@"))
      (return-from nil +fail+))
    (let ((decorators '()))
      (loop
        (let ((at (ps-token ps)))
          (unless (and at (eq (tok-type at) :op) (string= (tok-value at) "@"))
            (return))
          (ps-advance ps)
          (let ((expr (parse-expression-internal ps)))
            (when (failp expr) (return))
            (push expr decorators))
          ;; Consume newline
          (let ((nl (ps-token ps)))
            (when (and nl (eq (tok-type nl) :newline))
              (ps-advance ps)))))
      (setf decorators (nreverse decorators))
      ;; Now parse the definition
      (let ((defn (funcall (peg-or #'parse-funcdef #'parse-classdef #'parse-async-stmt) ps)))
        (when (failp defn) (return-from nil +fail+))
        ;; Attach decorators
        (cond
          ((typep defn 'clython.ast:function-def-node)
           (setf (clython.ast:function-def-node-decorator-list defn) decorators))
          ((typep defn 'clython.ast:class-def-node)
           (setf (clython.ast:class-def-node-decorator-list defn) decorators))
          ((typep defn 'clython.ast:async-function-def-node)
           (setf (clython.ast:async-function-def-node-decorator-list defn) decorators)))
        defn))))

;;; --- Match statement (soft keyword) ---

(defrule parse-match-stmt
  ;; match EXPR : NEWLINE INDENT case_block+ DEDENT
  (let ((tok (ps-token ps)))
    (unless (and tok (eq (tok-type tok) :name) (string= (tok-value tok) "match"))
      (return-from nil +fail+))
    (ps-advance ps)
    (let ((subject (parse-expression-internal ps)))
      (when (failp subject) (return-from nil +fail+))
      (expect-colon ps)
      ;; Expect NEWLINE INDENT
      (let ((nl (ps-token ps)))
        (when (and nl (eq (tok-type nl) :newline)) (ps-advance ps)))
      (let ((indent-tok (ps-token ps)))
        (unless (and indent-tok (eq (tok-type indent-tok) :indent))
          (return-from nil +fail+))
        (ps-advance ps))
      ;; Parse case blocks
      (let ((cases '()))
        (loop
          (let ((case-tok (ps-token ps)))
            (unless (and case-tok (eq (tok-type case-tok) :name) (string= (tok-value case-tok) "case"))
              (return))
            (ps-advance ps)
            ;; Pattern (simplified: treat as expression for now)
            (let ((pattern (parse-match-pattern ps)))
              (when (failp pattern) (return))
              ;; Optional guard: if expr
              (let ((guard nil))
                (let ((if-tok (ps-token ps)))
                  (when (and if-tok (eq (tok-type if-tok) :keyword) (string= (tok-value if-tok) "if"))
                    (ps-advance ps)
                    (let ((g (parse-expression-internal ps)))
                      (unless (failp g) (setf guard g)))))
                (expect-colon ps)
                (let ((body (parse-suite ps)))
                  (push (make-instance 'clython.ast:py-match-case
                                       :pattern pattern :guard guard
                                       :body (if (failp body) nil body))
                        cases))))))
        ;; Consume DEDENT
        (let ((dedent-tok (ps-token ps)))
          (when (and dedent-tok (eq (tok-type dedent-tok) :dedent))
            (ps-advance ps)))
        (make-node 'clython.ast:match-node
                   :subject subject
                   :cases (nreverse cases)
                   :line (tok-line tok) :col (tok-col tok))))))

(defrule parse-match-pattern
  ;; Simplified pattern parsing - handles common patterns
  ;; Full pattern matching would need much more work
  (let ((tok (ps-token ps)))
    (cond
      ;; Wildcard _
      ((and tok (eq (tok-type tok) :name) (string= (tok-value tok) "_"))
       (ps-advance ps)
       (make-node 'clython.ast:match-as-node :pattern nil :name nil
                  :line (tok-line tok) :col (tok-col tok)))
      ;; Constants
      ((and tok (eq (tok-type tok) :keyword)
            (member (tok-value tok) '("True" "False" "None") :test #'string=))
       (let ((val (cond ((string= (tok-value tok) "True") t)
                        ((string= (tok-value tok) "False") nil)
                        (t :none))))
         (ps-advance ps)
         (make-node 'clython.ast:match-singleton-node :value val
                    :line (tok-line tok) :col (tok-col tok))))
      ;; Number or string
      ((or (eq (tok-type tok) :number) (eq (tok-type tok) :string) (eq (tok-type tok) :fstring))
       (let ((expr (parse-atom ps)))
         (if (failp expr) +fail+
             (make-node 'clython.ast:match-value-node :value expr
                        :line (tok-line tok) :col (tok-col tok)))))
      ;; Name (capture pattern or value pattern if dotted)
      ((and tok (eq (tok-type tok) :name))
       (let ((expr (parse-primary ps)))
         (if (failp expr) +fail+
             ;; Check for 'as' binding
             (let ((as-tok (ps-token ps)))
               (if (and as-tok (eq (tok-type as-tok) :keyword) (string= (tok-value as-tok) "as"))
                   (progn
                     (ps-advance ps)
                     (let ((name-tok (ps-token ps)))
                       (if (and name-tok (eq (tok-type name-tok) :name))
                           (progn
                             (ps-advance ps)
                             (make-node 'clython.ast:match-as-node
                                        :pattern (make-node 'clython.ast:match-value-node :value expr)
                                        :name (tok-value name-tok)
                                        :line (clython.ast:node-line expr)
                                        :col (clython.ast:node-col expr)))
                           +fail+)))
                   ;; Simple name -> capture if not dotted, value if dotted
                   (if (typep expr 'clython.ast:name-node)
                       (make-node 'clython.ast:match-as-node
                                  :pattern nil
                                  :name (clython.ast:name-node-id expr)
                                  :line (clython.ast:node-line expr)
                                  :col (clython.ast:node-col expr))
                       (make-node 'clython.ast:match-value-node :value expr
                                  :line (clython.ast:node-line expr)
                                  :col (clython.ast:node-col expr))))))))
      ;; [ ] sequence pattern
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "["))
       (ps-advance ps)
       (let ((patterns '()))
         (loop
           (let ((close (ps-token ps)))
             (when (and close (eq (tok-type close) :op) (string= (tok-value close) "]"))
               (ps-advance ps)
               (return)))
           (let ((p (parse-match-pattern ps)))
             (when (failp p) (return))
             (push p patterns))
           (let ((comma (ps-token ps)))
             (when (and comma (eq (tok-type comma) :op) (string= (tok-value comma) ","))
               (ps-advance ps))))
         (make-node 'clython.ast:match-sequence-node
                    :patterns (nreverse patterns)
                    :line (tok-line tok) :col (tok-col tok))))
      ;; ( ) grouped or sequence pattern
      ((and tok (eq (tok-type tok) :op) (string= (tok-value tok) "("))
       (ps-advance ps)
       (let ((inner (parse-match-pattern ps)))
         (when (failp inner)
           (return-from nil +fail+))
         (let ((close (ps-token ps)))
           (if (and close (eq (tok-type close) :op) (string= (tok-value close) ")"))
               (progn (ps-advance ps) inner)
               +fail+))))
      (t +fail+))))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Section 6: Top-level Statement and Module
;;;; ═══════════════════════════════════════════════════════════════════════════

(defrule parse-statement
  ;; Skip newlines first
  (progn
    (skip-newlines ps)
    (funcall (peg-or #'parse-compound-statement
                     #'parse-simple-stmt-list)
             ps)))

(defun parse-module (tokens)
  "Parse a list of tokens into a module-node AST.
   This is the main entry point for parsing a complete Python source file."
  (let ((ps (make-parser-state tokens))
        (stmts '()))
    ;; Parse statements until ENDMARKER
    (block module-loop
      (tagbody
       :next-stmt
        (skip-newlines ps)
        (let ((tok (ps-token ps)))
          (when (or (null tok) (eq (tok-type tok) :endmarker))
            (return-from module-loop)))
        (let ((stmt (parse-statement ps)))
          (when (failp stmt)
            ;; Syntax error — cannot parse statement at current token
            (let ((tok (ps-token ps)))
              (when (or (null tok) (eq (tok-type tok) :endmarker))
                (return-from module-loop))
              (error 'parser-error
                     :message (format nil "invalid syntax: unexpected '~A'"
                                      (tok-value tok))
                     :line (tok-line tok)
                     :column (tok-col tok))))
          (if (listp stmt)
              (setf stmts (append stmts stmt))
              (setf stmts (append stmts (list stmt)))))
        (go :next-stmt)))
    ;; Build module node — stmts is always in source order (append-only)
    (let ((body stmts))
      (make-instance 'clython.ast:module-node
                     :body body
                     :line 1 :col 0))))

(defun parse-expression (tokens)
  "Parse a list of tokens as a single expression.
   Returns an expression-node wrapping the parsed expression."
  (let ((ps (make-parser-state tokens)))
    (skip-newlines ps)
    (let ((expr (parse-expression-internal ps)))
      (if (failp expr)
          (error 'parser-error :message "Failed to parse expression"
                 :line (current-line ps) :column (current-col ps))
          (make-instance 'clython.ast:expression-node
                         :body expr
                         :line 1 :col 0)))))