;;;; clython.lisp — Main entry point for the Clython interpreter

(defpackage :clython
  (:use :cl)
  (:import-from :clython.exceptions #:py-syntax-error)
  (:export #:repl #:py-eval #:py-eval-expr #:py-parse #:py-syntax-error))

(in-package :clython)

(defun py-parse (source)
  "Parse a Python source string and return the AST."
  (let ((tokens (clython.lexer:tokenize source)))
    (handler-case
        (clython.parser:parse-module tokens)
      (clython.parser:parser-error (e)
        (error 'py-syntax-error
               :message (format nil "~A" e))))))

(defun py-eval (source &optional env)
  "Evaluate a Python source string. Returns the last expression value (as a py-object).
   If ENV is supplied, evaluates in that environment (for REPL continuity)."
  (let* ((ast (py-parse source))
         (env (or env (clython.scope:make-global-env))))
    (clython.eval:eval-node ast env)))

(defun py-eval-expr (source env)
  "Try to evaluate SOURCE as a single expression in ENV.
   Returns (values result t) on success, or (values nil nil) if SOURCE
   is not a valid standalone expression."
  (handler-case
      (let* ((tokens (clython.lexer:tokenize source))
             (expr (clython.parser:parse-expression tokens)))
        (values (clython.eval:eval-node expr env) t))
    (error () (values nil nil))))

(defun block-starter-p (line)
  "Return T if LINE ends with a colon, indicating a block-starting statement."
  (let ((trimmed (string-right-trim '(#\Space #\Tab #\Return) line)))
    (and (plusp (length trimmed))
         (char= (char trimmed (1- (length trimmed))) #\:))))

(defun continuation-line-p (line)
  "Return T if LINE is indented (belongs to a block body)."
  (and (plusp (length line))
       (or (char= (char line 0) #\Space)
           (char= (char line 0) #\Tab))))

(defun repl ()
  "Start an interactive Clython REPL.

  Supports multi-line input: when a line ends with ':', keep reading
  continuation lines (shown with '... ' prompt) until a blank line
  signals end of block. Blank lines on a fresh prompt are ignored."
  (format t "Clython 0.1.0 — Python in Common Lisp~%")
  (format t "Type (quit) to exit.~%~%")
  (let ((env (clython.scope:make-global-env)))
    (loop
      (format t ">>> ")
      (force-output)
      (let ((first-line (read-line *standard-input* nil :eof)))
        (cond
          ;; EOF or quit — exit.
          ((or (eq first-line :eof)
               (string= first-line "(quit)"))
           (return))
          ;; Blank line at top level — skip.
          ((string= (string-trim '(#\Space #\Tab) first-line) "")
           nil)
          (t
           ;; Accumulate source: single line or multi-line block.
           (let ((source
                  (if (block-starter-p first-line)
                      ;; Multi-line mode: read until a blank line or EOF.
                      (with-output-to-string (buf)
                        (write-string first-line buf)
                        (write-char #\Newline buf)
                        (loop
                          (format t "... ")
                          (force-output)
                          (let ((cont (read-line *standard-input* nil :eof)))
                            (when (or (eq cont :eof)
                                      (string= (string-trim '(#\Space #\Tab) cont) ""))
                              (return))
                            (write-string cont buf)
                            (write-char #\Newline buf))))
                      ;; Single-line mode.
                      first-line)))
             (handler-case
                 ;; Try as expression first (like CPython's eval mode).
                 (multiple-value-bind (result ok) (py-eval-expr source env)
                   (if ok
                       ;; Expression — print result unless None.
                       (unless (eq result clython.runtime:+py-none+)
                         (format t "~A~%" (clython.runtime:py-repr result)))
                       ;; Statement(s) — execute in current env.
                       (py-eval source env)))
               (error (e)
                 (format t "Error: ~A~%" e)))))))))
)
