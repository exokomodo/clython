(defpackage :clython
  (:use :cl)
  (:export #:repl #:py-eval #:py-parse #:py-syntax-error))

(in-package :clython)

(define-condition py-syntax-error (error)
  ((message :initarg :message :reader py-syntax-error-message))
  (:report (lambda (c stream)
             (format stream "~A" (py-syntax-error-message c)))))

(defun py-parse (source)
  "Parse a Python source string and return the AST."
  (let ((tokens (clython.lexer:tokenize source)))
    (handler-case
        (clython.parser:parse-module tokens)
      (clython.parser:parser-error (e)
        (error 'py-syntax-error
               :message (format nil "~A" e))))))

(defun py-eval (source)
  "Evaluate a Python source string and return the result."
  (declare (ignore source))
  (error "Not yet implemented"))

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
      (handler-case
          (format t "~A~%" (py-eval line))
        (error (e)
          (format t "Error: ~A~%" e))))))
