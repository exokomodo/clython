;;;; modules/decimal.lisp — decimal built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-decimal-module ()
  "Create a stub decimal module with Decimal class."
  (let* ((mod (clython.runtime:make-py-module "decimal"))
         (decimal-type (clython.runtime:make-py-type
                        :name "Decimal" :bases nil :tdict (make-hash-table :test #'equal))))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "decimal"))
    ;; Decimal is implemented as a wrapper around CL rational numbers
    ;; The "class" is actually a constructor function that returns py-objects
    (setf (gethash "Decimal" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "Decimal"
           :cl-fn (lambda (val)
                    (let* ((s (clython.runtime:py->cl val))
                           (r (cond ((stringp s)
                                     (let ((rat (read-from-string s)))
                                       (if (rationalp rat) rat (rationalize rat))))
                                    ((rationalp s) s)
                                    ((numberp s) (rationalize s))
                                    (t 0)))
                           (obj (make-instance 'clython.runtime:py-object :py-class decimal-type :py-dict (make-hash-table :test #'equal))))
                      ;; Store the rational value
                      (setf (gethash "_value" (clython.runtime:py-object-dict obj)) r)
                      ;; __str__ and __repr__
                      (setf (gethash "__str__" (clython.runtime:py-type-dict decimal-type))
                            (clython.runtime:make-py-function
                             :name "__str__"
                             :cl-fn (lambda (self)
                                      (let ((v (gethash "_value" (clython.runtime:py-object-dict self))))
                                        (clython.runtime:make-py-str
                                         (format nil "~F" (coerce v 'double-float)))))))
                      ;; __add__
                      (setf (gethash "__add__" (clython.runtime:py-type-dict decimal-type))
                            (clython.runtime:make-py-function
                             :name "__add__"
                             :cl-fn (lambda (self other)
                                      (let* ((v1 (gethash "_value" (clython.runtime:py-object-dict self)))
                                             (v2 (gethash "_value" (clython.runtime:py-object-dict other)))
                                             (result (+ v1 v2))
                                             (new-obj (make-instance 'clython.runtime:py-object :py-class decimal-type :py-dict (make-hash-table :test #'equal))))
                                        (setf (gethash "_value" (clython.runtime:py-object-dict new-obj)) result)
                                        new-obj))))
                      obj))))
    mod))

;;; ─── fractions module ───────────────────────────────────────────────────────

