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

(defun repl ()
  "Start an interactive Clython REPL."
  (format t "Clython 0.1.0 — Python in Common Lisp~%")
  (format t "Type (quit) to exit.~%~%")
  (let ((env (clython.scope:make-global-env)))
    (loop
      (format t ">>> ")
      (force-output)
      (let ((line (read-line *standard-input* nil :eof)))
        (when (or (eq line :eof)
                  (string= line "(quit)"))
          (return))
        (unless (string= (string-trim '(#\Space #\Tab) line) "")
          (handler-case
              ;; Try as expression first (like CPython's eval mode)
              (multiple-value-bind (result ok) (py-eval-expr line env)
                (if ok
                    ;; Expression — print result unless None
                    (unless (eq result clython.runtime:+py-none+)
                      (format t "~A~%" (clython.runtime:py-repr result)))
                    ;; Not an expression — execute as statements
                    (py-eval line env)))
            (error (e)
              (format t "Error: ~A~%" e))))))))
