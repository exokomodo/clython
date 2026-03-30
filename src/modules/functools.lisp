;;;; modules/functools.lisp — functools built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-functools-module ()
  "Create a functools module."
  (let ((mod (clython.runtime:make-py-module "functools")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "functools"))
    ;; wraps — identity decorator
    (setf (gethash "wraps" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "wraps"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-function
                     :name "wraps_inner"
                     :cl-fn (lambda (&rest inner) (first inner))))))
    ;; lru_cache — identity decorator
    (setf (gethash "lru_cache" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "lru_cache"
           :cl-fn (lambda (&rest args)
                    (if (and args (typep (first args) 'clython.runtime:py-function))
                        (first args)
                        (clython.runtime:make-py-function
                         :name "lru_cache_inner"
                         :cl-fn (lambda (&rest dargs) (first dargs)))))))
    ;; reduce(fn, seq[, initial])
    (setf (gethash "reduce" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "reduce"
           :cl-fn (lambda (&rest args)
                    (let* ((fn   (first args))
                           (seq  (second args))
                           (init (third args))
                           (items (cond
                                    ((typep seq 'clython.runtime:py-list)
                                     (coerce (clython.runtime:py-list-value seq) 'list))
                                    ((typep seq 'clython.runtime:py-tuple)
                                     (coerce (clython.runtime:py-tuple-value seq) 'list))
                                    (t nil)))
                           (acc init))
                      (dolist (item items)
                        (if acc
                            (setf acc (clython.runtime:py-call fn acc item))
                            (setf acc item)))
                      (or acc clython.runtime:+py-none+)))))
    ;; partial(fn, *args, **kwargs) — returns a partial application
    (setf (gethash "partial" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "partial"
           :cl-fn (lambda (&rest args)
                    (let ((fn (first args))
                          (bound-args (rest args)))
                      (clython.runtime:make-py-function
                       :name "partial"
                       :cl-fn (lambda (&rest call-args)
                                (apply #'clython.runtime:py-call fn
                                       (append bound-args call-args))))))))
    mod))

;;;; ─── io module ─────────────────────────────────────────────────────────────

