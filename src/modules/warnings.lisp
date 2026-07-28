;;;; ─── warnings module ───────────────────────────────────────────────────────

(in-package :clython.imports)

(defun make-warnings-module ()
  "Create a stub warnings module that silently accepts warn/filter calls."
  (let ((mod (clython.runtime:make-py-module "warnings")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "warnings"))
    ;; warn(message, category=UserWarning, stacklevel=1, source=None) — silently ignore
    (setf (gethash "warn" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "warn"
           :cl-fn (lambda (&rest _args)
                    (declare (ignore _args))
                    clython.runtime:+py-none+)))
    ;; filterwarnings(action, ...) — accept and ignore
    (setf (gethash "filterwarnings" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "filterwarnings"
           :cl-fn (lambda (&rest _args)
                    (declare (ignore _args))
                    clython.runtime:+py-none+)))
    ;; simplefilter(action, ...) — accept and ignore
    (setf (gethash "simplefilter" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "simplefilter"
           :cl-fn (lambda (&rest _args)
                    (declare (ignore _args))
                    clython.runtime:+py-none+)))
    mod))
