;;;; runtime.lisp — Python object model (CLOS-based)
;;;;
;;;; Implements the core PyObject hierarchy, all primitive types,
;;;; and the key dunder-protocol generic functions.

(defpackage :clython.runtime
  (:use :cl)
  (:export
   ;; Base
   #:py-object
   #:py-object-class
   #:py-object-dict

   ;; Primitive types
   #:py-none
   #:py-bool
   #:py-int
   #:py-float
   #:py-complex
   #:py-str
   #:py-bytes
   #:py-list
   #:py-tuple
   #:py-dict
   #:py-set
   #:py-frozenset
   #:py-function
   #:py-method
   #:py-type
   #:py-module
   #:py-iterator
   #:py-range

   ;; Slot accessors
   #:py-int-value
   #:py-float-value
   #:py-complex-value
   #:py-str-value
   #:py-bytes-value
   #:py-list-value
   #:py-tuple-value
   #:py-dict-value
   #:py-set-value
   #:py-frozenset-value
   #:py-function-name
   #:py-function-params
   #:py-function-body
   #:py-function-env
   #:py-function-cl-fn
   #:py-method-function
   #:py-method-self
   #:py-type-name
   #:py-type-bases
   #:py-type-dict
   #:py-module-name
   #:py-module-dict
   #:py-iterator-next-fn
   #:py-range-start
   #:py-range-stop
   #:py-range-step

   ;; Helpers / internal
   #:py-bool-from-cl
   #:py-bool-raw
   #:stop-iteration

   ;; Singletons
   #:+py-none+
   #:+py-true+
   #:+py-false+

   ;; Constructors
   #:make-py-int
   #:make-py-float
   #:make-py-complex
   #:make-py-str
   #:make-py-bytes
   #:make-py-list
   #:make-py-tuple
   #:make-py-dict
   #:make-py-set
   #:make-py-frozenset
   #:make-py-function
   #:make-py-method
   #:make-py-type
   #:make-py-module
   #:make-py-iterator
   #:make-py-range

   ;; Protocols (generic functions)
   #:py-repr
   #:py-str-of
   #:py-bool-val
   #:py-eq
   #:py-ne
   #:py-lt
   #:py-le
   #:py-gt
   #:py-ge
   #:py-add
   #:py-sub
   #:py-mul
   #:py-truediv
   #:py-floordiv
   #:py-mod
   #:py-pow
   #:py-lshift
   #:py-rshift
   #:py-and
   #:py-or
   #:py-xor
   #:py-neg
   #:py-pos
   #:py-abs
   #:py-invert
   #:py-getattr
   #:py-setattr
   #:py-delattr
   #:py-getitem
   #:py-setitem
   #:py-delitem
   #:py-len
   #:py-iter
   #:py-next
   #:py-call
   #:py-contains
   #:py-hash
   #:py-id
   #:py-type-of
   ;; Exception objects
   #:py-exception-object
   #:py-exception-class-name
   #:py-exception-args
   #:py-exception-message
   #:make-py-exception-object
   #:*exception-hierarchy*
   #:exception-is-subclass-p

   ;; Helpers
   #:py-object-p
   #:cl->py
   #:py->cl))

(in-package :clython.runtime)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Base class
;;;; ─────────────────────────────────────────────────────────────────────────

(defclass py-object ()
  ((%class :initarg :py-class :accessor py-object-class :initform nil)
   (%dict  :initarg :py-dict  :accessor py-object-dict  :initform nil))
  (:documentation "Root of the Python object hierarchy."))

(defun py-object-p (x) (typep x 'py-object))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Primitive types
;;;; ─────────────────────────────────────────────────────────────────────────

;;; NoneType ----------------------------------------------------------------
(defclass py-none (py-object) ()
  (:documentation "Python None."))

(defvar +py-none+ (make-instance 'py-none))

;;; bool -------------------------------------------------------------------
(defclass py-bool (py-object)
  ((%value :initarg :value :reader py-bool-raw :type boolean))
  (:documentation "Python bool."))

(defvar +py-true+  (make-instance 'py-bool :value t))
(defvar +py-false+ (make-instance 'py-bool :value nil))

(defun py-bool-from-cl (x)
  "Return +py-true+ or +py-false+ from a CL generalised boolean."
  (if x +py-true+ +py-false+))

;;; int --------------------------------------------------------------------
(defclass py-int (py-object)
  ((%value :initarg :value :accessor py-int-value :type integer))
  (:documentation "Python int (arbitrary precision via CL bignum)."))

(defun make-py-int (n)
  (check-type n integer)
  (make-instance 'py-int :value n))

;;; float ------------------------------------------------------------------
(defclass py-float (py-object)
  ((%value :initarg :value :accessor py-float-value :type double-float))
  (:documentation "Python float."))

(defun make-py-float (x)
  (make-instance 'py-float :value (coerce x 'double-float)))

;;; complex ----------------------------------------------------------------
(defclass py-complex (py-object)
  ((%value :initarg :value :accessor py-complex-value))
  (:documentation "Python complex."))

(defun make-py-complex (z)
  (make-instance 'py-complex :value (coerce z '(complex double-float))))

;;; str --------------------------------------------------------------------
(defclass py-str (py-object)
  ((%value :initarg :value :accessor py-str-value :type string))
  (:documentation "Python str."))

(defun make-py-str (s)
  (check-type s string)
  (make-instance 'py-str :value s))

;;; bytes ------------------------------------------------------------------
(defclass py-bytes (py-object)
  ((%value :initarg :value :accessor py-bytes-value :type (vector (unsigned-byte 8))))
  (:documentation "Python bytes."))

(defun make-py-bytes (vec)
  (make-instance 'py-bytes :value (coerce vec '(vector (unsigned-byte 8)))))

;;; list -------------------------------------------------------------------
(defclass py-list (py-object)
  ((%value :initarg :value :accessor py-list-value))
  (:documentation "Python list (adjustable vector)."))

(defun make-py-list (&optional items)
  (let ((v (make-array (length items)
                       :fill-pointer (length items)
                       :adjustable t
                       :initial-contents (or items '()))))
    (make-instance 'py-list :value v)))

;;; tuple ------------------------------------------------------------------
(defclass py-tuple (py-object)
  ((%value :initarg :value :accessor py-tuple-value :type simple-vector))
  (:documentation "Python tuple (immutable simple-vector)."))

(defun make-py-tuple (&optional items)
  (make-instance 'py-tuple :value (coerce (or items '()) 'simple-vector)))

;;; dict -------------------------------------------------------------------
(defclass py-dict (py-object)
  ((%value :initarg :value :accessor py-dict-value))
  (:documentation "Python dict."))

(defun make-py-dict ()
  (make-instance 'py-dict :value (make-hash-table :test #'equal)))

;;; set --------------------------------------------------------------------
(defclass py-set (py-object)
  ((%value :initarg :value :accessor py-set-value))
  (:documentation "Python set (mutable)."))

(defun make-py-set (&optional items)
  (let ((ht (make-hash-table :test #'equal)))
    (dolist (i (or items '()))
      (setf (gethash i ht) t))
    (make-instance 'py-set :value ht)))

;;; frozenset --------------------------------------------------------------
(defclass py-frozenset (py-object)
  ((%value :initarg :value :accessor py-frozenset-value))
  (:documentation "Python frozenset (immutable)."))

(defun make-py-frozenset (&optional items)
  (let ((ht (make-hash-table :test #'equal)))
    (dolist (i (or items '()))
      (setf (gethash i ht) t))
    (make-instance 'py-frozenset :value ht)))

;;; function ---------------------------------------------------------------
(defclass py-function (py-object)
  ((%name   :initarg :name   :accessor py-function-name   :initform "<lambda>")
   (%params :initarg :params :accessor py-function-params :initform '())
   (%body   :initarg :body   :accessor py-function-body   :initform nil)
   (%env    :initarg :env    :accessor py-function-env    :initform nil)
   (%cl-fn  :initarg :cl-fn  :accessor py-function-cl-fn  :initform nil))
  (:documentation "Python function or lambda."))

(defun make-py-function (&key name params body env cl-fn)
  (make-instance 'py-function
                 :name (or name "<lambda>")
                 :params (or params '())
                 :body body
                 :env env
                 :cl-fn cl-fn))

;;; method -----------------------------------------------------------------
(defclass py-method (py-object)
  ((%function :initarg :function :accessor py-method-function)
   (%self     :initarg :self     :accessor py-method-self))
  (:documentation "Python bound method."))

(defun make-py-method (fn self)
  (make-instance 'py-method :function fn :self self))

;;; type -------------------------------------------------------------------
(defclass py-type (py-object)
  ((%name  :initarg :name  :accessor py-type-name  :initform "type")
   (%bases :initarg :bases :accessor py-type-bases :initform '())
   (%tdict :initarg :tdict :accessor py-type-dict  :initform nil))
  (:documentation "Python type / metaclass."))

(defun make-py-type (&key name bases tdict)
  (make-instance 'py-type
                 :name  (or name "type")
                 :bases (or bases '())
                 :tdict (or tdict (make-hash-table :test #'equal))))

;;; module -----------------------------------------------------------------
(defclass py-module (py-object)
  ((%name  :initarg :name  :accessor py-module-name)
   (%mdict :initarg :mdict :accessor py-module-dict))
  (:documentation "Python module."))

(defun make-py-module (name)
  (make-instance 'py-module
                 :name name
                 :mdict (make-hash-table :test #'equal)))

;;; iterator (generic) -----------------------------------------------------
(defclass py-iterator (py-object)
  ((%next-fn :initarg :next-fn :accessor py-iterator-next-fn))
  (:documentation "Generic Python iterator backed by a CL thunk."))

(defun make-py-iterator (thunk)
  "THUNK is called with no args; return the next py-object or signal
   StopIteration by signalling a condition named 'stop-iteration'."
  (make-instance 'py-iterator :next-fn thunk))

;;; range ------------------------------------------------------------------
(defclass py-range (py-object)
  ((%start :initarg :start :accessor py-range-start)
   (%stop  :initarg :stop  :accessor py-range-stop)
   (%step  :initarg :step  :accessor py-range-step))
  (:documentation "Python range object."))

(defun make-py-range (start stop &optional (step 1))
  (make-instance 'py-range :start start :stop stop :step step))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; StopIteration condition
;;;; ─────────────────────────────────────────────────────────────────────────

(define-condition stop-iteration (error) ()
  (:report (lambda (c stream)
             (declare (ignore c))
             (format stream "StopIteration"))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Protocol generic functions
;;;; ─────────────────────────────────────────────────────────────────────────

;;; __repr__ / __str__ ------------------------------------------------------

(defgeneric py-repr (obj)
  (:documentation "Return a CL string — Python __repr__."))

(defgeneric py-str-of (obj)
  (:documentation "Return a CL string — Python __str__."))

(defmethod py-repr ((obj py-none))   "None")
(defmethod py-str-of ((obj py-none)) "None")

(defmethod py-repr ((obj py-bool))
  (if (py-bool-raw obj) "True" "False"))
(defmethod py-str-of ((obj py-bool))
  (py-repr obj))

(defmethod py-repr ((obj py-int))
  (format nil "~D" (py-int-value obj)))
(defmethod py-str-of ((obj py-int))
  (py-repr obj))

(defmethod py-repr ((obj py-float))
  (let ((v (py-float-value obj)))
    (if (and (= v (floor v)) (< (abs v) 1.0d15))
        (format nil "~,1f" v)
        (format nil "~G" v))))
(defmethod py-str-of ((obj py-float))
  (py-repr obj))

(defmethod py-repr ((obj py-complex))
  (let* ((z (py-complex-value obj))
         (r (realpart z))
         (i (imagpart z)))
    (if (zerop r)
        (format nil "~Gj" i)
        (format nil "(~G~@Gj)" r i))))
(defmethod py-str-of ((obj py-complex)) (py-repr obj))

(defmethod py-repr ((obj py-str))
  (format nil "'~A'" (py-str-value obj)))
(defmethod py-str-of ((obj py-str))
  (py-str-value obj))

(defmethod py-repr ((obj py-bytes))
  (format nil "b'~A'"
          (with-output-to-string (s)
            (loop for b across (py-bytes-value obj)
                  do (cond ((= b 39)  (write-string "\\'" s))
                           ((= b 92)  (write-string "\\\\" s))
                           ((<= 32 b 126) (write-char (code-char b) s))
                           (t (format s "\\x~2,'0x" b)))))))
(defmethod py-str-of ((obj py-bytes)) (py-repr obj))

(defmethod py-repr ((obj py-list))
  (format nil "[~{~A~^, ~}]"
          (map 'list #'py-repr (py-list-value obj))))
(defmethod py-str-of ((obj py-list)) (py-repr obj))

(defmethod py-repr ((obj py-tuple))
  (let ((elems (coerce (py-tuple-value obj) 'list)))
    (if (= (length elems) 1)
        (format nil "(~A,)" (py-repr (first elems)))
        (format nil "(~{~A~^, ~})" (mapcar #'py-repr elems)))))
(defmethod py-str-of ((obj py-tuple)) (py-repr obj))

(defun repr-dict-key (k)
  "Repr a dict hash-table key (which is a CL value, not a py-object)."
  (typecase k
    (string  (format nil "'~A'" k))
    (integer (format nil "~A" k))
    (float   (format nil "~A" k))
    (t       (if (eq k :none) "None" (format nil "~A" k)))))

(defmethod py-repr ((obj py-dict))
  (let ((pairs '()))
    (maphash (lambda (k v)
               (push (format nil "~A: ~A" (repr-dict-key k) (py-repr v)) pairs))
             (py-dict-value obj))
    (format nil "{~{~A~^, ~}}" (nreverse pairs))))
(defmethod py-str-of ((obj py-dict)) (py-repr obj))

(defun %hash-table-keys (ht)
  (let ((keys '()))
    (maphash (lambda (k v) (declare (ignore v)) (push k keys)) ht)
    (nreverse keys)))

(defmethod py-repr ((obj py-set))
  (let ((keys (%hash-table-keys (py-set-value obj))))
    (if (null keys)
        "set()"
        (format nil "{~{~A~^, ~}}" (mapcar #'py-repr keys)))))
(defmethod py-str-of ((obj py-set)) (py-repr obj))

(defmethod py-repr ((obj py-frozenset))
  (let ((keys (%hash-table-keys (py-frozenset-value obj))))
    (if (null keys)
        "frozenset()"
        (format nil "frozenset({~{~A~^, ~}})" (mapcar #'py-repr keys)))))
(defmethod py-str-of ((obj py-frozenset)) (py-repr obj))

(defmethod py-repr ((obj py-function))
  (format nil "<function ~A>" (py-function-name obj)))
(defmethod py-str-of ((obj py-function)) (py-repr obj))

(defmethod py-repr ((obj py-method))
  (format nil "<bound method ~A>" (py-repr (py-method-function obj))))
(defmethod py-str-of ((obj py-method)) (py-repr obj))

(defmethod py-repr ((obj py-type))
  (format nil "<class '~A'>" (py-type-name obj)))
(defmethod py-str-of ((obj py-type)) (py-repr obj))

(defmethod py-repr ((obj py-module))
  (format nil "<module '~A'>" (py-module-name obj)))
(defmethod py-str-of ((obj py-module)) (py-repr obj))

(defmethod py-repr ((obj py-iterator))
  "<iterator>")
(defmethod py-str-of ((obj py-iterator)) (py-repr obj))

(defmethod py-repr ((obj py-range))
  (if (= (py-range-step obj) 1)
      (format nil "range(~D, ~D)" (py-range-start obj) (py-range-stop obj))
      (format nil "range(~D, ~D, ~D)"
              (py-range-start obj) (py-range-stop obj) (py-range-step obj))))
(defmethod py-str-of ((obj py-range)) (py-repr obj))

;;; __bool__ ---------------------------------------------------------------

(defgeneric py-bool-val (obj)
  (:documentation "Return CL boolean: truthiness of a Python object."))

(defmethod py-bool-val ((obj py-none))   nil)
(defmethod py-bool-val ((obj py-bool))   (py-bool-raw obj))
(defmethod py-bool-val ((obj py-int))    (not (zerop (py-int-value obj))))
(defmethod py-bool-val ((obj py-float))  (not (zerop (py-float-value obj))))
(defmethod py-bool-val ((obj py-complex)) (not (zerop (py-complex-value obj))))
(defmethod py-bool-val ((obj py-str))    (not (string= "" (py-str-value obj))))
(defmethod py-bool-val ((obj py-bytes))  (not (zerop (length (py-bytes-value obj)))))
(defmethod py-bool-val ((obj py-list))   (not (zerop (length (py-list-value obj)))))
(defmethod py-bool-val ((obj py-tuple))  (not (zerop (length (py-tuple-value obj)))))
(defmethod py-bool-val ((obj py-dict))   (not (zerop (hash-table-count (py-dict-value obj)))))
(defmethod py-bool-val ((obj py-set))    (not (zerop (hash-table-count (py-set-value obj)))))
(defmethod py-bool-val ((obj py-frozenset)) (not (zerop (hash-table-count (py-frozenset-value obj)))))
(defmethod py-bool-val ((obj py-object)) t) ; default: all other objects are truthy

;;; __eq__ / __ne__ --------------------------------------------------------

(defgeneric py-eq (a b)
  (:documentation "Python == : return CL boolean."))

(defmethod py-eq ((a py-none) (b py-none)) t)
(defmethod py-eq ((a py-bool) (b py-bool))
  (eq (py-bool-raw a) (py-bool-raw b)))
(defmethod py-eq ((a py-int) (b py-int))
  (= (py-int-value a) (py-int-value b)))
(defmethod py-eq ((a py-float) (b py-float))
  (= (py-float-value a) (py-float-value b)))
(defmethod py-eq ((a py-int) (b py-float))
  (= (py-int-value a) (py-float-value b)))
(defmethod py-eq ((a py-float) (b py-int))
  (= (py-float-value a) (py-int-value b)))
(defmethod py-eq ((a py-complex) (b py-complex))
  (= (py-complex-value a) (py-complex-value b)))
(defmethod py-eq ((a py-str) (b py-str))
  (string= (py-str-value a) (py-str-value b)))
(defmethod py-eq ((a py-bytes) (b py-bytes))
  (equalp (py-bytes-value a) (py-bytes-value b)))
(defmethod py-eq ((a py-list) (b py-list))
  (let ((va (py-list-value a))
        (vb (py-list-value b)))
    (and (= (length va) (length vb))
         (every #'py-eq va vb))))
(defmethod py-eq ((a py-tuple) (b py-tuple))
  (let ((va (py-tuple-value a))
        (vb (py-tuple-value b)))
    (and (= (length va) (length vb))
         (every #'py-eq va vb))))
(defmethod py-eq (a b) (eq a b))  ; identity fallback

(defgeneric py-ne (a b)
  (:documentation "Python != : return CL boolean."))
(defmethod py-ne (a b) (not (py-eq a b)))

;;; ordering ---------------------------------------------------------------

(defgeneric py-lt (a b) (:documentation "Python < : return CL boolean."))
(defgeneric py-le (a b) (:documentation "Python <= : return CL boolean."))
(defgeneric py-gt (a b) (:documentation "Python > : return CL boolean."))
(defgeneric py-ge (a b) (:documentation "Python >= : return CL boolean."))

(defmacro %define-numeric-order (type reader)
  `(progn
     (defmethod py-lt ((a ,type) (b ,type)) (< (,reader a) (,reader b)))
     (defmethod py-le ((a ,type) (b ,type)) (<= (,reader a) (,reader b)))
     (defmethod py-gt ((a ,type) (b ,type)) (> (,reader a) (,reader b)))
     (defmethod py-ge ((a ,type) (b ,type)) (>= (,reader a) (,reader b)))))

(%define-numeric-order py-int   py-int-value)
(%define-numeric-order py-float py-float-value)

(defmethod py-lt ((a py-int) (b py-float)) (< (py-int-value a) (py-float-value b)))
(defmethod py-lt ((a py-float) (b py-int)) (< (py-float-value a) (py-int-value b)))
(defmethod py-le ((a py-int) (b py-float)) (<= (py-int-value a) (py-float-value b)))
(defmethod py-le ((a py-float) (b py-int)) (<= (py-float-value a) (py-int-value b)))
(defmethod py-gt ((a py-int) (b py-float)) (> (py-int-value a) (py-float-value b)))
(defmethod py-gt ((a py-float) (b py-int)) (> (py-float-value a) (py-int-value b)))
(defmethod py-ge ((a py-int) (b py-float)) (>= (py-int-value a) (py-float-value b)))
(defmethod py-ge ((a py-float) (b py-int)) (>= (py-float-value a) (py-int-value b)))

(defmethod py-lt ((a py-str) (b py-str)) (string< (py-str-value a) (py-str-value b)))
(defmethod py-le ((a py-str) (b py-str)) (string<= (py-str-value a) (py-str-value b)))
(defmethod py-gt ((a py-str) (b py-str)) (string> (py-str-value a) (py-str-value b)))
(defmethod py-ge ((a py-str) (b py-str)) (string>= (py-str-value a) (py-str-value b)))

;;; arithmetic -------------------------------------------------------------

(defgeneric py-add (a b) (:documentation "Python a + b."))
(defgeneric py-sub (a b) (:documentation "Python a - b."))
(defgeneric py-mul (a b) (:documentation "Python a * b."))
(defgeneric py-truediv (a b) (:documentation "Python a / b (true division)."))
(defgeneric py-floordiv (a b) (:documentation "Python a // b."))
(defgeneric py-mod (a b) (:documentation "Python a %% b."))
(defgeneric py-pow (a b) (:documentation "Python a ** b."))
(defgeneric py-lshift (a b) (:documentation "Python a << b."))
(defgeneric py-rshift (a b) (:documentation "Python a >> b."))
(defgeneric py-and (a b) (:documentation "Python a & b."))
(defgeneric py-or  (a b) (:documentation "Python a | b."))
(defgeneric py-xor (a b) (:documentation "Python a ^ b."))

;; int × int
(defmethod py-add ((a py-int) (b py-int))
  (make-py-int (+ (py-int-value a) (py-int-value b))))
(defmethod py-sub ((a py-int) (b py-int))
  (make-py-int (- (py-int-value a) (py-int-value b))))
(defmethod py-mul ((a py-int) (b py-int))
  (make-py-int (* (py-int-value a) (py-int-value b))))
(defmethod py-truediv ((a py-int) (b py-int))
  (when (zerop (py-int-value b))
    (error "ZeroDivisionError: division by zero"))
  (make-py-float (/ (float (py-int-value a) 1.0d0)
                    (float (py-int-value b) 1.0d0))))
(defmethod py-floordiv ((a py-int) (b py-int))
  (when (zerop (py-int-value b))
    (error "ZeroDivisionError: integer division or modulo by zero"))
  (make-py-int (floor (py-int-value a) (py-int-value b))))
(defmethod py-mod ((a py-int) (b py-int))
  (when (zerop (py-int-value b))
    (error "ZeroDivisionError: integer division or modulo by zero"))
  (make-py-int (mod (py-int-value a) (py-int-value b))))
(defmethod py-pow ((a py-int) (b py-int))
  (make-py-int (expt (py-int-value a) (py-int-value b))))
(defmethod py-lshift ((a py-int) (b py-int))
  (make-py-int (ash (py-int-value a) (py-int-value b))))
(defmethod py-rshift ((a py-int) (b py-int))
  (make-py-int (ash (py-int-value a) (- (py-int-value b)))))
(defmethod py-and ((a py-int) (b py-int))
  (make-py-int (logand (py-int-value a) (py-int-value b))))
(defmethod py-or  ((a py-int) (b py-int))
  (make-py-int (logior (py-int-value a) (py-int-value b))))
(defmethod py-xor ((a py-int) (b py-int))
  (make-py-int (logxor (py-int-value a) (py-int-value b))))

;; float × float
(defmethod py-add ((a py-float) (b py-float))
  (make-py-float (+ (py-float-value a) (py-float-value b))))
(defmethod py-sub ((a py-float) (b py-float))
  (make-py-float (- (py-float-value a) (py-float-value b))))
(defmethod py-mul ((a py-float) (b py-float))
  (make-py-float (* (py-float-value a) (py-float-value b))))
(defmethod py-truediv ((a py-float) (b py-float))
  (when (zerop (py-float-value b))
    (error "ZeroDivisionError: float division by zero"))
  (make-py-float (/ (py-float-value a) (py-float-value b))))
(defmethod py-floordiv ((a py-float) (b py-float))
  (when (zerop (py-float-value b))
    (error "ZeroDivisionError: float floor division by zero"))
  (make-py-float (ffloor (py-float-value a) (py-float-value b))))
(defmethod py-mod ((a py-float) (b py-float))
  (make-py-float (mod (py-float-value a) (py-float-value b))))
(defmethod py-pow ((a py-float) (b py-float))
  (make-py-float (expt (py-float-value a) (py-float-value b))))

;; int × float / float × int
(defmacro %coerce-float-op (method int-reader float-reader cl-op)
  `(progn
     (defmethod ,method ((a py-int) (b py-float))
       (make-py-float (,cl-op (float (,int-reader a) 1.0d0) (,float-reader b))))
     (defmethod ,method ((a py-float) (b py-int))
       (make-py-float (,cl-op (,float-reader a) (float (,int-reader b) 1.0d0))))))

(%coerce-float-op py-add   py-int-value py-float-value +)
(%coerce-float-op py-sub   py-int-value py-float-value -)
(%coerce-float-op py-mul   py-int-value py-float-value *)
(%coerce-float-op py-truediv py-int-value py-float-value /)

;; str concatenation / repetition
(defmethod py-add ((a py-str) (b py-str))
  (make-py-str (concatenate 'string (py-str-value a) (py-str-value b))))

(defmethod py-mul ((a py-str) (b py-int))
  (let ((n (py-int-value b)))
    (if (<= n 0)
        (make-py-str "")
        (make-py-str (apply #'concatenate 'string
                            (loop repeat n collect (py-str-value a)))))))
(defmethod py-mul ((a py-int) (b py-str)) (py-mul b a))

;; list concatenation / repetition
(defmethod py-add ((a py-list) (b py-list))
  (let ((result (make-array 0 :fill-pointer 0 :adjustable t)))
    (loop for x across (py-list-value a) do (vector-push-extend x result))
    (loop for x across (py-list-value b) do (vector-push-extend x result))
    (make-instance 'py-list :value result)))

(defmethod py-mul ((a py-list) (b py-int))
  (let ((n (py-int-value b))
        (result (make-array 0 :fill-pointer 0 :adjustable t)))
    (loop repeat (max 0 n)
          do (loop for x across (py-list-value a)
                   do (vector-push-extend x result)))
    (make-instance 'py-list :value result)))
(defmethod py-mul ((a py-int) (b py-list)) (py-mul b a))

;; tuple concatenation
(defmethod py-add ((a py-tuple) (b py-tuple))
  (make-py-tuple (concatenate 'list
                               (coerce (py-tuple-value a) 'list)
                               (coerce (py-tuple-value b) 'list))))

;;; unary ------------------------------------------------------------------

(defgeneric py-neg (a) (:documentation "Python -a."))
(defgeneric py-pos (a) (:documentation "Python +a."))
(defgeneric py-abs (a) (:documentation "Python abs(a)."))
(defgeneric py-invert (a) (:documentation "Python ~a."))

(defmethod py-neg ((a py-int))   (make-py-int   (- (py-int-value a))))
(defmethod py-pos ((a py-int))   (make-py-int   (py-int-value a)))
(defmethod py-abs ((a py-int))   (make-py-int   (abs (py-int-value a))))
(defmethod py-invert ((a py-int)) (make-py-int  (lognot (py-int-value a))))
(defmethod py-neg ((a py-float)) (make-py-float (- (py-float-value a))))
(defmethod py-pos ((a py-float)) (make-py-float (py-float-value a)))
(defmethod py-abs ((a py-float)) (make-py-float (abs (py-float-value a))))
(defmethod py-neg ((a py-complex)) (make-py-complex (- (py-complex-value a))))
(defmethod py-abs ((a py-complex)) (make-py-float (abs (py-complex-value a))))

;;; attribute access -------------------------------------------------------

(defgeneric py-getattr (obj name)
  (:documentation "Python getattr(obj, name) — name is a CL string."))

(defgeneric py-setattr (obj name value)
  (:documentation "Python setattr(obj, name, value)."))

(defgeneric py-delattr (obj name)
  (:documentation "Python delattr(obj, name)."))

(defmethod py-getattr ((obj py-object) (name string))
  (let ((d (py-object-dict obj)))
    (when (hash-table-p d)
      (multiple-value-bind (val found) (gethash name d)
        (when found (return-from py-getattr val)))))
  (error "AttributeError: '~A' object has no attribute '~A'"
         (class-name (class-of obj)) name))

(defmethod py-setattr ((obj py-object) (name string) value)
  (unless (hash-table-p (py-object-dict obj))
    (setf (py-object-dict obj) (make-hash-table :test #'equal)))
  (setf (gethash name (py-object-dict obj)) value))

(defmethod py-delattr ((obj py-object) (name string))
  (let ((d (py-object-dict obj)))
    (when (hash-table-p d)
      (remhash name d))))

;; Module attribute access via mdict
(defmethod py-getattr ((obj py-module) (name string))
  (multiple-value-bind (val found) (gethash name (py-module-dict obj))
    (if found val
        (error "AttributeError: module '~A' has no attribute '~A'"
               (py-module-name obj) name))))

(defmethod py-setattr ((obj py-module) (name string) value)
  (setf (gethash name (py-module-dict obj)) value))

;;; subscript access -------------------------------------------------------

(defgeneric py-getitem (obj key)
  (:documentation "Python obj[key]."))

(defgeneric py-setitem (obj key value)
  (:documentation "Python obj[key] = value."))

(defgeneric py-delitem (obj key)
  (:documentation "Python del obj[key]."))

(defmethod py-getitem ((obj py-list) (key py-int))
  (let* ((vec (py-list-value obj))
         (len (length vec))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (error "IndexError: list index out of range")
        (aref vec i))))

(defmethod py-setitem ((obj py-list) (key py-int) value)
  (let* ((vec (py-list-value obj))
         (len (length vec))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (error "IndexError: list assignment index out of range")
        (setf (aref vec i) value))))

(defmethod py-delitem ((obj py-list) (key py-int))
  (let* ((vec (py-list-value obj))
         (len (length vec))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (error "IndexError: list assignment index out of range")
        (progn
          (loop for j from i below (1- len)
                do (setf (aref vec j) (aref vec (1+ j))))
          (decf (fill-pointer vec))))))

(defmethod py-getitem ((obj py-tuple) (key py-int))
  (let* ((vec (py-tuple-value obj))
         (len (length vec))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (error "IndexError: tuple index out of range")
        (svref vec i))))

(defmethod py-getitem ((obj py-str) (key py-int))
  (let* ((s   (py-str-value obj))
         (len (length s))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (error "IndexError: string index out of range")
        (make-py-str (string (char s i))))))

(defun dict-hash-key (key)
  "Unwrap a Python object to a CL value suitable for EQUAL hash-table lookup.
   py-str → CL string, py-int → CL integer, py-float → CL float,
   py-bool → CL T/NIL, py-none → :none, otherwise the object itself."
  (typecase key
    (py-str   (py-str-value key))
    (py-int   (py-int-value key))
    (py-float (py-float-value key))
    (py-bool  (py-bool-raw key))
    (t        (if (eq key +py-none+) :none key))))

(defmethod py-getitem ((obj py-dict) key)
  (multiple-value-bind (val found) (gethash (dict-hash-key key) (py-dict-value obj))
    (unless found
      (error "KeyError: ~A" (py-repr key)))
    val))

(defmethod py-setitem ((obj py-dict) key value)
  (setf (gethash (dict-hash-key key) (py-dict-value obj)) value))

(defmethod py-delitem ((obj py-dict) key)
  (unless (remhash (dict-hash-key key) (py-dict-value obj))
    (error "KeyError: ~A" (py-repr key))))

;;; __len__ ----------------------------------------------------------------

(defgeneric py-len (obj) (:documentation "Python len(obj) — returns a CL integer."))

(defmethod py-len ((obj py-str))       (length (py-str-value obj)))
(defmethod py-len ((obj py-bytes))     (length (py-bytes-value obj)))
(defmethod py-len ((obj py-list))      (length (py-list-value obj)))
(defmethod py-len ((obj py-tuple))     (length (py-tuple-value obj)))
(defmethod py-len ((obj py-dict))      (hash-table-count (py-dict-value obj)))
(defmethod py-len ((obj py-set))       (hash-table-count (py-set-value obj)))
(defmethod py-len ((obj py-frozenset)) (hash-table-count (py-frozenset-value obj)))

;;; __iter__ / __next__ ----------------------------------------------------

(defgeneric py-iter (obj)
  (:documentation "Return a py-iterator for obj."))

(defgeneric py-next (iter)
  (:documentation "Advance iter; signal stop-iteration when exhausted."))

(defmethod py-iter ((obj py-iterator)) obj)

(defmethod py-next ((obj py-iterator))
  (funcall (py-iterator-next-fn obj)))

(defmethod py-iter ((obj py-list))
  (let ((vec (py-list-value obj))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length vec))
           (prog1 (aref vec i) (incf i))
           (error 'stop-iteration))))))

(defmethod py-iter ((obj py-tuple))
  (let ((vec (py-tuple-value obj))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length vec))
           (prog1 (svref vec i) (incf i))
           (error 'stop-iteration))))))

(defmethod py-iter ((obj py-str))
  (let ((s (py-str-value obj))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length s))
           (prog1 (make-py-str (string (char s i))) (incf i))
           (error 'stop-iteration))))))

(defmethod py-iter ((obj py-bytes))
  (let ((v (py-bytes-value obj))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length v))
           (prog1 (make-py-int (aref v i)) (incf i))
           (error 'stop-iteration))))))

(defun cl-to-py (val)
  "Wrap a CL value back into a py-object for iteration over dict keys."
  (typecase val
    (string  (make-py-str val))
    (integer (make-py-int val))
    (float   (make-py-float val))
    (t       (if (eq val :none) +py-none+ val))))

(defmethod py-iter ((obj py-dict))
  (let ((keys (%hash-table-keys (py-dict-value obj)))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length keys))
           (prog1 (cl-to-py (nth i keys)) (incf i))
           (error 'stop-iteration))))))

(defmethod py-iter ((obj py-set))
  (let ((keys (%hash-table-keys (py-set-value obj)))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length keys))
           (prog1 (nth i keys) (incf i))
           (error 'stop-iteration))))))

(defmethod py-iter ((obj py-frozenset))
  (let ((keys (%hash-table-keys (py-frozenset-value obj)))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length keys))
           (prog1 (nth i keys) (incf i))
           (error 'stop-iteration))))))

(defmethod py-iter ((obj py-range))
  (let ((cur  (py-range-start obj))
        (stop (py-range-stop  obj))
        (step (py-range-step  obj)))
    (make-py-iterator
     (lambda ()
       (if (if (> step 0) (< cur stop) (> cur stop))
           (let ((val cur))
             (incf cur step)
             (make-py-int val))
           (error 'stop-iteration))))))

;;; __call__ ---------------------------------------------------------------

(defgeneric py-call (obj &rest args)
  (:documentation "Python obj(*args)."))

(defmethod py-call ((obj py-function) &rest args)
  (let ((cl-fn (py-function-cl-fn obj)))
    (if cl-fn
        (apply cl-fn args)
        (error "py-function ~A has no CL implementation (interpreter not yet wired)"
               (py-function-name obj)))))

(defmethod py-call ((obj py-method) &rest args)
  (apply #'py-call (py-method-function obj) (py-method-self obj) args))

;;; __contains__ -----------------------------------------------------------

(defgeneric py-contains (container item)
  (:documentation "Python item in container — returns CL boolean."))

(defmethod py-contains ((obj py-list) item)
  (some (lambda (x) (py-eq x item)) (py-list-value obj)))

(defmethod py-contains ((obj py-tuple) item)
  (some (lambda (x) (py-eq x item)) (py-tuple-value obj)))

(defmethod py-contains ((obj py-str) (item py-str))
  (not (null (search (py-str-value item) (py-str-value obj)))))

(defmethod py-contains ((obj py-dict) key)
  (nth-value 1 (gethash (dict-hash-key key) (py-dict-value obj))))

(defmethod py-contains ((obj py-set) item)
  (nth-value 1 (gethash item (py-set-value obj))))

(defmethod py-contains ((obj py-frozenset) item)
  (nth-value 1 (gethash item (py-frozenset-value obj))))

;;; __hash__ / id ----------------------------------------------------------

(defgeneric py-hash (obj)
  (:documentation "Python hash(obj) — returns a CL integer."))

(defmethod py-hash ((obj py-none))   0)
(defmethod py-hash ((obj py-bool))   (if (py-bool-raw obj) 1 0))
(defmethod py-hash ((obj py-int))    (py-int-value obj))
(defmethod py-hash ((obj py-float))  (sxhash (py-float-value obj)))
(defmethod py-hash ((obj py-str))    (sxhash (py-str-value obj)))
(defmethod py-hash ((obj py-bytes))  (sxhash (py-bytes-value obj)))
(defmethod py-hash ((obj py-tuple))
  (reduce (lambda (acc x) (logxor acc (py-hash x))) (py-tuple-value obj) :initial-value 0))
(defmethod py-hash ((obj py-object)) (sxhash obj))

(defgeneric py-id (obj)
  (:documentation "Python id(obj) — returns a CL integer."))
(defmethod py-id (obj) (sb-kernel:get-lisp-obj-address obj))

;;; type-of ----------------------------------------------------------------

(defgeneric py-type-of (obj)
  (:documentation "Return a CL string naming the Python type."))

(defmethod py-type-of ((obj py-none))      "NoneType")
(defmethod py-type-of ((obj py-bool))      "bool")
(defmethod py-type-of ((obj py-int))       "int")
(defmethod py-type-of ((obj py-float))     "float")
(defmethod py-type-of ((obj py-complex))   "complex")
(defmethod py-type-of ((obj py-str))       "str")
(defmethod py-type-of ((obj py-bytes))     "bytes")
(defmethod py-type-of ((obj py-list))      "list")
(defmethod py-type-of ((obj py-tuple))     "tuple")
(defmethod py-type-of ((obj py-dict))      "dict")
(defmethod py-type-of ((obj py-set))       "set")
(defmethod py-type-of ((obj py-frozenset)) "frozenset")
(defmethod py-type-of ((obj py-function))  "function")
(defmethod py-type-of ((obj py-method))    "method")
(defmethod py-type-of ((obj py-type))      "type")
(defmethod py-type-of ((obj py-module))    "module")
(defmethod py-type-of ((obj py-iterator))  "iterator")
(defmethod py-type-of ((obj py-range))     "range")
(defmethod py-type-of ((obj py-object))    (string (class-name (class-of obj))))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Exception objects — runtime representation of Python exceptions
;;;; ═══════════════════════════════════════════════════════════════════════════

(defclass py-exception-object (py-object)
  ((class-name :initarg :class-name :accessor py-exception-class-name
               :initform "Exception"
               :documentation "Python exception class name (e.g. \"ValueError\")")
   (args       :initarg :args :accessor py-exception-args
               :initform nil
               :documentation "Exception arguments (list of py-objects)")
   (message    :initarg :message :accessor py-exception-message
               :initform ""
               :documentation "Human-readable message string"))
  (:documentation "Runtime representation of a Python exception instance."))

(defun make-py-exception-object (class-name &optional args)
  "Create a py-exception-object with CLASS-NAME and ARGS."
  (let ((msg (if (and args (typep (first args) 'py-str))
                 (py-str-value (first args))
                 (if args (py-str-of (first args)) ""))))
    (make-instance 'py-exception-object
                   :class-name class-name
                   :args args
                   :message msg)))

(defmethod py-repr ((obj py-exception-object))
  (let ((msg (py-exception-message obj)))
    (if (string= msg "")
        (format nil "~A()" (py-exception-class-name obj))
        (format nil "~A('~A')" (py-exception-class-name obj) msg))))

(defmethod py-str-of ((obj py-exception-object))
  (py-exception-message obj))

(defmethod py-type-of ((obj py-exception-object))
  (py-exception-class-name obj))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Exception hierarchy — parent mapping for isinstance/except checks
;;;; ─────────────────────────────────────────────────────────────────────────

(defvar *exception-hierarchy* (make-hash-table :test #'equal)
  "Maps exception class name → list of parent class names (MRO-like).")

(defun %register-exception-hierarchy ()
  "Populate the exception inheritance chain."
  (let ((tree
         ;; (child . parents) — parents listed from immediate to root
         '(("BaseException"         . ())
           ("Exception"             . ("BaseException"))
           ("ArithmeticError"       . ("Exception" "BaseException"))
           ("ZeroDivisionError"     . ("ArithmeticError" "Exception" "BaseException"))
           ("OverflowError"         . ("ArithmeticError" "Exception" "BaseException"))
           ("FloatingPointError"    . ("ArithmeticError" "Exception" "BaseException"))
           ("AssertionError"        . ("Exception" "BaseException"))
           ("AttributeError"       . ("Exception" "BaseException"))
           ("EOFError"             . ("Exception" "BaseException"))
           ("ImportError"          . ("Exception" "BaseException"))
           ("ModuleNotFoundError"  . ("ImportError" "Exception" "BaseException"))
           ("LookupError"          . ("Exception" "BaseException"))
           ("IndexError"           . ("LookupError" "Exception" "BaseException"))
           ("KeyError"             . ("LookupError" "Exception" "BaseException"))
           ("NameError"            . ("Exception" "BaseException"))
           ("UnboundLocalError"    . ("NameError" "Exception" "BaseException"))
           ("OSError"              . ("Exception" "BaseException"))
           ("FileNotFoundError"    . ("OSError" "Exception" "BaseException"))
           ("PermissionError"      . ("OSError" "Exception" "BaseException"))
           ("FileExistsError"      . ("OSError" "Exception" "BaseException"))
           ("IsADirectoryError"    . ("OSError" "Exception" "BaseException"))
           ("NotADirectoryError"   . ("OSError" "Exception" "BaseException"))
           ("RuntimeError"         . ("Exception" "BaseException"))
           ("RecursionError"       . ("RuntimeError" "Exception" "BaseException"))
           ("NotImplementedError"  . ("RuntimeError" "Exception" "BaseException"))
           ("StopIteration"        . ("Exception" "BaseException"))
           ("StopAsyncIteration"   . ("Exception" "BaseException"))
           ("SyntaxError"          . ("Exception" "BaseException"))
           ("IndentationError"     . ("SyntaxError" "Exception" "BaseException"))
           ("TabError"             . ("IndentationError" "SyntaxError" "Exception" "BaseException"))
           ("TypeError"            . ("Exception" "BaseException"))
           ("ValueError"           . ("Exception" "BaseException"))
           ("UnicodeError"         . ("ValueError" "Exception" "BaseException"))
           ("KeyboardInterrupt"    . ("BaseException"))
           ("SystemExit"           . ("BaseException"))
           ("GeneratorExit"        . ("BaseException")))))
    (dolist (entry tree)
      ;; Each class maps to itself + all its parents
      (setf (gethash (car entry) *exception-hierarchy*)
            (cons (car entry) (cdr entry))))))

(%register-exception-hierarchy)

(defun exception-is-subclass-p (child-name parent-name)
  "Return T if CHILD-NAME is the same as or a subclass of PARENT-NAME."
  (let ((mro (gethash child-name *exception-hierarchy*)))
    (if mro
        (member parent-name mro :test #'string=)
        ;; Unknown exception — only match if names are equal
        (string= child-name parent-name))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; CL ↔ Python coercion helpers
;;;; ─────────────────────────────────────────────────────────────────────────

(defun cl->py (x)
  "Best-effort coerce a CL value to a py-object."
  (cond
    ((null x)              +py-none+)
    ((eq x t)              +py-true+)
    ((eq x nil)            +py-false+)
    ((integerp x)          (make-py-int x))
    ((typep x 'double-float) (make-py-float x))
    ((floatp x)            (make-py-float (coerce x 'double-float)))
    ((complexp x)          (make-py-complex x))
    ((stringp x)           (make-py-str x))
    ((typep x '(vector (unsigned-byte 8))) (make-py-bytes x))
    ((vectorp x)           (make-py-list (coerce x 'list)))
    ((listp x)             (make-py-list x))
    ((py-object-p x)       x)
    (t (error "Cannot coerce ~S to py-object" x))))

(defun py->cl (obj)
  "Best-effort coerce a py-object to a natural CL value."
  (typecase obj
    (py-none    nil)
    (py-bool    (py-bool-raw obj))
    (py-int     (py-int-value obj))
    (py-float   (py-float-value obj))
    (py-complex (py-complex-value obj))
    (py-str     (py-str-value obj))
    (py-bytes   (py-bytes-value obj))
    (py-list    (coerce (py-list-value obj) 'list))
    (py-tuple   (coerce (py-tuple-value obj) 'list))
    (otherwise  obj)))
