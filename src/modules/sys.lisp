;;;; modules/sys.lisp — sys built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-sys-path-list ()
  "Create a py-list from *sys-path*."
  (clython.runtime:make-py-list
   (mapcar #'clython.runtime:make-py-str *sys-path*)))

(defun make-stdout-write ()
  "Create a write function for sys.stdout."
  (clython.runtime:make-py-function
   :name "write"
   :cl-fn (lambda (text)
            (let ((s (clython.runtime:py-str-value text)))
              (write-string s *standard-output*)
              (clython.runtime:make-py-int (length s))))))

(defun make-stderr-write ()
  "Create a write function for sys.stderr."
  (clython.runtime:make-py-function
   :name "write"
   :cl-fn (lambda (text)
            (let ((s (clython.runtime:py-str-value text)))
              (write-string s *error-output*)
              (clython.runtime:make-py-int (length s))))))

(defun make-stdout-object ()
  "Create a minimal sys.stdout object."
  (let ((mod (clython.runtime:make-py-module "<stdout>")))
    (setf (gethash "write" (clython.runtime:py-module-dict mod)) (make-stdout-write))
    (setf (gethash "flush" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "flush"
           :cl-fn (lambda () (force-output *standard-output*) clython.runtime:+py-none+)))
    mod))

(defun make-stderr-object ()
  "Create a minimal sys.stderr object."
  (let ((mod (clython.runtime:make-py-module "<stderr>")))
    (setf (gethash "write" (clython.runtime:py-module-dict mod)) (make-stderr-write))
    (setf (gethash "flush" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "flush"
           :cl-fn (lambda () (force-output *error-output*) clython.runtime:+py-none+)))
    mod))

(defun make-sys-module ()
  "Create the sys built-in module."
  (let ((mod (clython.runtime:make-py-module "sys")))
    (setf (gethash "path" (clython.runtime:py-module-dict mod)) (make-sys-path-list))
    ;; sys.modules — live view over *module-registry*
    ;; Use a py-object whose __getitem__/__contains__ proxy the registry.
    (let* ((sys-modules-type (clython.runtime:make-py-type :name "sys.modules"))
           (sys-mod-obj (make-instance 'clython.runtime:py-object
                                       :py-class sys-modules-type
                                       :py-dict (make-hash-table :test #'equal))))
      (setf (gethash "__getitem__" (clython.runtime:py-object-dict sys-mod-obj))
            (clython.runtime:make-py-function
             :name "__getitem__"
             :cl-fn (lambda (key)
                      (let ((k (clython.runtime:py-str-value key)))
                        (multiple-value-bind (v found) (gethash k *module-registry*)
                          (if found v
                              (clython.runtime:py-raise "KeyError" "~A" k)))))))
      (setf (gethash "__contains__" (clython.runtime:py-object-dict sys-mod-obj))
            (clython.runtime:make-py-function
             :name "__contains__"
             :cl-fn (lambda (key)
                      (let ((k (if (typep key 'clython.runtime:py-str)
                                   (clython.runtime:py-str-value key)
                                   (clython.runtime:py-str-of key))))
                        (if (gethash k *module-registry*)
                            clython.runtime:+py-true+
                            clython.runtime:+py-false+)))))
      (setf (gethash "__setitem__" (clython.runtime:py-object-dict sys-mod-obj))
            (clython.runtime:make-py-function
             :name "__setitem__"
             :cl-fn (lambda (key val)
                      (setf (gethash (clython.runtime:py-str-value key) *module-registry*) val)
                      clython.runtime:+py-none+)))
      (setf (gethash "modules" (clython.runtime:py-module-dict mod)) sys-mod-obj))
    (setf (gethash "version" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "3.12.0 (clython)"))
    (setf (gethash "version_info" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-tuple
           (list (clython.runtime:make-py-int 3)
                 (clython.runtime:make-py-int 12)
                 (clython.runtime:make-py-int 0)
                 (clython.runtime:make-py-str "final")
                 (clython.runtime:make-py-int 0))))
    (setf (gethash "platform" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "linux"))
    (setf (gethash "argv" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-list))
    (setf (gethash "maxsize" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-int (1- (expt 2 63))))
    (setf (gethash "stdout" (clython.runtime:py-module-dict mod)) (make-stdout-object))
    (setf (gethash "stderr" (clython.runtime:py-module-dict mod)) (make-stderr-object))
    (setf (gethash "stdin" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-module "<stdin>"))
    (setf (gethash "exit" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "exit"
           :cl-fn (lambda (&optional code)
                    (let ((rc (if code
                                 (if (typep code 'clython.runtime:py-int)
                                     (clython.runtime:py-int-value code)
                                     0)
                                 0)))
                      (sb-ext:exit :code rc)))))
    (setf (gethash "executable" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "clython"))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "sys"))
    mod))

