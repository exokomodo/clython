;;;; modules/itertools.lisp — itertools built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-itertools-module ()
  "Create an itertools module with common functions."
  (let ((mod (clython.runtime:make-py-module "itertools")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "itertools"))
    ;; islice(iterable, [start,] stop [, step])
    (setf (gethash "islice" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "islice"
           :cl-fn (lambda (&rest args)
                    (let* ((iterable (first args))
                           (rest-args (rest args))
                           (start (if (>= (length rest-args) 2)
                                      (clython.runtime:py->cl (first rest-args)) 0))
                           (stop  (if rest-args
                                      (clython.runtime:py->cl
                                       (if (>= (length rest-args) 2)
                                           (second rest-args) (first rest-args)))
                                      nil))
                           (step  (if (>= (length rest-args) 3)
                                      (clython.runtime:py->cl (third rest-args)) 1))
                           (it (clython.runtime:py-iter iterable))
                           (result nil) (i 0))
                      (block done
                        (handler-bind
                            ((clython.runtime:stop-iteration
                              (lambda (c) (declare (ignore c)) (return-from done)))
                             (clython.runtime:py-exception
                              (lambda (c)
                                (let ((v (clython.runtime:py-exception-value c)))
                                  (when (and (typep v 'clython.runtime:py-exception-object)
                                             (string= (clython.runtime:py-exception-class-name v) "StopIteration"))
                                    (return-from done))))))
                          (loop
                            (when (and stop (>= i stop)) (return-from done))
                            (let ((item (clython.runtime:py-next it)))
                              (when (and (>= i start)
                                         (zerop (mod (- i start) (max 1 step))))
                                (push item result))
                              (incf i)))))
                      (clython.runtime:make-py-list
                       (coerce (nreverse result) 'vector))))))
    ;; chain(*iterables)
    (setf (gethash "chain" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "chain"
           :cl-fn (lambda (&rest args)
                    (let ((result nil))
                      (dolist (arg args)
                        (cond
                          ((typep arg 'clython.runtime:py-list)
                           (loop for item across (clython.runtime:py-list-value arg)
                                 do (push item result)))
                          ((typep arg 'clython.runtime:py-tuple)
                           (loop for item across (clython.runtime:py-tuple-value arg)
                                 do (push item result)))))
                      (clython.runtime:make-py-list (nreverse result))))))
    ;; count(start=0, step=1) — returns a generator; stub returns a list
    (setf (gethash "count" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "count"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    clython.runtime:+py-none+)))
    ;; repeat(obj, times=None)
    (setf (gethash "repeat" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "repeat"
           :cl-fn (lambda (&rest args)
                    (let* ((obj (first args))
                           (times (if (second args)
                                      (clython.runtime:py->cl (second args))
                                      nil)))
                      (if times
                          (clython.runtime:make-py-list
                           (loop repeat times collect obj))
                          clython.runtime:+py-none+)))))
    mod))

;;;; ─── re module ──────────────────────────────────────────────────────────────

