;;;; cli.lisp - Standalone CLI entry point for Clython

(defpackage :clython.cli
  (:use :cl)
  (:export #:main))

(in-package :clython.cli)

(defun main ()
  "CLI entry point for the Clython interpreter binary."
  (let ((args (uiop:command-line-arguments)))
    (cond
      ;; No arguments → REPL
      ((null args)
       (clython:repl))
      ;; -c "source" → evaluate source string
      ((string= (first args) "-c")
       (unless (second args)
         (format *error-output* "clython: argument expected for -c~%")
         (uiop:quit 2))
       (handler-case
           (clython:py-eval (second args))
         (division-by-zero ()
           (format *error-output* "ZeroDivisionError: division by zero~%")
           (uiop:quit 1))
         (error (e)
           (format *error-output* "~A~%" e)
           (uiop:quit 1))))
      ;; --parse-only -c "source" → parse and print AST
      ((string= (first args) "--parse-only")
       (unless (and (string= (second args) "-c") (third args))
         (format *error-output* "Usage: clython --parse-only -c \"source\"~%")
         (uiop:quit 2))
       (handler-case
           (let ((ast (clython:py-parse (third args))))
             (format t "~A~%" ast))
         (error (e)
           (format *error-output* "SyntaxError: ~A~%" e)
           (uiop:quit 2))))
      ;; file.py [args...] → evaluate file with sys.argv populated
      (t
       (let ((filename (first args))
             (script-args (rest args)))
         (unless (probe-file filename)
           (format *error-output* "clython: can't open file '~A': No such file~%" filename)
           (uiop:quit 2))
         ;; Set sys.argv = [filename, arg1, arg2, ...]
         (let ((sys-mod (clython.imports:import-module "sys")))
           (setf (gethash "argv" (clython.runtime:py-module-dict sys-mod))
                 (clython.runtime:make-py-list
                  (mapcar #'clython.runtime:make-py-str
                          (cons filename script-args)))))
         (handler-case
             (let ((source (uiop:read-file-string filename)))
               (clython:py-eval source))
           (error (e)
             (format *error-output* "~A~%" e)
             (uiop:quit 1))))))))	
