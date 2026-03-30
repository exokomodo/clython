;;;; modules/random.lisp — random built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-random-module ()
  "Create a random module with seed, randint, random, choice."
  (let ((mod (clython.runtime:make-py-module "random")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "random"))
    ;; seed(a)
    (setf (gethash "seed" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "seed"
           :cl-fn (lambda (&rest args)
                    (let ((s (if args (clython.runtime:py->cl (first args)) 0)))
                      (setf *random-state* (sb-ext:seed-random-state s)))
                    clython.runtime:+py-none+)))
    ;; randint(a, b)
    (setf (gethash "randint" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "randint"
           :cl-fn (lambda (a b)
                    (let ((lo (clython.runtime:py->cl a))
                          (hi (clython.runtime:py->cl b)))
                      (clython.runtime:make-py-int (+ lo (random (1+ (- hi lo)))))))))
    ;; random()
    (setf (gethash "random" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "random"
           :cl-fn (lambda () (clython.runtime:make-py-float (random 1.0d0)))))
    ;; choice(seq)
    (setf (gethash "choice" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "choice"
           :cl-fn (lambda (seq)
                    (let ((items (cond
                                   ((typep seq 'clython.runtime:py-list)
                                    (clython.runtime:py-list-value seq))
                                   ((typep seq 'clython.runtime:py-tuple)
                                    (clython.runtime:py-tuple-value seq))
                                   (t (error "choice(): unsupported type")))))
                      (aref items (random (length items)))))))
    mod))

