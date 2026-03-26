;;;; clython.lisp — Main entry point for the Clython interpreter

(defpackage :clython
  (:use :cl)
  (:import-from :clython.exceptions #:py-syntax-error)
  (:export #:repl #:py-eval #:py-parse #:py-syntax-error))

(in-package :clython)

(defun py-parse (source)
  "Parse a Python source string and return the AST."
  (let ((tokens (clython.lexer:tokenize source)))
    (handler-case
        (clython.parser:parse-module tokens)
      (clython.parser:parser-error (e)
        (error 'py-syntax-error
               :message (format nil "~A" e))))))

(defun py-eval (source)
  "Evaluate a Python source string. Returns the last expression value (as a py-object)."
  (let* ((ast (py-parse source))
         (env (clython.scope:make-global-env)))
    (clython.eval:eval-node ast env)))

(defun repl ()
  "Start an interactive Clython REPL."
  (format t "Clython 0.1.0 — Python in Common Lisp~%")
  (format t "Type (quit) to exit.~%~%")
  (loop
    (format t ">>> ")
    (force-output)
    (let ((line (read-line *standard-input* nil :eof)))
      (when (or (eq line :eof)
                (string= line "(quit)"))
        (return))
      (unless (string= (string-trim '(#\Space #\Tab) line) "")
        (handler-case
            (let ((result (py-eval line)))
              ;; Print result if it's not None (like Python interactive mode)
              (unless (eq result clython.runtime:+py-none+)
                (format t "~A~%" (clython.runtime:py-repr result))))
          (error (e)
            (format t "Error: ~A~%" e)))))))
