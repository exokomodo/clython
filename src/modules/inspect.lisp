;;;; modules/inspect.lisp — inspect built-in module stub
;;;;
;;;; Implements the subset of inspect used by the conformance suite.

(in-package :clython.imports)

(defun make-inspect-module ()
  "Create an inspect module with iscoroutinefunction and basic predicates."
  (let ((mod (clython.runtime:make-py-module "inspect")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "inspect"))

      ;; iscoroutinefunction(obj) — True if obj is an async def function
      (setf (gethash "iscoroutinefunction" d)
            (clython.runtime:make-py-function
             :name "iscoroutinefunction"
             :cl-fn (lambda (obj &rest _)
                      (declare (ignore _))
                      (clython.runtime:py-bool-from-cl
                       (and (typep obj 'clython.runtime:py-function)
                            (clython.runtime:py-function-async-p obj))))))

      ;; isfunction(obj) — True if obj is a Python function (sync or async)
      (setf (gethash "isfunction" d)
            (clython.runtime:make-py-function
             :name "isfunction"
             :cl-fn (lambda (obj &rest _)
                      (declare (ignore _))
                      (clython.runtime:py-bool-from-cl
                       (typep obj 'clython.runtime:py-function)))))

      ;; isclass(obj) — True if obj is a class (py-type)
      (setf (gethash "isclass" d)
            (clython.runtime:make-py-function
             :name "isclass"
             :cl-fn (lambda (obj &rest _)
                      (declare (ignore _))
                      (clython.runtime:py-bool-from-cl
                       (typep obj 'clython.runtime:py-type)))))

      ;; ismethod(obj) — True if obj is a bound method
      (setf (gethash "ismethod" d)
            (clython.runtime:make-py-function
             :name "ismethod"
             :cl-fn (lambda (obj &rest _)
                      (declare (ignore _))
                      (clython.runtime:py-bool-from-cl
                       (typep obj 'clython.runtime:py-method)))))

      ;; ismodule(obj) — True if obj is a module
      (setf (gethash "ismodule" d)
            (clython.runtime:make-py-function
             :name "ismodule"
             :cl-fn (lambda (obj &rest _)
                      (declare (ignore _))
                      (clython.runtime:py-bool-from-cl
                       (typep obj 'clython.runtime:py-module))))))
    mod))
