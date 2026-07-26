;;;; modules/types.lisp — types built-in module
;;;;
;;;; Provides the common type objects from Python's types module.
;;;; Most are just aliases for the built-in type objects.

(in-package :clython.imports)

(defun make-types-module ()
  "Create a types module with FunctionType, LambdaType, MethodType, etc."
  (let ((mod (clython.runtime:make-py-module "types")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "types"))

      ;; FunctionType / LambdaType — the type of a Python function
      (let ((fn-type (clython.runtime:make-py-type :name "function")))
        (setf (gethash "FunctionType" d) fn-type)
        (setf (gethash "LambdaType" d) fn-type))

      ;; MethodType — the type of a bound method
      (setf (gethash "MethodType" d)
            (clython.runtime:make-py-type :name "method"))

      ;; BuiltinFunctionType / BuiltinMethodType
      (let ((bfn-type (clython.runtime:make-py-type
                       :name "builtin_function_or_method")))
        (setf (gethash "BuiltinFunctionType" d) bfn-type)
        (setf (gethash "BuiltinMethodType" d) bfn-type))

      ;; ModuleType — the type of a module
      (setf (gethash "ModuleType" d)
            (clython.runtime:make-py-type :name "module"))

      ;; NoneType
      (setf (gethash "NoneType" d)
            (clython.runtime:make-py-type :name "NoneType"))

      ;; CodeType / FrameType / GeneratorType / CoroutineType — stubs
      (setf (gethash "CodeType" d)
            (clython.runtime:make-py-type :name "code"))
      (setf (gethash "FrameType" d)
            (clython.runtime:make-py-type :name "frame"))
      (setf (gethash "GeneratorType" d)
            (clython.runtime:make-py-type :name "generator"))
      (setf (gethash "CoroutineType" d)
            (clython.runtime:make-py-type :name "coroutine"))

      ;; SimpleNamespace — simple attribute bag
      (let ((sns-cls (clython.runtime:make-py-type :name "SimpleNamespace")))
        (setf (gethash "__init__" (clython.runtime:py-type-dict sns-cls))
              (clython.runtime:make-py-function
               :name "__init__"
               :cl-fn (lambda (self &rest _)
                         (declare (ignore _ self))
                         clython.runtime:+py-none+)))
        (setf (gethash "SimpleNamespace" d) sns-cls)))
    mod))
