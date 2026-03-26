(defpackage :clython
  (:use :cl)
  (:export #:repl #:py-eval))

(in-package :clython)

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
