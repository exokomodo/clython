;;;; modules/pickle.lisp — minimal native pickle module for Clython
;;;;
;;;; Uses a Clython-internal serialization format (not CPython-compatible).
;;;; Supports: int, str, float, bool, None, bytes, list, tuple, dict,
;;;; and user-defined classes via __getstate__ / __setstate__.

(in-package :clython.imports)

;;; ─── Serialisation ────────────────────────────────────────────────────────

(defun %pickle-to-lisp (obj)
  "Convert a py-object to a Lisp-printable s-expression."
  (cond
    ((eq obj clython.runtime:+py-none+)  '(:none))
    ((eq obj clython.runtime:+py-true+)  '(:bool t))
    ((eq obj clython.runtime:+py-false+) '(:bool nil))
    ((typep obj 'clython.runtime:py-int)
     (list :int (clython.runtime:py-int-value obj)))
    ((typep obj 'clython.runtime:py-float)
     (list :float (clython.runtime:py-float-value obj)))
    ((typep obj 'clython.runtime:py-str)
     (list :str (clython.runtime:py-str-value obj)))
    ((typep obj 'clython.runtime:py-bytes)
     (list :bytes (coerce (clython.runtime:py-bytes-value obj) 'list)))
    ((typep obj 'clython.runtime:py-list)
     (list :list (mapcar #'%pickle-to-lisp
                         (coerce (clython.runtime:py-list-value obj) 'list))))
    ((typep obj 'clython.runtime:py-tuple)
     (list :tuple (mapcar #'%pickle-to-lisp
                          (coerce (clython.runtime:py-tuple-value obj) 'list))))
    ((typep obj 'clython.runtime:py-dict)
     (let (pairs)
       (maphash (lambda (k v)
                  (push (list (%pickle-to-lisp k) (%pickle-to-lisp v)) pairs))
                (clython.runtime:py-dict-value obj))
       (list :dict (nreverse pairs))))
    ((typep obj 'clython.runtime:py-object)
     (let* ((cls (clython.runtime:py-object-class obj))
            (class-name (if (typep cls 'clython.runtime:py-type)
                            (clython.runtime:py-type-name cls)
                            "object"))
            ;; Try __getstate__
            (state (handler-case
                       (let ((gs (clython.runtime:py-getattr obj "__getstate__")))
                         (%pickle-to-lisp (clython.runtime:py-call gs)))
                     (error ()
                       ;; Fall back to instance dict (minus __class__)
                       (let ((d (clython.runtime:py-object-dict obj))
                           pairs)
                       (when d
                         (maphash (lambda (k v)
                                    (push (list (list :str k)
                                                (%pickle-to-lisp v))
                                          pairs))
                                  d))
                       (list :dict (nreverse pairs)))))))
       (list :obj class-name state)))
    (t (list :str (format nil "<unpicklable:~A>" (type-of obj))))))

;;; ─── Deserialisation ──────────────────────────────────────────────────────

(defun %pickle-from-lisp (sexp)
  "Reconstruct a py-object from a serialized s-expression."
  (case (first sexp)
    (:none  clython.runtime:+py-none+)
    (:bool  (if (second sexp) clython.runtime:+py-true+ clython.runtime:+py-false+))
    (:int   (clython.runtime:make-py-int (second sexp)))
    (:float (clython.runtime:make-py-float (second sexp)))
    (:str   (clython.runtime:make-py-str (second sexp)))
    (:bytes (clython.runtime:make-py-bytes
             (coerce (second sexp) '(vector (unsigned-byte 8)))))
    (:list  (clython.runtime:make-py-list
             (mapcar #'%pickle-from-lisp (second sexp))))
    (:tuple (clython.runtime:make-py-tuple
             (coerce (mapcar #'%pickle-from-lisp (second sexp)) 'vector)))
    (:dict  (let ((ht (make-hash-table :test #'equal)))
              (dolist (pair (second sexp))
                (setf (gethash (%pickle-from-lisp (first pair)) ht)
                      (%pickle-from-lisp (second pair))))
              (make-instance 'clython.runtime:py-dict :value ht)))
    (:obj
     (let* ((class-name (second sexp))
            (state-sexp (third sexp))
            (state (%pickle-from-lisp state-sexp))
            (cls (clython.runtime:lookup-py-class class-name))
            (inst (make-instance 'clython.runtime:py-object)))
       ;; Attach the class via the slot
       (when cls
         (setf (clython.runtime:py-object-class inst) cls))
       ;; Restore state via __setstate__ or direct dict merge
       (handler-case
           (let ((ss (clython.runtime:py-getattr inst "__setstate__")))
             (clython.runtime:py-call ss state))
         (error ()
           (when (typep state 'clython.runtime:py-dict)
             (maphash (lambda (k v)
                        (when (typep k 'clython.runtime:py-str)
                          (setf (gethash (clython.runtime:py-str-value k)
                                         (clython.runtime:py-object-dict inst))
                                v)))
                      (clython.runtime:py-dict-value state)))))
       inst))
    (t clython.runtime:+py-none+)))

;;; ─── Module ───────────────────────────────────────────────────────────────

(defun make-pickle-module ()
  "Create the pickle module with dumps/loads support."
  (let ((mod (clython.runtime:make-py-module "pickle"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))

    ;; pickle.dumps(obj, protocol=None, *, fix_imports=True) → bytes
    (setf (gethash "dumps" d)
          (clython.runtime:make-py-function
           :name "dumps"
           :cl-fn (lambda (obj &rest _proto)
                    (declare (ignore _proto))
                    (let* ((sexp (%pickle-to-lisp obj))
                           (txt  (with-output-to-string (s) (prin1 sexp s))))
                      (clython.runtime:make-py-bytes
                       (map '(vector (unsigned-byte 8)) #'char-code txt))))))

    ;; pickle.loads(data, ...) → object
    (setf (gethash "loads" d)
          (clython.runtime:make-py-function
           :name "loads"
           :cl-fn (lambda (data &rest _kw)
                    (declare (ignore _kw))
                    (let* ((raw (if (typep data 'clython.runtime:py-bytes)
                                    (map 'string #'code-char
                                         (clython.runtime:py-bytes-value data))
                                    (clython.runtime:py-str-value data)))
                           (sexp (with-input-from-string (s raw) (read s))))
                      (%pickle-from-lisp sexp)))))

    ;; Exceptions
    (dolist (exc '("PickleError" "PicklingError" "UnpicklingError"))
      (setf (gethash exc d) (clython.runtime:make-py-type :name exc)))

    ;; Constants
    (setf (gethash "DEFAULT_PROTOCOL" d) (clython.runtime:make-py-int 4))
    (setf (gethash "HIGHEST_PROTOCOL" d) (clython.runtime:make-py-int 5))

    (setf (gethash "__name__" d) (clython.runtime:make-py-str "pickle"))
    mod))
