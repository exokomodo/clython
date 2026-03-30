;;;; modules/io.lisp — io built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-io-module ()
  "Create an io module with StringIO."
  (let ((mod (clython.runtime:make-py-module "io"))
        (stringio-type (clython.runtime:make-py-type :name "StringIO")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "io"))
    ;; StringIO([initial_value])
    (setf (gethash "StringIO" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "StringIO"
           :cl-fn (lambda (&rest args)
                    (let* ((initial (if args (clython.runtime:py-str-value (first args)) ""))
                           (buf (make-array (length initial)
                                            :element-type 'character
                                            :fill-pointer (length initial)
                                            :adjustable t
                                            :initial-contents initial))
                           (obj (make-instance 'clython.runtime:py-object
                                               :py-class stringio-type
                                               :py-dict (make-hash-table :test #'equal))))
                      (setf (gethash "_buf" (clython.runtime:py-object-dict obj)) buf)
                      ;; write(s)
                      (setf (gethash "write" (clython.runtime:py-object-dict obj))
                            (clython.runtime:make-py-function
                             :name "write"
                             :cl-fn (lambda (s)
                                      (let ((text (clython.runtime:py-str-value s)))
                                        (loop for ch across text do (vector-push-extend ch buf))
                                        (clython.runtime:make-py-int (length text))))))
                      ;; getvalue()
                      (setf (gethash "getvalue" (clython.runtime:py-object-dict obj))
                            (clython.runtime:make-py-function
                             :name "getvalue"
                             :cl-fn (lambda () (clython.runtime:make-py-str (coerce buf 'string)))))
                      ;; __enter__ / __exit__ for with statement
                      (setf (gethash "__enter__" (clython.runtime:py-object-dict obj))
                            (clython.runtime:make-py-function
                             :name "__enter__" :cl-fn (lambda () obj)))
                      (setf (gethash "__exit__" (clython.runtime:py-object-dict obj))
                            (clython.runtime:make-py-function
                             :name "__exit__"
                             :cl-fn (lambda (&rest _) (declare (ignore _))
                                      clython.runtime:+py-none+)))
                      obj))))
    mod))

;;;; ─── random module ────────────────────────────────────────────────────────

