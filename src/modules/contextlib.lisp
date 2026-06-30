;;;; modules/contextlib.lisp — contextlib built-in module
;;;;
;;;; Implements contextlib.contextmanager and contextlib.suppress.
;;;; Part of Clython's built-in module registry.

(in-package :clython.imports)

;;; ─── _GeneratorContextManager ───────────────────────────────────────────────
;;;
;;; Python contextlib.contextmanager wraps a generator function so it can be
;;; used as a context manager.  The protocol is:
;;;
;;;   __enter__  →  advance the generator to its first yield, return yielded value
;;;   __exit__   →  if no exception, call next(gen) to let it clean up (should
;;;                 raise StopIteration); if an exception, throw it into the gen
;;;
;;; We implement this as a py-object whose instance dict holds the __enter__
;;; and __exit__ CL functions (as py-function cl-fn wrappers).

(defun %make-generator-context-manager (gen)
  "Create a context manager object that drives generator GEN."
  (let ((ctx (make-instance 'clython.runtime:py-object)))
    ;; Give it an instance dict
    (setf (clython.runtime:py-object-dict ctx) (make-hash-table :test #'equal))
    ;; __enter__: advance to first yield
    (setf (gethash "__enter__" (clython.runtime:py-object-dict ctx))
          (clython.runtime:make-py-function
           :name "__enter__"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    ;; Call next(gen) — advances to first yield
                    (handler-case
                        (clython.runtime:py-next gen)
                      (clython.runtime:stop-iteration ()
                        (clython.runtime:py-raise "RuntimeError"
                                                  "generator didn't yield"))))))
    ;; __exit__(exc_type, exc_val, exc_tb)
    (setf (gethash "__exit__" (clython.runtime:py-object-dict ctx))
          (clython.runtime:make-py-function
           :name "__exit__"
           :cl-fn (lambda (&rest args)
                    (let ((exc-type (first args))
                          (_exc-val (second args))
                          (_exc-tb  (third args)))
                      (declare (ignore _exc-val _exc-tb))
                      (if (or (null exc-type)
                              (eq exc-type clython.runtime:+py-none+))
                          ;; Normal exit — resume generator (it should raise StopIteration)
                          (progn
                            (handler-case
                                (progn
                                  (clython.runtime:py-next gen)
                                  ;; Generator yielded again — that's a bug
                                  (clython.runtime:py-raise "RuntimeError"
                                                            "generator didn't stop"))
                              (clython.runtime:stop-iteration ()
                                ;; Expected — generator is done
                                clython.runtime:+py-false+)))
                          ;; Exception exit — we don't have throw() yet, just
                          ;; try to advance; if gen is done, don't suppress
                          (progn
                            (handler-case
                                (progn
                                  (clython.runtime:py-next gen)
                                  ;; Generator yielded again without re-raising
                                  (clython.runtime:py-raise "RuntimeError"
                                                            "generator didn't stop after throw()"))
                              (clython.runtime:stop-iteration ()
                                ;; Generator finished — don't suppress the exception
                                clython.runtime:+py-false+)
                              (error ()
                                ;; Generator itself raised — don't suppress
                                clython.runtime:+py-false+))))))))
    ctx))

(defun make-contextlib-module ()
  "Create the contextlib module with contextmanager and suppress."
  (let ((mod (clython.runtime:make-py-module "contextlib")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "contextlib"))

    ;; contextmanager(fn) — decorator that wraps a generator function
    (setf (gethash "contextmanager" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "contextmanager"
           :cl-fn (lambda (&rest args)
                    (let ((gen-fn (first args)))
                      ;; Return a new function that, when called, creates the ctx mgr
                      (clython.runtime:make-py-function
                       :name (if (typep gen-fn 'clython.runtime:py-function)
                                 (clython.runtime:py-function-name gen-fn)
                                 "contextmanager_wrapper")
                       :cl-fn (lambda (&rest call-args)
                                (let ((gen (clython.runtime:py-call gen-fn call-args)))
                                  (%make-generator-context-manager gen))))))))

    ;; suppress(*exc_types) — context manager that suppresses listed exceptions
    (setf (gethash "suppress" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "suppress"
           :cl-fn (lambda (&rest exc-types)
                    (let ((ctx (make-instance 'clython.runtime:py-object)))
                      (setf (clython.runtime:py-object-dict ctx)
                            (make-hash-table :test #'equal))
                      (setf (gethash "__enter__" (clython.runtime:py-object-dict ctx))
                            (clython.runtime:make-py-function
                             :name "__enter__"
                             :cl-fn (lambda (&rest a)
                                      (declare (ignore a))
                                      clython.runtime:+py-none+)))
                      (setf (gethash "__exit__" (clython.runtime:py-object-dict ctx))
                            (clython.runtime:make-py-function
                             :name "__exit__"
                             :cl-fn (lambda (&rest a)
                                      (let ((exc-type (first a)))
                                        (if (or (null exc-type)
                                                (eq exc-type clython.runtime:+py-none+))
                                            clython.runtime:+py-false+
                                            ;; Suppress if exc matches any listed type
                                            (if (some (lambda (et)
                                                        (and (typep et 'clython.runtime:py-type)
                                                             (typep exc-type 'clython.runtime:py-type)
                                                             (string= (clython.runtime:py-type-name et)
                                                                      (clython.runtime:py-type-name exc-type))))
                                                      exc-types)
                                                clython.runtime:+py-true+
                                                clython.runtime:+py-false+))))))
                      ctx))))

    ;; nullcontext() — a no-op context manager
    (setf (gethash "nullcontext" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "nullcontext"
           :cl-fn (lambda (&rest args)
                    (let ((enter-result (if args (first args) clython.runtime:+py-none+))
                          (ctx (make-instance 'clython.runtime:py-object)))
                      (setf (clython.runtime:py-object-dict ctx)
                            (make-hash-table :test #'equal))
                      (setf (gethash "__enter__" (clython.runtime:py-object-dict ctx))
                            (clython.runtime:make-py-function
                             :name "__enter__"
                             :cl-fn (lambda (&rest a)
                                      (declare (ignore a))
                                      enter-result)))
                      (setf (gethash "__exit__" (clython.runtime:py-object-dict ctx))
                            (clython.runtime:make-py-function
                             :name "__exit__"
                             :cl-fn (lambda (&rest a)
                                      (declare (ignore a))
                                      clython.runtime:+py-false+)))
                      ctx))))

    mod))
