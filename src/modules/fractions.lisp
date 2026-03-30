;;;; modules/fractions.lisp — fractions built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-fractions-module ()
  "Create a stub fractions module with Fraction class."
  (let* ((mod (clython.runtime:make-py-module "fractions"))
         (fraction-type (clython.runtime:make-py-type
                         :name "Fraction" :bases nil :tdict (make-hash-table :test #'equal))))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "fractions"))
    ;; __str__ for Fraction: "numerator/denominator"
    (setf (gethash "__str__" (clython.runtime:py-type-dict fraction-type))
          (clython.runtime:make-py-function
           :name "__str__"
           :cl-fn (lambda (self)
                    (let ((v (gethash "_value" (clython.runtime:py-object-dict self))))
                      (clython.runtime:make-py-str
                       (format nil "~D/~D" (numerator v) (denominator v)))))))
    ;; Fraction(num, den) constructor
    (setf (gethash "Fraction" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "Fraction"
           :cl-fn (lambda (num &optional den)
                    (let* ((n (clython.runtime:py->cl num))
                           (d (if den (clython.runtime:py->cl den) 1))
                           (obj (make-instance 'clython.runtime:py-object :py-class fraction-type :py-dict (make-hash-table :test #'equal))))
                      (setf (gethash "_value" (clython.runtime:py-object-dict obj))
                            (/ n d))
                      obj))))
    mod))

;;; ─── collections module ─────────────────────────────────────────────────────

