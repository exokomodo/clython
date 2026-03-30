;;;; modules/math.lisp — math built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-math-module ()
  "Create the math built-in module."
  (let ((mod (clython.runtime:make-py-module "math"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))
    ;; Constants
    (setf (gethash "pi" d) (clython.runtime:make-py-float (coerce pi 'double-float)))
    (setf (gethash "e" d) (clython.runtime:make-py-float (exp 1.0d0)))
    (setf (gethash "tau" d) (clython.runtime:make-py-float (* 2.0d0 (coerce pi 'double-float))))
    (setf (gethash "inf" d) (clython.runtime:make-py-float
                              #+sbcl sb-ext:double-float-positive-infinity
                              #-sbcl most-positive-double-float))
    (setf (gethash "nan" d) (clython.runtime:make-py-float
                              #+sbcl (sb-int:with-float-traps-masked (:invalid)
                                       (- sb-ext:double-float-positive-infinity
                                          sb-ext:double-float-positive-infinity))
                              #-sbcl 0.0d0))
    ;; Single-arg functions
    (dolist (pair '((sqrt . cl:sqrt) (sin . cl:sin) (cos . cl:cos) (tan . cl:tan)
                    (asin . cl:asin) (acos . cl:acos) (atan . cl:atan)
                    (exp . cl:exp) (log . cl:log)
                    (floor . cl:floor) (ceil . cl:ceiling)))
      (let ((name (symbol-name (car pair)))
            (fn (cdr pair)))
        (setf (gethash (string-downcase name) d)
              (clython.runtime:make-py-function
               :name (string-downcase name)
               :cl-fn (let ((f fn))  ; capture
                         (lambda (x)
                           (let ((result (funcall f (coerce (clython.runtime:py->cl x) 'double-float))))
                             (if (integerp result)
                                 (clython.runtime:make-py-int result)
                                 (clython.runtime:make-py-float (coerce result 'double-float))))))))))
    ;; fabs
    (setf (gethash "fabs" d)
          (clython.runtime:make-py-function
           :name "fabs"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-float
                     (abs (coerce (clython.runtime:py->cl x) 'double-float))))))
    ;; pow
    (setf (gethash "pow" d) (%math-wrap-2 "pow" #'expt))
    ;; isnan, isinf
    (setf (gethash "isnan" d)
          (clython.runtime:make-py-function
           :name "isnan"
           :cl-fn (lambda (x)
                    (let ((v (coerce (clython.runtime:py->cl x) 'double-float)))
                      (clython.runtime:cl->py #+sbcl (sb-ext:float-nan-p v) #-sbcl nil)))))
    (setf (gethash "isinf" d)
          (clython.runtime:make-py-function
           :name "isinf"
           :cl-fn (lambda (x)
                    (let ((v (coerce (clython.runtime:py->cl x) 'double-float)))
                      (clython.runtime:cl->py #+sbcl (sb-ext:float-infinity-p v) #-sbcl nil)))))
    ;; factorial(n)
    (setf (gethash "factorial" d)
          (clython.runtime:make-py-function
           :name "factorial"
           :cl-fn (lambda (n)
                    (let ((v (clython.runtime:py->cl n)))
                      (when (or (not (integerp v)) (< v 0))
                        (clython.runtime:py-raise "ValueError"
                          "factorial() only accepts integral values >= 0"))
                      (clython.runtime:make-py-int
                       (loop for i from 1 to v
                             for acc = 1 then (* acc i)
                             finally (return (if (zerop v) 1 acc))))))))
    ;; gcd(a, b)
    (setf (gethash "gcd" d)
          (clython.runtime:make-py-function
           :name "gcd"
           :cl-fn (lambda (&rest args)
                    (cond
                      ((null args) (clython.runtime:make-py-int 0))
                      ((= (length args) 1)
                       (clython.runtime:make-py-int (abs (clython.runtime:py->cl (first args)))))
                      (t (clython.runtime:make-py-int
                          (reduce #'gcd (mapcar (lambda (x) (abs (clython.runtime:py->cl x))) args))))))))
    ;; lcm(a, b)
    (setf (gethash "lcm" d)
          (clython.runtime:make-py-function
           :name "lcm"
           :cl-fn (lambda (&rest args)
                    (flet ((lcm2 (a b)
                             (if (or (zerop a) (zerop b)) 0
                                 (/ (abs (* a b)) (gcd a b)))))
                      (if (null args)
                          (clython.runtime:make-py-int 1)
                          (clython.runtime:make-py-int
                           (reduce #'lcm2 (mapcar (lambda (x) (abs (clython.runtime:py->cl x))) args))))))))
    ;; trunc(x)
    (setf (gethash "trunc" d)
          (clython.runtime:make-py-function
           :name "trunc"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-int
                     (truncate (clython.runtime:py->cl x))))))
    ;; degrees / radians
    (setf (gethash "degrees" d)
          (clython.runtime:make-py-function
           :name "degrees"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-float
                     (* (coerce (clython.runtime:py->cl x) 'double-float)
                        (/ 180.0d0 (coerce pi 'double-float)))))))
    (setf (gethash "radians" d)
          (clython.runtime:make-py-function
           :name "radians"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-float
                     (* (coerce (clython.runtime:py->cl x) 'double-float)
                        (/ (coerce pi 'double-float) 180.0d0))))))
    ;; Module metadata
    (setf (gethash "__name__" d) (clython.runtime:make-py-str "math"))
    mod))

;;; asyncio module -----------------------------------------------------------

