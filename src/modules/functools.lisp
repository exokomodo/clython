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
    ;; wraps(wrapped) — returns a decorator that copies metadata from wrapped onto wrapper
    (setf (gethash "wraps" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "wraps"
           :cl-fn (lambda (wrapped &rest _)
                    (declare (ignore _))
                    ;; Return decorator that copies __name__, __doc__, __wrapped__
                    (clython.runtime:make-py-function
                     :name "wraps_decorator"
                     :cl-fn (lambda (wrapper &rest __)
                              (declare (ignore __))
                              ;; Copy name from wrapped onto wrapper
                              (when (typep wrapper 'clython.runtime:py-function)
                                (let ((wname (clython.runtime:py-function-name wrapped)))
                                  (setf (clython.runtime:py-function-name wrapper) wname)))
                              wrapper)))))
    ;; %make-caching-wrapper — wrap a py-function with a hash-table memo cache.
    ;; Exposes cache_info() returning a CacheInfo-like namedtuple-style object
    ;; with hits, misses, maxsize, currsize attributes.
    (flet ((%make-caching-wrapper (fn maxsize)
             (let ((cache-ht (make-hash-table :test #'equal))
                   (hits 0)
                   (misses 0))
               (let ((wrapper
                      (clython.runtime:make-py-function
                       :name (clython.runtime:py-function-name fn)
                       :cl-fn (lambda (&rest args)
                                (let ((key (mapcar (lambda (x) (clython.runtime:py-repr x)) args)))
                                  (multiple-value-bind (cached found)
                                      (gethash key cache-ht)
                                    (if found
                                        (progn (incf hits) cached)
                                        (let ((result (apply #'clython.runtime:py-call fn args)))
                                          (incf misses)
                                          (setf (gethash key cache-ht) result)
                                          result))))))))
                 ;; Attach cache_info() as an attribute on the wrapper function.
                 ;; cache_info() → an object with .hits .misses .maxsize .currsize
                 (let ((info-fn
                        (clython.runtime:make-py-function
                         :name "cache_info"
                         :cl-fn (lambda (&rest _)
                                  (declare (ignore _))
                                  ;; Return as a tuple: (hits, misses, maxsize, currsize)
                                  ;; matching CPython's CacheInfo namedtuple behaviour.
                                  (clython.runtime:make-py-tuple
                                   (vector
                                    (clython.runtime:make-py-int hits)
                                    (clython.runtime:make-py-int misses)
                                    (if maxsize
                                        (clython.runtime:make-py-int maxsize)
                                        clython.runtime:+py-none+)
                                    (clython.runtime:make-py-int (hash-table-count cache-ht))))))))

                   (let ((wdict (make-hash-table :test #'equal)))
                     (setf (gethash "cache_info"  wdict) info-fn)
                     (setf (gethash "cache_clear" wdict)
                           (clython.runtime:make-py-function
                            :name "cache_clear"
                            :cl-fn (lambda (&rest _)
                                     (declare (ignore _))
                                     (clrhash cache-ht)
                                     (setf hits 0)
                                     (setf misses 0)
                                     clython.runtime:+py-none+)))
                     (setf (clython.runtime:py-object-dict wrapper) wdict)))
                 wrapper))))

    ;; lru_cache(maxsize=128) / lru_cache(fn) — memoising decorator
    (setf (gethash "lru_cache" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "lru_cache"
           :cl-fn (lambda (&rest args)
                    (let ((first-arg (first args))
                          ;; Read maxsize from kwargs if present
                          (kw-maxsize (let ((kw (assoc "maxsize" clython.runtime:*current-kwargs* :test #'string=)))
                                        (when (and kw (typep (cdr kw) 'clython.runtime:py-int))
                                          (clython.runtime:py-int-value (cdr kw))))))
                      (cond
                        ;; @lru_cache  (called directly on function, no parentheses)
                        ((typep first-arg 'clython.runtime:py-function)
                         (%make-caching-wrapper first-arg 128))
                        ;; @lru_cache(maxsize=N) or @lru_cache() — return decorator
                        (t
                         (let ((maxsize (or kw-maxsize
                                           (when (and first-arg (typep first-arg 'clython.runtime:py-int))
                                             (clython.runtime:py-int-value first-arg))
                                           128)))
                           (clython.runtime:make-py-function
                            :name "lru_cache_decorator"
                            :cl-fn (lambda (&rest fargs)
                                     (%make-caching-wrapper (first fargs) maxsize))))))))))
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
    ;; cache — alias for lru_cache(maxsize=None), same behaviour
    (setf (gethash "cache" (clython.runtime:py-module-dict mod))
          (gethash "lru_cache" (clython.runtime:py-module-dict mod)))) ; closes flet
    mod))

;;;; ─── io module ─────────────────────────────────────────────────────────────
