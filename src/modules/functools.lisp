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
    ;; total_ordering — class decorator that fills in missing comparison methods.
    ;; Given __eq__ and one of __lt__/__le__/__gt__/__ge__, fills in the rest.
    (setf (gethash "total_ordering" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "total_ordering"
           :cl-fn (lambda (cls)
                    (when (typep cls 'clython.runtime:py-type)
                      (let ((tdict (clython.runtime:py-type-dict cls)))
                        (unless tdict
                          (setf tdict (make-hash-table :test #'equal))
                          (setf (clython.runtime:py-type-dict cls) tdict))
                        (let ((has-lt (nth-value 1 (gethash "__lt__" tdict)))
                              (has-le (nth-value 1 (gethash "__le__" tdict)))
                              (has-gt (nth-value 1 (gethash "__gt__" tdict)))
                              (has-ge (nth-value 1 (gethash "__ge__" tdict))))
                          (cond
                            ;; Based on __lt__: fill in __le__, __gt__, __ge__
                            (has-lt
                             (unless has-le
                               ;; __le__(self, other) = self < other or self == other
                               (setf (gethash "__le__" tdict)
                                     (clython.runtime:make-py-function
                                      :name "__le__"
                                      :cl-fn (lambda (self other)
                                               (clython.runtime:py-bool-from-cl
                                                (or (clython.runtime:py-lt self other)
                                                    (clython.runtime:py-eq self other)))))))
                             (unless has-gt
                               ;; __gt__(self, other) = not (self < other or self == other)
                               (setf (gethash "__gt__" tdict)
                                     (clython.runtime:make-py-function
                                      :name "__gt__"
                                      :cl-fn (lambda (self other)
                                               (clython.runtime:py-bool-from-cl
                                                (not (or (clython.runtime:py-lt self other)
                                                         (clython.runtime:py-eq self other))))))))
                             (unless has-ge
                               ;; __ge__(self, other) = not self < other
                               (setf (gethash "__ge__" tdict)
                                     (clython.runtime:make-py-function
                                      :name "__ge__"
                                      :cl-fn (lambda (self other)
                                               (clython.runtime:py-bool-from-cl
                                                (not (clython.runtime:py-lt self other))))))))
                            ;; Based on __le__: fill in __lt__, __gt__, __ge__
                            (has-le
                             (unless has-lt
                               ;; __lt__(self, other) = self <= other and not self == other
                               (setf (gethash "__lt__" tdict)
                                     (clython.runtime:make-py-function
                                      :name "__lt__"
                                      :cl-fn (lambda (self other)
                                               (clython.runtime:py-bool-from-cl
                                                (and (clython.runtime:py-le self other)
                                                     (not (clython.runtime:py-eq self other))))))))
                             (unless has-gt
                               ;; __gt__(self, other) = not self <= other
                               (setf (gethash "__gt__" tdict)
                                     (clython.runtime:make-py-function
                                      :name "__gt__"
                                      :cl-fn (lambda (self other)
                                               (clython.runtime:py-bool-from-cl
                                                (not (clython.runtime:py-le self other)))))))
                             (unless has-ge
                               ;; __ge__(self, other) = not (self <= other and not self == other)
                               (setf (gethash "__ge__" tdict)
                                     (clython.runtime:make-py-function
                                      :name "__ge__"
                                      :cl-fn (lambda (self other)
                                               (clython.runtime:py-bool-from-cl
                                                (or (not (clython.runtime:py-le self other))
                                                    (clython.runtime:py-eq self other))))))))))))
                    ;; Always return cls (whether we modified it or not)
                    cls)))
    mod))

;;;; ─── io module ─────────────────────────────────────────────────────────────
