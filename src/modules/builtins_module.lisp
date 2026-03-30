;;;; modules/builtins_module.lisp — builtins-module built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-builtins-module ()
  "Create the builtins module referencing our builtins."
  (let ((mod (clython.runtime:make-py-module "builtins")))
    ;; Copy all builtins into the module dict
    (maphash (lambda (name fn)
               (setf (gethash name (clython.runtime:py-module-dict mod)) fn))
             clython.builtins:*builtins*)
    (setf (gethash "True" (clython.runtime:py-module-dict mod)) clython.runtime:+py-true+)
    (setf (gethash "False" (clython.runtime:py-module-dict mod)) clython.runtime:+py-false+)
    (setf (gethash "None" (clython.runtime:py-module-dict mod)) clython.runtime:+py-none+)
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "builtins"))
    mod))

