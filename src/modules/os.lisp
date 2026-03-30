;;;; modules/os.lisp — os built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-os-path-module ()
  "Create a stub os.path module with join."
  (let ((mod (clython.runtime:make-py-module "os.path")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "os.path"))
    ;; os.path.join(*parts)
    (setf (gethash "join" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "join"
           :cl-fn (lambda (&rest parts)
                    (clython.runtime:make-py-str
                     (format nil "~{~A~^/~}"
                             (mapcar #'clython.runtime:py->cl parts))))))
    ;; os.path.exists(path) — stub returns False
    (setf (gethash "exists" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "exists"
           :cl-fn (lambda (p) (declare (ignore p)) clython.runtime:+py-false+)))
    mod))

(defun make-os-module ()
  "Create a stub os module."
  (let ((mod (clython.runtime:make-py-module "os")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "os"))
    ;; os.path submodule
    (let ((path-mod (make-os-path-module)))
      (setf (gethash "path" (clython.runtime:py-module-dict mod)) path-mod)
      ;; Also register os.path in the module registry
      (setf (gethash "os.path" *module-registry*) path-mod))
    ;; os.getcwd()
    (setf (gethash "getcwd" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "getcwd"
           :cl-fn (lambda ()
                    (clython.runtime:make-py-str
                     (namestring (uiop:getcwd))))))
    ;; os.sep
    (setf (gethash "sep" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "/"))
    mod))

;;; ─── json module ────────────────────────────────────────────────────────────

