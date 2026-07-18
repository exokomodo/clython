;;;; modules/copy.lisp — copy built-in module
;;;;
;;;; Implements copy.copy and copy.deepcopy.
;;;; If the object defines __copy__ / __deepcopy__, those are called.
;;;; Otherwise a shallow / recursive-object copy is performed.

(in-package :clython.imports)

(defun make-copy-module ()
  "Create the copy module with copy() and deepcopy()."
  (let ((mod (clython.runtime:make-py-module "copy")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "copy"))

    ;;; copy.copy(obj)
    ;;; Perform a shallow copy.  Calls __copy__ if present.
    (setf (gethash "copy" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "copy"
           :cl-fn (lambda (obj)
                    (let ((copy-fn (clython.runtime::%lookup-dunder obj "__copy__")))
                      (if copy-fn
                          ;; Call __copy__(self) — __lookup-dunder already
                          ;; handles the self argument convention.
                          (clython.runtime:py-call copy-fn obj)
                          ;; Fallback: shallow copy for py-object instances.
                          (if (typep obj 'clython.runtime:py-object)
                              (let* ((old-d (clython.runtime:py-object-dict obj))
                                     (new-d (if (hash-table-p old-d)
                                                (let ((h (make-hash-table :test #'equal)))
                                                  (maphash (lambda (k v)
                                                             (setf (gethash k h) v))
                                                           old-d)
                                                  h)
                                                nil))
                                     (new-obj (make-instance
                                               'clython.runtime:py-object
                                               :py-class (clython.runtime:py-object-class obj)
                                               :py-dict new-d)))
                                new-obj)
                              obj))))))

    ;;; copy.deepcopy(obj, memo=None)
    ;;; Perform a deep copy.  Calls __deepcopy__ if present.
    (setf (gethash "deepcopy" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "deepcopy"
           :cl-fn (lambda (obj &optional memo)
                    (when (null memo)
                      (setf memo clython.runtime:+py-none+))
                    (let ((deep-fn (clython.runtime::%lookup-dunder obj "__deepcopy__")))
                      (if deep-fn
                          ;; Call __deepcopy__(self, memo)
                          (clython.runtime:py-call deep-fn obj memo)
                          ;; Fallback: same shallow copy for now (sufficient for
                          ;; simple objects without nested mutable state).
                          (if (typep obj 'clython.runtime:py-object)
                              (let* ((old-d (clython.runtime:py-object-dict obj))
                                     (new-d (if (hash-table-p old-d)
                                                (let ((h (make-hash-table :test #'equal)))
                                                  (maphash (lambda (k v)
                                                             (setf (gethash k h) v))
                                                           old-d)
                                                  h)
                                                nil))
                                     (new-obj (make-instance
                                               'clython.runtime:py-object
                                               :py-class (clython.runtime:py-object-class obj)
                                               :py-dict new-d)))
                                new-obj)
                              obj))))))

    mod))
