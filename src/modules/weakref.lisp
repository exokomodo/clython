;;;; modules/weakref.lisp — weakref built-in module

(in-package :clython.imports)

;;; ─── weakref.ref ────────────────────────────────────────────────────────────

(defun make-weakref-module ()
  "Create the weakref module with weakref.ref support."
  (let ((mod (clython.runtime:make-py-module "weakref"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))

    ;; weakref.ref(object[, callback]) — returns a callable weak reference
    ;; Uses SBCL's sb-ext:make-weak-pointer for real GC-aware weak refs.
    (setf (gethash "ref" d)
          (clython.runtime:make-py-function
           :name "ref"
           :cl-fn (lambda (obj &rest _callback)
                    (declare (ignore _callback))
                    (let* ((wp (sb-ext:make-weak-pointer obj))
                           (d (make-hash-table :test #'equal))
                           (ref-instance (make-instance 'clython.runtime:py-object
                                                        :py-dict d)))
                      ;; Store the weak pointer; py-call on py-object checks this slot.
                      (setf (gethash "__weakref_wp__" d) wp)
                      (setf (gethash "__class_name__" d)
                            (clython.runtime:make-py-str "weakref"))
                      ref-instance))))

    ;; weakref.proxy(object) — simplified: return the object directly
    (setf (gethash "proxy" d)
          (clython.runtime:make-py-function
           :name "proxy"
           :cl-fn (lambda (obj &rest _) (declare (ignore _)) obj)))

    ;; weakref.WeakValueDictionary — stub type
    (setf (gethash "WeakValueDictionary" d)
          (clython.runtime:make-py-type :name "WeakValueDictionary"))

    (setf (gethash "__name__" d) (clython.runtime:make-py-str "weakref"))
    mod))
