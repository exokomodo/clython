;;;; modules/asyncio.lisp — asyncio built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-asyncio-module ()
  "Create a minimal asyncio module with run() for driving coroutines."
  (let ((mod (clython.runtime:make-py-module "asyncio"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))
    ;; asyncio.run(coro) — runs a coroutine to completion
    (setf (gethash "run" d)
          (clython.runtime:make-py-function
           :name "run"
           :cl-fn (lambda (coro)
                    (if (typep coro 'clython.runtime:py-coroutine)
                        (clython.runtime:py-coroutine-run coro)
                        ;; If not a coroutine, just return it (matches CPython behavior for non-coro)
                        (clython.runtime:py-raise "TypeError"
                                                  "asyncio.run() requires a coroutine object")))))
    ;; asyncio.iscoroutine(obj)
    (setf (gethash "iscoroutine" d)
          (clython.runtime:make-py-function
           :name "iscoroutine"
           :cl-fn (lambda (obj)
                    (if (typep obj 'clython.runtime:py-coroutine)
                        clython.runtime:+py-true+
                        clython.runtime:+py-false+))))
    ;; asyncio.iscoroutinefunction(obj)
    (setf (gethash "iscoroutinefunction" d)
          (clython.runtime:make-py-function
           :name "iscoroutinefunction"
           :cl-fn (lambda (obj)
                    (if (and (typep obj 'clython.runtime:py-function)
                             (clython.runtime:py-function-async-p obj))
                        clython.runtime:+py-true+
                        clython.runtime:+py-false+))))
    ;; asyncio.sleep(seconds) — in synchronous mode, returns a coroutine that resolves to None
    (setf (gethash "sleep" d)
          (clython.runtime:make-py-function
           :name "sleep"
           :cl-fn (lambda (seconds)
                    (declare (ignore seconds))
                    ;; Return a coroutine that resolves to None (no actual sleeping in sync mode)
                    (clython.runtime:make-py-coroutine
                     (lambda () clython.runtime:+py-none+)))
           :async-p t))
    ;; asyncio.gather(*coros) — run all coroutines, return list of results
    (setf (gethash "gather" d)
          (clython.runtime:make-py-function
           :name "gather"
           :cl-fn (lambda (&rest coros)
                    (clython.runtime:make-py-coroutine
                     (lambda ()
                       (clython.runtime:make-py-list
                        (mapcar (lambda (c)
                                  (if (typep c 'clython.runtime:py-coroutine)
                                      (clython.runtime:py-coroutine-run c)
                                      c))
                                coros)))))
           :async-p t))
    ;; asyncio.create_task(coro) — wrap a coroutine in a Task-like object
    ;; In our synchronous model this just runs the coroutine immediately and
    ;; wraps the result in a done Task so `await task` returns the value.
    (setf (gethash "create_task" d)
          (clython.runtime:make-py-function
           :name "create_task"
           :cl-fn (lambda (coro &rest _)
                    (declare (ignore _))
                    ;; Run the coroutine now, stash result in a Task
                    (let* ((result (if (typep coro 'clython.runtime:py-coroutine)
                                      (clython.runtime:py-coroutine-run coro)
                                      coro))
                           (task (clython.runtime:make-py-coroutine
                                  (lambda () result))))
                      ;; Pre-mark as done so repeated await returns the cached result
                      (setf (clython.runtime:py-coroutine-finished task) t)
                      (setf (clython.runtime:py-coroutine-result task) result)
                      task))))
    ;; asyncio.get_event_loop() — stub returning a minimal loop object
    (setf (gethash "get_event_loop" d)
          (clython.runtime:make-py-function
           :name "get_event_loop"
           :cl-fn (lambda (&rest _) (declare (ignore _)) clython.runtime:+py-none+)))
    ;; asyncio.ensure_future(coro) — alias for create_task
    (let ((ct-fn (gethash "create_task" d)))
      (setf (gethash "ensure_future" d) ct-fn))
    ;; asyncio.Task class stub
    (setf (gethash "Task" d)
          (clython.runtime:make-py-type :name "Task"))
    ;; Module metadata
    (setf (gethash "__name__" d) (clython.runtime:make-py-str "asyncio"))
    mod))

;;; ─── os module ──────────────────────────────────────────────────────────────

