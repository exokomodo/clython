;;;; modules/copyreg.lisp — copyreg stub module for Clython
;;;;
;;;; Provides the minimal copyreg interface needed for pickle to load.
;;;; dispatch_table is an empty dict (no C-extension types to register).

(in-package :clython.imports)

(defun make-copyreg-module ()
  "Create the copyreg module stub."
  (let ((mod (clython.runtime:make-py-module "copyreg"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))

    ;; dispatch_table: dict mapping type -> reduce function
    ;; Empty by default (no C extension types in Clython).
    (setf (gethash "dispatch_table" d)
          (clython.runtime:make-py-dict nil))

    ;; copyreg.pickle(ob_type, pickle_function, constructor_ob=None)
    ;; Registers a reduce function for ob_type. We store in dispatch_table.
    (setf (gethash "pickle" d)
          (clython.runtime:make-py-function
           :name "pickle"
           :cl-fn (lambda (ob-type pickle-fn &rest _constructor)
                    (declare (ignore _constructor))
                    (let ((dt (gethash "dispatch_table" d)))
                      (setf (gethash ob-type
                                     (clython.runtime:py-dict-value dt))
                            pickle-fn))
                    clython.runtime:+py-none+)))

    ;; copyreg.constructor(object) — registers a constructor (no-op for us)
    (setf (gethash "constructor" d)
          (clython.runtime:make-py-function
           :name "constructor"
           :cl-fn (lambda (obj &rest _) (declare (ignore obj _)) clython.runtime:+py-none+)))

    ;; add_extension / remove_extension / clear_extension_cache — no-ops
    (dolist (fname '("add_extension" "remove_extension" "clear_extension_cache"))
      (setf (gethash fname d)
            (clython.runtime:make-py-function
             :name fname
             :cl-fn (lambda (&rest _) (declare (ignore _)) clython.runtime:+py-none+))))

    ;; Internal registries used by pickle
    (setf (gethash "_extension_registry" d)
          (clython.runtime:make-py-dict nil))
    (setf (gethash "_inverted_registry" d)
          (clython.runtime:make-py-dict nil))
    (setf (gethash "_extension_cache" d)
          (clython.runtime:make-py-dict nil))

    (setf (gethash "__name__" d) (clython.runtime:make-py-str "copyreg"))
    mod))
