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
   #:py-staticmethod-wrapper
   #:py-staticmethod-function
   #:py-classmethod-wrapper
   #:py-classmethod-function
   #:py-property-wrapper
   #:py-property-fget
   #:py-property-fset
   #:py-super
   #:make-py-super
   #:py-super-type
   #:py-super-obj
   #:py-type
   #:py-module
   #:py-iterator
   #:py-generator
   #:py-coroutine
   #:py-range
   #:py-slice

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
   #:py-function-generator
   #:py-function-async-p
   #:py-method-function
   #:py-method-self
   #:py-type-name
   #:py-type-bases
   #:py-type-dict
   #:py-module-name
   #:py-module-dict
   #:py-iterator-next-fn
   #:py-generator-mutex
   #:py-generator-caller-queue
   #:py-generator-gen-queue
   #:py-generator-value
   #:py-generator-sent-value
   #:py-generator-finished
   #:py-generator-thread
   #:py-coroutine-body-fn
   #:py-coroutine-result
   #:py-coroutine-finished
   #:py-coroutine-started
   #:py-range-start
   #:py-range-stop
   #:py-range-step
   #:py-slice-start
   #:py-slice-stop
   #:py-slice-step

   ;; Helpers / internal
   #:py-bool-from-cl
   #:py-bool-raw
   #:stop-iteration

   ;; Singletons
   #:+py-none+
   #:py-ellipsis
   #:+py-ellipsis+
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
   #:make-py-generator
   #:py-generator-send
   #:make-py-coroutine
   #:py-coroutine-run
   #:make-py-range
   #:make-py-slice

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

   ;; Kwargs passing
   #:*current-kwargs*

   ;; Helpers
   #:py-object-p
   #:cl->py
   #:py->cl
   ;; Runtime error condition
   #:py-runtime-error
   #:py-runtime-error-class-name
   #:py-runtime-error-message
   #:py-raise
   #:%lookup-dunder
   #:*object-type*
   #:%compute-c3-mro))

(in-package :clython.runtime)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Runtime error condition (catchable by try/except)
;;;; ─────────────────────────────────────────────────────────────────────────

(define-condition py-runtime-error (error)
  ((class-name :initarg :class-name :reader py-runtime-error-class-name)
   (message    :initarg :message    :reader py-runtime-error-message :initform ""))
  (:report (lambda (c stream)
             (let ((name (py-runtime-error-class-name c))
                   (msg  (py-runtime-error-message c)))
               (if (string= msg "")
                   (format stream "~A" name)
                   (format stream "~A: ~A" name msg)))))
  (:documentation "Signalled by runtime operations (arithmetic, indexing, etc.)
   when a Python-level error occurs. Caught by the try/except handler in eval."))

(defun py-raise (class-name message &rest format-args)
  "Signal a py-runtime-error with CLASS-NAME and formatted MESSAGE."
  (error 'py-runtime-error
         :class-name class-name
         :message (if format-args
                      (apply #'format nil message format-args)
                      message)))

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

;;; Ellipsis ---------------------------------------------------------------
(defclass py-ellipsis (py-object) ()
  (:documentation "Python Ellipsis (...)."))

(defvar +py-ellipsis+ (make-instance 'py-ellipsis))

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

(defun make-py-dict (&optional ht)
  (make-instance 'py-dict :value (or ht (make-hash-table :test #'equal))))

;;; set --------------------------------------------------------------------
(defclass py-set (py-object)
  ((%value :initarg :value :accessor py-set-value))
  (:documentation "Python set (mutable)."))

(defun set-hash-key (key)
  "Unwrap a Python object to a CL value suitable for EQUAL hash-table lookup in sets."
  (typecase key
    (py-str   (py-str-value key))
    (py-int   (py-int-value key))
    (py-float (py-float-value key))
    (py-bool  (py-bool-raw key))
    (t        (if (eq key +py-none+) :none key))))

(defun make-py-set (&optional items)
  (let ((ht (make-hash-table :test #'equal)))
    (dolist (i (or items '()))
      (setf (gethash (set-hash-key i) ht) i))
    (make-instance 'py-set :value ht)))

;;; frozenset --------------------------------------------------------------
(defclass py-frozenset (py-object)
  ((%value :initarg :value :accessor py-frozenset-value))
  (:documentation "Python frozenset (immutable)."))

(defun make-py-frozenset (&optional items)
  (let ((ht (make-hash-table :test #'equal)))
    (dolist (i (or items '()))
      (setf (gethash (set-hash-key i) ht) i))
    (make-instance 'py-frozenset :value ht)))

;;; function ---------------------------------------------------------------
(defclass py-function (py-object)
  ((%name      :initarg :name      :accessor py-function-name      :initform "<lambda>")
   (%params    :initarg :params    :accessor py-function-params    :initform '())
   (%body      :initarg :body      :accessor py-function-body      :initform nil)
   (%env       :initarg :env       :accessor py-function-env       :initform nil)
   (%cl-fn     :initarg :cl-fn     :accessor py-function-cl-fn     :initform nil)
   (%generator :initarg :generator :accessor py-function-generator :initform nil)
   (%async-p   :initarg :async-p   :accessor py-function-async-p   :initform nil)
   (%docstring :initarg :docstring :accessor py-function-docstring :initform nil))
  (:documentation "Python function or lambda."))

(defun make-py-function (&key name params body env cl-fn generator async-p docstring)
  (make-instance 'py-function
                 :name (or name "<lambda>")
                 :params (or params '())
                 :body body
                 :env env
                 :cl-fn cl-fn
                 :generator generator
                 :async-p async-p
                 :docstring docstring))

;;; method -----------------------------------------------------------------
(defclass py-super (py-object)
  ((%type     :initarg :type     :accessor py-super-type)
   (%obj      :initarg :obj      :accessor py-super-obj))
  (:documentation "Python super() proxy — delegates attr lookup to parent class."))

(defmethod py-getattr ((obj py-super) (name string))
  "Look up NAME in the parent class(es) of the super's type."
  (let* ((cls (py-super-type obj))
         (bases (when (typep cls 'py-type) (py-type-bases cls))))
    (dolist (base bases)
      (multiple-value-bind (val found) (%lookup-in-class-hierarchy base name)
        (when found
          (if (typep val 'py-function)
              (return-from py-getattr
                (make-instance 'py-method :function val :self (py-super-obj obj)))
              (return-from py-getattr val)))))
    (py-raise "AttributeError" "'super' object has no attribute '~A'" name)))

(defclass py-method (py-object)
  ((%function :initarg :function :accessor py-method-function)
   (%self     :initarg :self     :accessor py-method-self))
  (:documentation "Python bound method."))

(defun make-py-method (fn self)
  (make-instance 'py-method :function fn :self self))

;;; staticmethod / classmethod / property wrappers -------------------------
(defclass py-staticmethod-wrapper (py-object)
  ((%function :initarg :function :accessor py-staticmethod-function))
  (:documentation "Python staticmethod descriptor."))

(defclass py-classmethod-wrapper (py-object)
  ((%function :initarg :function :accessor py-classmethod-function))
  (:documentation "Python classmethod descriptor."))

(defclass py-property-wrapper (py-object)
  ((%fget :initarg :fget :accessor py-property-fget :initform nil)
   (%fset :initarg :fset :accessor py-property-fset :initform nil))
  (:documentation "Python property descriptor."))

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

;;; generator --------------------------------------------------------------
(defclass py-generator (py-object)
  ((%mutex        :accessor py-generator-mutex)
   (%caller-queue :accessor py-generator-caller-queue)
   (%gen-queue    :accessor py-generator-gen-queue)
   (%value        :accessor py-generator-value        :initform nil)
   (%sent-value   :accessor py-generator-sent-value   :initform nil)
   (%state        :accessor py-generator-state        :initform :created)  ; :created :yielded :running :finished
   (%finished     :accessor py-generator-finished     :initform nil)
   (%thread       :accessor py-generator-thread       :initform nil))
  (:documentation "Python generator object backed by a thread."))

(defun make-py-generator (body-fn)
  "Create a generator. BODY-FN is a function of one argument (a yield-fn).
   The yield-fn takes (value) and suspends the generator, returning the sent value."
  (let* ((mutex (sb-thread:make-mutex :name "generator-mutex"))
         (caller-queue (sb-thread:make-waitqueue :name "generator-caller"))
         (gen-queue (sb-thread:make-waitqueue :name "generator-gen"))
         (gen (make-instance 'py-generator)))
    (setf (py-generator-mutex gen) mutex
          (py-generator-caller-queue gen) caller-queue
          (py-generator-gen-queue gen) gen-queue)
    (let ((thread
            (sb-thread:make-thread
             (lambda ()
               (sb-thread:with-mutex (mutex)
                 ;; Wait until first next() call
                 (loop until (eq (py-generator-state gen) :running)
                       do (sb-thread:condition-wait gen-queue mutex))
                 (unwind-protect
                      (progn
                        (funcall body-fn
                                 (lambda (value)
                                   ;; yield: store value, notify caller, wait for resume
                                   (setf (py-generator-value gen) value
                                         (py-generator-state gen) :yielded)
                                   (sb-thread:condition-notify caller-queue)
                                   ;; Wait until next()/send() resumes us
                                   (loop until (eq (py-generator-state gen) :running)
                                         do (sb-thread:condition-wait gen-queue mutex))
                                   ;; Return the sent value
                                   (let ((sent (py-generator-sent-value gen)))
                                     (setf (py-generator-sent-value gen) nil)
                                     (if (eq sent :next-signal)
                                         +py-none+
                                         sent)))))
                   ;; Generator body completed (returned or errored) => finished
                   (setf (py-generator-finished gen) t
                         (py-generator-state gen) :finished)
                   (sb-thread:condition-notify caller-queue))))
             :name "clython-generator")))
      (setf (py-generator-thread gen) thread)
      gen)))

(defun py-generator-send (gen value)
  "Send a value to the generator and get the next yielded value.
   Signal stop-iteration when generator is exhausted."
  (when (py-generator-finished gen)
    (error 'stop-iteration))
  (sb-thread:with-mutex ((py-generator-mutex gen))
    ;; Tell generator to run with this sent value
    (setf (py-generator-sent-value gen) value
          (py-generator-state gen) :running)
    (sb-thread:condition-notify (py-generator-gen-queue gen))
    ;; Wait for the generator to yield or finish
    (loop until (member (py-generator-state gen) '(:yielded :finished))
          do (sb-thread:condition-wait (py-generator-caller-queue gen)
                                       (py-generator-mutex gen)))
    (if (py-generator-finished gen)
        (error 'stop-iteration)
        (let ((val (py-generator-value gen)))
          (setf (py-generator-value gen) nil)
          val))))

;;; coroutine --------------------------------------------------------------
(defclass py-coroutine (py-object)
  ((%body-fn  :initarg :body-fn  :accessor py-coroutine-body-fn  :initform nil)
   (%result   :accessor py-coroutine-result   :initform nil)
   (%finished :accessor py-coroutine-finished :initform nil)
   (%started  :accessor py-coroutine-started  :initform nil)
   (%error    :accessor py-coroutine-error    :initform nil))
  (:documentation "Python coroutine object (returned by async def functions).
   In Clython's synchronous interpreter, coroutines run eagerly when awaited."))

(defun make-py-coroutine (body-fn)
  "Create a coroutine. BODY-FN is a thunk that executes the async function body."
  (make-instance 'py-coroutine :body-fn body-fn))

(defun py-coroutine-run (coro)
  "Drive a coroutine to completion synchronously. Returns the result.
   If already finished, returns the cached result."
  (when (py-coroutine-finished coro)
    (if (py-coroutine-error coro)
        (error (py-coroutine-error coro))
        (return-from py-coroutine-run (py-coroutine-result coro))))
  (when (py-coroutine-started coro)
    (py-raise "RuntimeError" "coroutine is being awaited"))
  (setf (py-coroutine-started coro) t)
  (handler-case
      (let ((result (funcall (py-coroutine-body-fn coro))))
        (setf (py-coroutine-result coro) result
              (py-coroutine-finished coro) t)
        result)
    (error (e)
      (setf (py-coroutine-error coro) e
            (py-coroutine-finished coro) t)
      (error e))))

;;; range ------------------------------------------------------------------
(defclass py-range (py-object)
  ((%start :initarg :start :accessor py-range-start)
   (%stop  :initarg :stop  :accessor py-range-stop)
   (%step  :initarg :step  :accessor py-range-step))
  (:documentation "Python range object."))

(defun make-py-range (start stop &optional (step 1))
  (make-instance 'py-range :start start :stop stop :step step))

(defclass py-slice (py-object)
  ((%start :initarg :start :accessor py-slice-start)
   (%stop  :initarg :stop  :accessor py-slice-stop)
   (%step  :initarg :step  :accessor py-slice-step))
  (:documentation "Python slice object — slice(start, stop, step)."))

(defun make-py-slice (start stop step)
  (make-instance 'py-slice :start start :stop stop :step step))

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

;;; C3 MRO linearization ---------------------------------------------------

(defvar *object-type* nil
  "Cached reference to the builtin 'object' type, set after builtins are registered.")

(defun %compute-c3-mro (cls)
  "Compute C3 linearization for CLS. Returns a list of py-type objects."
  (if (null (py-type-bases cls))
      ;; Base case: class with no explicit bases
      (if *object-type*
          (if (eq cls *object-type*)
              (list cls)
              (list cls *object-type*))
          (list cls))
      ;; Recursive C3 merge
      (let* ((parent-mros (mapcar #'%compute-c3-mro (py-type-bases cls)))
             (to-merge (append parent-mros (list (copy-list (py-type-bases cls))))))
        (cons cls (%c3-merge to-merge)))))

(defun %c3-merge (seqs)
  "C3 linearization merge step."
  (let ((result '()))
    (loop
      ;; Remove empty lists
      (setf seqs (remove-if #'null seqs))
      (when (null seqs) (return (nreverse result)))
      ;; Find a candidate: head of some list that doesn't appear in tail of any list
      (let ((candidate nil))
        (dolist (seq seqs)
          (let ((head (first seq)))
            (unless (some (lambda (s) (member head (rest s) :test #'eq)) seqs)
              (setf candidate head)
              (return))))
        (unless candidate
          ;; C3 linearization impossible — fall back to DFS
          (return (nreverse (append result (mapcan #'copy-list seqs)))))
        ;; Add candidate to result and remove it from all lists
        (push candidate result)
        (setf seqs (mapcar (lambda (s) (remove candidate s :test #'eq)) seqs))))))

;;; Class hierarchy lookup --------------------------------------------------

(defun %lookup-in-class-hierarchy (cls name)
  "Look up NAME in CLS's dict, then walk bases recursively (DFS). Returns value or NIL, found-p."
  (when (typep cls 'py-type)
    (let ((tdict (py-type-dict cls)))
      (when tdict
        (multiple-value-bind (val found) (gethash name tdict)
          (when found (return-from %lookup-in-class-hierarchy (values val t))))))
    ;; Walk bases
    (dolist (base (py-type-bases cls))
      (multiple-value-bind (val found) (%lookup-in-class-hierarchy base name)
        (when found (return-from %lookup-in-class-hierarchy (values val t))))))
  (values nil nil))

;;; Dunder method dispatch helper -------------------------------------------

(defun %lookup-dunder (obj name)
  "Look up a dunder method NAME in OBJ's class hierarchy. Returns the function or NIL."
  (let ((cls (py-object-class obj)))
    (multiple-value-bind (fn found) (%lookup-in-class-hierarchy cls name)
      (when found fn))))

;;; __repr__ / __str__ ------------------------------------------------------

(defgeneric py-repr (obj)
  (:documentation "Return a CL string — Python __repr__."))

(defgeneric py-str-of (obj)
  (:documentation "Return a CL string — Python __str__."))

;; py-repr default for py-object is defined in the dunder fallbacks section below

(defmethod py-str-of ((obj py-object))
  "Default: check for __str__ in class hierarchy, else use __repr__."
  (let ((str-fn (%lookup-dunder obj "__str__")))
    (when str-fn
      (return-from py-str-of (py-str-value (py-call str-fn obj)))))
  (py-repr obj))

(defmethod py-repr ((obj py-none))   "None")
(defmethod py-str-of ((obj py-none)) "None")
(defmethod py-repr ((obj py-ellipsis))   "Ellipsis")
(defmethod py-str-of ((obj py-ellipsis)) "Ellipsis")

(defmethod py-repr ((obj py-bool))
  (if (py-bool-raw obj) "True" "False"))
(defmethod py-str-of ((obj py-bool))
  (py-repr obj))

(defmethod py-repr ((obj py-int))
  (format nil "~D" (py-int-value obj)))
(defmethod py-str-of ((obj py-int))
  (py-repr obj))

(defun format-py-float (v)
  "Format a double-float the way Python's repr() does."
  (cond
    ;; NaN and Inf must come first — they fail on zerop/floor/etc.
    ((sb-ext:float-nan-p v) "nan")
    ((and (sb-ext:float-infinity-p v) (> v 0)) "inf")
    ((sb-ext:float-infinity-p v) "-inf")
    ;; Special cases
    ((zerop v) (if (minusp (float-sign v)) "-0.0" "0.0"))
    ;; Integers that fit: 3.0, -1.0, etc.
    ((and (= v (floor v)) (< (abs v) 1.0d16))
     (format nil "~,1f" v))
    ;; Small numbers that don't need scientific notation
    ;; Python uses fixed notation when 1e-4 <= |v| < 1e16
    ((and (>= (abs v) 1.0d-4) (< (abs v) 1.0d16))
     ;; Use ~F and strip trailing zeros (keep at least one decimal digit)
     (let* ((s (format nil "~,17f" v))
            ;; Strip trailing zeros after decimal point
            (dot-pos (position #\. s)))
       (when dot-pos
         (let ((end (length s)))
           (loop while (and (> end (+ dot-pos 2))
                            (char= (char s (1- end)) #\0))
                 do (decf end))
           (setf s (subseq s 0 end))))
       s))
    ;; Scientific notation for very large or very small numbers
    (t
     (let* ((exp (floor (log (abs v) 10)))
            (mantissa (/ v (expt 10.0d0 exp)))
            ;; Format mantissa, strip trailing zeros
            (m-str (format nil "~,17f" mantissa))
            (dot-pos (position #\. m-str)))
       (when dot-pos
         (let ((end (length m-str)))
           (loop while (and (> end (+ dot-pos 2))
                            (char= (char m-str (1- end)) #\0))
                 do (decf end))
           (setf m-str (subseq m-str 0 end)))
         ;; If mantissa ends with ".0", strip to just the integer part
         ;; Python: 1e+16 not 1.0e+16
         (when (and (>= (length m-str) 2)
                    (string= (subseq m-str (- (length m-str) 2)) ".0"))
           ;; But only strip if it's exactly X.0 (not X.50 etc.)
           (setf m-str (subseq m-str 0 (- (length m-str) 2)))))
       (format nil "~Ae~:[+~;-~]~2,'0d"
               m-str
               (< exp 0)
               (abs exp))))))

(defmethod py-repr ((obj py-float))
  (format-py-float (py-float-value obj)))
(defmethod py-str-of ((obj py-float))
  (py-repr obj))

(defun %format-py-float (val &key (for-complex nil))
  "Format a double-float like Python. FOR-COMPLEX omits .0 when integer-valued."
  (cond
    ;; Handle NaN
    ((sb-ext:float-nan-p val) "nan")
    ;; Handle Inf
    ((sb-ext:float-infinity-p val)
     (if (> val 0) "inf" "-inf"))
    ((and for-complex (= val (ftruncate val)))
     ;; Complex parts: integer-valued → no decimal (Python prints 1j not 1.0j)
     (format nil "~D" (round val)))
    ((= val (ftruncate val))
     ;; Regular float: always show .0
     (format nil "~D.0" (round val)))
    (t
     ;; Fractional: trim trailing zeros
     (let ((s (string-right-trim "0" (format nil "~F" val))))
       (when (char= (char s (1- (length s))) #\.) (setf s (concatenate 'string s "0")))
       s))))

(defmethod py-repr ((obj py-complex))
  (let* ((z (py-complex-value obj))
         (r (realpart z))
         (i (imagpart z)))
    (if (zerop r)
        (format nil "~Aj" (%format-py-float i :for-complex t))
        (format nil "(~A~Aj)" (%format-py-float r :for-complex t)
                (if (>= i 0)
                    (format nil "+~A" (%format-py-float i :for-complex t))
                    (%format-py-float i :for-complex t))))))
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

(defun %hash-table-values (ht)
  (let ((vals '()))
    (maphash (lambda (k v) (declare (ignore k)) (push v vals)) ht)
    (nreverse vals)))

(defmethod py-repr ((obj py-set))
  (let ((elts (%hash-table-values (py-set-value obj))))
    (if (null elts)
        "set()"
        (format nil "{~{~A~^, ~}}" (mapcar #'py-repr elts)))))
(defmethod py-str-of ((obj py-set)) (py-repr obj))

(defmethod py-repr ((obj py-frozenset))
  (let ((vals (%hash-table-values (py-frozenset-value obj))))
    (if (null vals)
        "frozenset()"
        (format nil "frozenset({~{~A~^, ~}})" (mapcar #'py-repr vals)))))
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

(defmethod py-repr ((obj py-generator))
  (make-py-str "<generator object>"))
(defmethod py-str-of ((obj py-generator)) (py-repr obj))

(defmethod py-repr ((obj py-coroutine))
  (make-py-str "<coroutine object>"))
(defmethod py-str-of ((obj py-coroutine)) (py-repr obj))

(defmethod py-repr ((obj py-iterator))
  "<iterator>")
(defmethod py-str-of ((obj py-iterator)) (py-repr obj))

(defmethod py-repr ((obj py-range))
  (if (= (py-range-step obj) 1)
      (format nil "range(~D, ~D)" (py-range-start obj) (py-range-stop obj))
      (format nil "range(~D, ~D, ~D)"
              (py-range-start obj) (py-range-stop obj) (py-range-step obj))))
(defmethod py-str-of ((obj py-range)) (py-repr obj))

(defmethod py-repr ((obj py-slice))
  (format nil "slice(~A, ~A, ~A)"
          (py-repr (py-slice-start obj))
          (py-repr (py-slice-stop obj))
          (py-repr (py-slice-step obj))))
(defmethod py-str-of ((obj py-slice)) (py-repr obj))

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
;; py-bool-val default for py-object is defined in the dunder fallbacks section below

;;; __eq__ / __ne__ --------------------------------------------------------

(defgeneric py-eq (a b)
  (:documentation "Python == : return CL boolean."))

(defmethod py-eq ((a py-none) (b py-none)) t)
(defmethod py-eq ((a py-bool) (b py-bool))
  (eq (py-bool-raw a) (py-bool-raw b)))
(defmethod py-eq ((a py-bool) (b py-int))
  (= (if (py-bool-raw a) 1 0) (py-int-value b)))
(defmethod py-eq ((a py-int) (b py-bool))
  (= (py-int-value a) (if (py-bool-raw b) 1 0)))
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

;; sequence ordering (lexicographic, element-wise) for tuples and lists
(defun %seq-compare (va vb)
  "Lexicographic comparison of two sequences of py objects.
   Returns -1, 0, or 1."
  (let ((la (length va))
        (lb (length vb)))
    (dotimes (i (min la lb))
      (let ((ai (elt va i))
            (bi (elt vb i)))
        (cond
          ((py-lt ai bi) (return-from %seq-compare -1))
          ((py-lt bi ai) (return-from %seq-compare 1)))))
    (cond ((< la lb) -1)
          ((> la lb) 1)
          (t 0))))

(defmethod py-lt ((a py-tuple) (b py-tuple))
  (= (%seq-compare (py-tuple-value a) (py-tuple-value b)) -1))
(defmethod py-le ((a py-tuple) (b py-tuple))
  (<= (%seq-compare (py-tuple-value a) (py-tuple-value b)) 0))
(defmethod py-gt ((a py-tuple) (b py-tuple))
  (= (%seq-compare (py-tuple-value a) (py-tuple-value b)) 1))
(defmethod py-ge ((a py-tuple) (b py-tuple))
  (>= (%seq-compare (py-tuple-value a) (py-tuple-value b)) 0))

(defmethod py-lt ((a py-list) (b py-list))
  (= (%seq-compare (py-list-value a) (py-list-value b)) -1))
(defmethod py-le ((a py-list) (b py-list))
  (<= (%seq-compare (py-list-value a) (py-list-value b)) 0))
(defmethod py-gt ((a py-list) (b py-list))
  (= (%seq-compare (py-list-value a) (py-list-value b)) 1))
(defmethod py-ge ((a py-list) (b py-list))
  (>= (%seq-compare (py-list-value a) (py-list-value b)) 0))

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

;;; bool → int coercion for arithmetic
;;; Python treats bool as a subclass of int. When bools participate in
;;; arithmetic, they coerce to 0/1.
(defun %bool-to-int (obj)
  "Coerce py-bool to py-int (True→1, False→0). Pass through non-bools."
  (if (typep obj 'py-bool)
      (make-py-int (if (py-bool-raw obj) 1 0))
      obj))

;;; Bool arithmetic — coerce to int and dispatch
(defmethod py-add ((a py-bool) (b py-bool))
  (py-add (%bool-to-int a) (%bool-to-int b)))
(defmethod py-add ((a py-bool) (b py-int))
  (py-add (%bool-to-int a) b))
(defmethod py-add ((a py-int) (b py-bool))
  (py-add a (%bool-to-int b)))
(defmethod py-add ((a py-bool) (b py-float))
  (py-add (%bool-to-int a) b))
(defmethod py-add ((a py-float) (b py-bool))
  (py-add a (%bool-to-int b)))
(defmethod py-sub ((a py-bool) (b py-bool))
  (py-sub (%bool-to-int a) (%bool-to-int b)))
(defmethod py-sub ((a py-bool) (b py-int))
  (py-sub (%bool-to-int a) b))
(defmethod py-sub ((a py-int) (b py-bool))
  (py-sub a (%bool-to-int b)))
(defmethod py-mul ((a py-bool) (b py-bool))
  (py-mul (%bool-to-int a) (%bool-to-int b)))
(defmethod py-mul ((a py-bool) (b py-int))
  (py-mul (%bool-to-int a) b))
(defmethod py-mul ((a py-int) (b py-bool))
  (py-mul a (%bool-to-int b)))
(defmethod py-mul ((a py-bool) (b py-str))
  (py-mul (%bool-to-int a) b))
(defmethod py-truediv ((a py-bool) (b py-bool))
  (py-truediv (%bool-to-int a) (%bool-to-int b)))
(defmethod py-truediv ((a py-bool) (b py-int))
  (py-truediv (%bool-to-int a) b))
(defmethod py-truediv ((a py-int) (b py-bool))
  (py-truediv a (%bool-to-int b)))
(defmethod py-floordiv ((a py-bool) (b py-bool))
  (py-floordiv (%bool-to-int a) (%bool-to-int b)))
(defmethod py-floordiv ((a py-bool) (b py-int))
  (py-floordiv (%bool-to-int a) b))
(defmethod py-floordiv ((a py-int) (b py-bool))
  (py-floordiv a (%bool-to-int b)))
(defmethod py-mod ((a py-bool) (b py-bool))
  (py-mod (%bool-to-int a) (%bool-to-int b)))
(defmethod py-mod ((a py-bool) (b py-int))
  (py-mod (%bool-to-int a) b))
(defmethod py-mod ((a py-int) (b py-bool))
  (py-mod a (%bool-to-int b)))
(defmethod py-pow ((a py-bool) (b py-bool))
  (py-pow (%bool-to-int a) (%bool-to-int b)))
(defmethod py-pow ((a py-bool) (b py-int))
  (py-pow (%bool-to-int a) b))
(defmethod py-pow ((a py-int) (b py-bool))
  (py-pow a (%bool-to-int b)))
;; Bool bitwise — coerce and dispatch
(defmethod py-and ((a py-bool) (b py-bool))
  (py-and (%bool-to-int a) (%bool-to-int b)))
(defmethod py-and ((a py-bool) (b py-int))
  (py-and (%bool-to-int a) b))
(defmethod py-and ((a py-int) (b py-bool))
  (py-and a (%bool-to-int b)))
(defmethod py-or ((a py-bool) (b py-bool))
  (py-or (%bool-to-int a) (%bool-to-int b)))
(defmethod py-or ((a py-bool) (b py-int))
  (py-or (%bool-to-int a) b))
(defmethod py-or ((a py-int) (b py-bool))
  (py-or a (%bool-to-int b)))
(defmethod py-xor ((a py-bool) (b py-bool))
  (py-xor (%bool-to-int a) (%bool-to-int b)))
(defmethod py-xor ((a py-bool) (b py-int))
  (py-xor (%bool-to-int a) b))
(defmethod py-xor ((a py-int) (b py-bool))
  (py-xor a (%bool-to-int b)))
(defmethod py-lshift ((a py-bool) b)
  (py-lshift (%bool-to-int a) b))
(defmethod py-lshift (a (b py-bool))
  (py-lshift a (%bool-to-int b)))
(defmethod py-rshift ((a py-bool) b)
  (py-rshift (%bool-to-int a) b))
(defmethod py-rshift (a (b py-bool))
  (py-rshift a (%bool-to-int b)))

;; int × int
(defmethod py-add ((a py-int) (b py-int))
  (make-py-int (+ (py-int-value a) (py-int-value b))))
(defmethod py-sub ((a py-int) (b py-int))
  (make-py-int (- (py-int-value a) (py-int-value b))))
(defmethod py-mul ((a py-int) (b py-int))
  (make-py-int (* (py-int-value a) (py-int-value b))))
(defmethod py-truediv ((a py-int) (b py-int))
  (when (zerop (py-int-value b))
    (py-raise "ZeroDivisionError" "division by zero"))
  (make-py-float (/ (float (py-int-value a) 1.0d0)
                    (float (py-int-value b) 1.0d0))))
(defmethod py-floordiv ((a py-int) (b py-int))
  (when (zerop (py-int-value b))
    (py-raise "ZeroDivisionError" "integer division or modulo by zero"))
  (make-py-int (floor (py-int-value a) (py-int-value b))))
(defmethod py-mod ((a py-int) (b py-int))
  (when (zerop (py-int-value b))
    (py-raise "ZeroDivisionError" "integer division or modulo by zero"))
  (make-py-int (mod (py-int-value a) (py-int-value b))))
(defmethod py-pow ((a py-int) (b py-int))
  (let ((av (py-int-value a)) (bv (py-int-value b)))
    (if (< bv 0)
        ;; Negative exponent → float result (Python semantics)
        (make-py-float (expt (float av 1.0d0) bv))
        (make-py-int (expt av bv)))))
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
    (py-raise "ZeroDivisionError" "float division by zero"))
  (make-py-float (/ (py-float-value a) (py-float-value b))))
(defmethod py-floordiv ((a py-float) (b py-float))
  (when (zerop (py-float-value b))
    (py-raise "ZeroDivisionError" "float floor division by zero"))
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

;; float // int and float % int
(defmethod py-floordiv ((a py-float) (b py-int))
  (let ((bv (float (py-int-value b) 1.0d0)))
    (when (zerop bv) (py-raise "ZeroDivisionError" "float floor division by zero"))
    (make-py-float (ffloor (py-float-value a) bv))))
(defmethod py-floordiv ((a py-int) (b py-float))
  (when (zerop (py-float-value b)) (py-raise "ZeroDivisionError" "float floor division by zero"))
  (make-py-float (ffloor (float (py-int-value a) 1.0d0) (py-float-value b))))
(defmethod py-mod ((a py-float) (b py-int))
  (let ((bv (float (py-int-value b) 1.0d0)))
    (when (zerop bv) (py-raise "ZeroDivisionError" "float modulo"))
    (make-py-float (mod (py-float-value a) bv))))
(defmethod py-mod ((a py-int) (b py-float))
  (when (zerop (py-float-value b)) (py-raise "ZeroDivisionError" "float modulo"))
  (make-py-float (mod (float (py-int-value a) 1.0d0) (py-float-value b))))
;;; Complex arithmetic ─────────────────────────────────────────────────────

(defun %to-complex (obj)
  "Coerce a numeric py-object to a CL complex double-float."
  (etypecase obj
    (py-complex (py-complex-value obj))
    (py-float   (complex (py-float-value obj) 0.0d0))
    (py-int     (complex (float (py-int-value obj) 1.0d0) 0.0d0))
    (py-bool    (complex (float (if (py-bool-raw obj) 1 0) 1.0d0) 0.0d0))))

(defmacro %complex-binop (method cl-op)
  `(progn
     ;; complex × complex
     (defmethod ,method ((a py-complex) (b py-complex))
       (make-py-complex (,cl-op (py-complex-value a) (py-complex-value b))))
     ;; complex × int
     (defmethod ,method ((a py-complex) (b py-int))
       (make-py-complex (,cl-op (py-complex-value a) (%to-complex b))))
     ;; int × complex
     (defmethod ,method ((a py-int) (b py-complex))
       (make-py-complex (,cl-op (%to-complex a) (py-complex-value b))))
     ;; complex × float
     (defmethod ,method ((a py-complex) (b py-float))
       (make-py-complex (,cl-op (py-complex-value a) (%to-complex b))))
     ;; float × complex
     (defmethod ,method ((a py-float) (b py-complex))
       (make-py-complex (,cl-op (%to-complex a) (py-complex-value b))))))

(%complex-binop py-add +)
(%complex-binop py-sub -)
(%complex-binop py-mul *)
(%complex-binop py-truediv /)

(defmethod py-pow ((a py-complex) (b py-complex))
  (make-py-complex (expt (py-complex-value a) (py-complex-value b))))
(defmethod py-pow ((a py-complex) (b py-int))
  (make-py-complex (expt (py-complex-value a) (%to-complex b))))
(defmethod py-pow ((a py-int) (b py-complex))
  (make-py-complex (expt (%to-complex a) (py-complex-value b))))
(defmethod py-pow ((a py-complex) (b py-float))
  (make-py-complex (expt (py-complex-value a) (%to-complex b))))
(defmethod py-pow ((a py-float) (b py-complex))
  (make-py-complex (expt (%to-complex a) (py-complex-value b))))

;;; String % formatting (printf-style)
(defmethod py-mod ((a py-str) (b py-tuple))
  "Python string % formatting with tuple of args."
  (make-py-str (%py-string-format (py-str-value a) (coerce (py-tuple-value b) 'list))))

(defmethod py-mod ((a py-str) b)
  "Python string % formatting with single arg."
  (make-py-str (%py-string-format (py-str-value a) (list b))))

(defun %py-string-format (fmt args)
  "Implement Python %-style string formatting."
  (let ((result (make-array 0 :element-type 'character :fill-pointer 0 :adjustable t))
        (i 0)
        (arg-idx 0))
    (loop while (< i (length fmt)) do
      (let ((ch (char fmt i)))
        (if (and (char= ch #\%) (< (1+ i) (length fmt)))
            (progn
              (incf i)
              (let ((spec (char fmt i)))
                (case spec
                  (#\s (vector-push-extend-string result (py-str-of (nth arg-idx args)))
                       (incf arg-idx))
                  (#\d (vector-push-extend-string result
                         (write-to-string (py-int-value (nth arg-idx args))))
                       (incf arg-idx))
                  (#\f (vector-push-extend-string result
                         (format nil "~F" (if (typep (nth arg-idx args) 'py-float)
                                              (py-float-value (nth arg-idx args))
                                              (float (py-int-value (nth arg-idx args)) 1.0d0))))
                       (incf arg-idx))
                  (#\r (vector-push-extend-string result (py-repr (nth arg-idx args)))
                       (incf arg-idx))
                  (#\x (vector-push-extend-string result
                         (format nil "~x" (py-int-value (nth arg-idx args))))
                       (incf arg-idx))
                  (#\% (vector-push-extend #\% result))
                  (otherwise (vector-push-extend #\% result)
                             (vector-push-extend spec result)))
                (incf i)))
            (progn (vector-push-extend ch result) (incf i)))))
    (coerce result 'string)))

(defun vector-push-extend-string (vec str)
  "Push all characters of STR onto adjustable VEC."
  (loop for ch across str do (vector-push-extend ch vec)))

;; int ** float → float
(defmethod py-pow ((a py-int) (b py-float))
  (make-py-float (expt (float (py-int-value a) 1.0d0) (py-float-value b))))
(defmethod py-pow ((a py-float) (b py-int))
  (make-py-float (expt (py-float-value a) (float (py-int-value b) 1.0d0))))

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

;; set operations: & (intersection), | (union), ^ (symmetric difference), - (difference)
(defmethod py-and ((a py-set) (b py-set))
  (let ((ha (py-set-value a))
        (hb (py-set-value b))
        (result (make-hash-table :test #'equal)))
    (maphash (lambda (k v)
               (when (nth-value 1 (gethash k hb))
                 (setf (gethash k result) v)))
             ha)
    (make-instance 'py-set :value result)))

(defmethod py-or ((a py-set) (b py-set))
  (let ((ha (py-set-value a))
        (hb (py-set-value b))
        (result (make-hash-table :test #'equal)))
    (maphash (lambda (k v) (setf (gethash k result) v)) ha)
    (maphash (lambda (k v) (setf (gethash k result) v)) hb)
    (make-instance 'py-set :value result)))

(defmethod py-xor ((a py-set) (b py-set))
  (let ((ha (py-set-value a))
        (hb (py-set-value b))
        (result (make-hash-table :test #'equal)))
    (maphash (lambda (k v)
               (unless (nth-value 1 (gethash k hb))
                 (setf (gethash k result) v)))
             ha)
    (maphash (lambda (k v)
               (unless (nth-value 1 (gethash k ha))
                 (setf (gethash k result) v)))
             hb)
    (make-instance 'py-set :value result)))

(defmethod py-sub ((a py-set) (b py-set))
  (let ((ha (py-set-value a))
        (hb (py-set-value b))
        (result (make-hash-table :test #'equal)))
    (maphash (lambda (k v)
               (unless (nth-value 1 (gethash k hb))
                 (setf (gethash k result) v)))
             ha)
    (make-instance 'py-set :value result)))

;;; unary ------------------------------------------------------------------

(defgeneric py-neg (a) (:documentation "Python -a."))
(defgeneric py-pos (a) (:documentation "Python +a."))
(defgeneric py-abs (a) (:documentation "Python abs(a)."))
(defgeneric py-invert (a) (:documentation "Python ~a."))

(defmethod py-neg ((a py-bool))  (py-neg (%bool-to-int a)))
(defmethod py-pos ((a py-bool))  (py-pos (%bool-to-int a)))
(defmethod py-abs ((a py-bool))  (py-abs (%bool-to-int a)))
(defmethod py-invert ((a py-bool)) (py-invert (%bool-to-int a)))
(defmethod py-neg ((a py-int))   (make-py-int   (- (py-int-value a))))
(defmethod py-pos ((a py-int))   (make-py-int   (py-int-value a)))
(defmethod py-abs ((a py-int))   (make-py-int   (abs (py-int-value a))))
(defmethod py-invert ((a py-int)) (make-py-int  (lognot (py-int-value a))))
(defmethod py-neg ((a py-float)) (make-py-float (- (py-float-value a))))
(defmethod py-pos ((a py-float)) (make-py-float (py-float-value a)))
(defmethod py-abs ((a py-float)) (make-py-float (abs (py-float-value a))))
(defmethod py-neg ((a py-complex)) (make-py-complex (- (py-complex-value a))))
(defmethod py-neg ((a py-object))
  (let ((fn (%lookup-dunder a "__neg__")))
    (if fn (py-call fn a)
        (py-raise "TypeError" "bad operand type for unary -"))))
(defmethod py-pos ((a py-object))
  (let ((fn (%lookup-dunder a "__pos__")))
    (if fn (py-call fn a)
        (py-raise "TypeError" "bad operand type for unary +"))))
(defmethod py-abs ((a py-object))
  (let ((fn (%lookup-dunder a "__abs__")))
    (if fn (py-call fn a)
        (py-raise "TypeError" "bad operand type for abs()"))))
(defmethod py-invert ((a py-object))
  (let ((fn (%lookup-dunder a "__invert__")))
    (if fn (py-call fn a)
        (py-raise "TypeError" "bad operand type for unary ~"))))
(defmethod py-abs ((a py-complex)) (make-py-float (abs (py-complex-value a))))

;;; attribute access -------------------------------------------------------

(defgeneric py-getattr (obj name)
  (:documentation "Python getattr(obj, name) — name is a CL string."))

(defgeneric py-setattr (obj name value)
  (:documentation "Python setattr(obj, name, value)."))

(defgeneric py-delattr (obj name)
  (:documentation "Python delattr(obj, name)."))

;;; ─── Property descriptor methods ────────────────────────────────────────────

(defmethod py-getattr ((obj py-property-wrapper) (name string))
  (cond
    ((string= name "setter")
     ;; Return a callable that creates a new property with the same fget and the given fset
     (make-py-function
      :name "property.setter"
      :cl-fn (lambda (&rest args)
               (make-instance 'py-property-wrapper
                              :fget (py-property-fget obj)
                              :fset (first args)))))
    ((string= name "fget") (or (py-property-fget obj) +py-none+))
    ((string= name "fset") (or (py-property-fset obj) +py-none+))
    (t (call-next-method))))

;;; ─── String methods ─────────────────────────────────────────────────────────

(defmethod py-getattr ((obj py-str) (name string))
  "Return callable method objects for common str methods."
  (let ((s (py-str-value obj)))
    (flet ((wrap (fn) (make-py-function :name name :cl-fn fn)))
      (cond
        ((string= name "upper")
         (wrap (lambda () (make-py-str (string-upcase s)))))
        ((string= name "lower")
         (wrap (lambda () (make-py-str (string-downcase s)))))
        ((string= name "strip")
         (wrap (lambda (&optional chars)
                 (let ((cs (if chars (py-str-value chars) nil)))
                   (make-py-str (string-trim (or cs '(#\Space #\Tab #\Newline #\Return)) s))))))
        ((string= name "lstrip")
         (wrap (lambda (&optional chars)
                 (let ((cs (if chars (py-str-value chars) nil)))
                   (make-py-str (string-left-trim (or cs '(#\Space #\Tab #\Newline #\Return)) s))))))
        ((string= name "rstrip")
         (wrap (lambda (&optional chars)
                 (let ((cs (if chars (py-str-value chars) nil)))
                   (make-py-str (string-right-trim (or cs '(#\Space #\Tab #\Newline #\Return)) s))))))
        ((string= name "split")
         (wrap (lambda (&optional sep-obj)
                 (let ((parts
                         (if (and sep-obj (typep sep-obj 'py-str))
                             ;; Split by specific separator
                             (let ((sep (py-str-value sep-obj))
                                   (result '())
                                   (start 0))
                               (loop
                                 (let ((pos (search sep s :start2 start)))
                                   (if pos
                                       (progn
                                         (push (subseq s start pos) result)
                                         (setf start (+ pos (length sep))))
                                       (progn
                                         (push (subseq s start) result)
                                         (return)))))
                               (nreverse result))
                             ;; Split on whitespace (default)
                             (let ((result '()) (i 0) (len (length s)))
                               (loop while (< i len) do
                                 ;; Skip whitespace
                                 (loop while (and (< i len)
                                                  (member (char s i) '(#\Space #\Tab #\Newline #\Return)))
                                       do (incf i))
                                 (when (>= i len) (return))
                                 ;; Collect non-whitespace
                                 (let ((start i))
                                   (loop while (and (< i len)
                                                    (not (member (char s i) '(#\Space #\Tab #\Newline #\Return))))
                                         do (incf i))
                                   (push (subseq s start i) result)))
                               (nreverse result)))))
                   (make-py-list (mapcar #'make-py-str parts))))))
        ((string= name "join")
         (wrap (lambda (iterable)
                 (let ((items '())
                       (iter (py-iter iterable)))
                   (handler-case
                       (loop (push (py-str-value (py-next iter)) items))
                     (stop-iteration () nil))
                   (make-py-str (format nil "~{~A~^~A~}"
                                        (loop for (item . rest) on (nreverse items)
                                              collect item
                                              when rest collect s)))))))
        ((string= name "replace")
         (wrap (lambda (old new &optional count-obj)
                 (let ((old-s (py-str-value old))
                       (new-s (py-str-value new))
                       (max-count (if count-obj (py-int-value count-obj) -1))
                       (result (make-array 0 :element-type 'character :fill-pointer 0 :adjustable t))
                       (start 0)
                       (replacements 0))
                   (loop
                     (when (and (>= max-count 0) (>= replacements max-count))
                       (loop for i from start below (length s) do
                         (vector-push-extend (char s i) result))
                       (return))
                     (let ((pos (search old-s s :start2 start)))
                       (if pos
                           (progn
                             (loop for i from start below pos do
                               (vector-push-extend (char s i) result))
                             (loop for c across new-s do
                               (vector-push-extend c result))
                             (setf start (+ pos (length old-s)))
                             (incf replacements))
                           (progn
                             (loop for i from start below (length s) do
                               (vector-push-extend (char s i) result))
                             (return)))))
                   (make-py-str (coerce result 'string))))))
        ((string= name "startswith")
         (wrap (lambda (prefix) (py-bool-from-cl
                                 (let ((p (py-str-value prefix)))
                                   (and (>= (length s) (length p))
                                        (string= s p :end1 (length p))))))))
        ((string= name "endswith")
         (wrap (lambda (suffix) (py-bool-from-cl
                                 (let ((sf (py-str-value suffix)))
                                   (and (>= (length s) (length sf))
                                        (string= s sf :start1 (- (length s) (length sf)))))))))
        ((string= name "find")
         (wrap (lambda (sub &optional start-obj end-obj)
                 (let* ((sub-s (py-str-value sub))
                        (start-i (if start-obj (py-int-value start-obj) 0))
                        (end-i (if end-obj (py-int-value end-obj) (length s)))
                        (pos (search sub-s s :start2 start-i :end2 end-i)))
                   (make-py-int (or pos -1))))))
        ((string= name "count")
         (wrap (lambda (sub)
                 (let ((sub-s (py-str-value sub))
                       (count 0) (start 0))
                   (loop
                     (let ((pos (search sub-s s :start2 start)))
                       (if pos
                           (progn (incf count) (setf start (+ pos (max 1 (length sub-s)))))
                           (return (make-py-int count)))))))))
        ((string= name "format")
         (wrap (lambda (&rest format-args)
                 ;; Simple positional format: "{}".format(val) or "{0}{1}".format(a, b)
                 (let ((result (make-array 0 :element-type 'character :fill-pointer 0 :adjustable t))
                       (i 0) (auto-idx 0) (len (length s)))
                   (loop while (< i len) do
                     (if (and (char= (char s i) #\{) (< (1+ i) len))
                         (if (char= (char s (1+ i)) #\})
                             ;; {} — auto-numbered
                             (progn
                               (when (< auto-idx (length format-args))
                                 (loop for c across (py-str-of (nth auto-idx format-args))
                                       do (vector-push-extend c result)))
                               (incf auto-idx)
                               (incf i 2))
                             ;; {N} — explicitly numbered
                             (let ((close-pos (position #\} s :start (1+ i))))
                               (if close-pos
                                   (let* ((spec (subseq s (1+ i) close-pos))
                                          (idx (ignore-errors (parse-integer spec))))
                                     (if idx
                                         (progn
                                           (when (< idx (length format-args))
                                             (loop for c across (py-str-of (nth idx format-args))
                                                   do (vector-push-extend c result)))
                                           (setf i (1+ close-pos)))
                                         (progn
                                           (vector-push-extend (char s i) result)
                                           (incf i))))
                                   (progn
                                     (vector-push-extend (char s i) result)
                                     (incf i)))))
                         (progn
                           (vector-push-extend (char s i) result)
                           (incf i))))
                   (make-py-str (coerce result 'string))))))
        ((string= name "capitalize")
         (wrap (lambda ()
                 (if (zerop (length s))
                     (make-py-str "")
                     (make-py-str (concatenate 'string
                                               (string (char-upcase (char s 0)))
                                               (string-downcase (subseq s 1))))))))
        ((string= name "title")
         (wrap (lambda ()
                 (let ((result (make-array (length s) :element-type 'character))
                       (cap-next t))
                   (loop for i below (length s)
                         for c = (char s i) do
                         (cond
                           ((not (alphanumericp c))
                            (setf (aref result i) c)
                            (setf cap-next t))
                           (cap-next
                            (setf (aref result i) (char-upcase c))
                            (setf cap-next nil))
                           (t
                            (setf (aref result i) (char-downcase c)))))
                   (make-py-str (coerce result 'string))))))
        ((string= name "isdigit")
         (wrap (lambda ()
                 (py-bool-from-cl (and (plusp (length s))
                                       (every #'digit-char-p s))))))
        ((string= name "isalpha")
         (wrap (lambda ()
                 (py-bool-from-cl (and (plusp (length s))
                                       (every #'alpha-char-p s))))))
        ((string= name "zfill")
         (wrap (lambda (width-obj)
                 (let* ((width (py-int-value width-obj))
                        (len (length s))
                        (has-sign (and (plusp len)
                                       (or (char= (char s 0) #\+)
                                           (char= (char s 0) #\-)))))
                   (if (<= width len)
                       (make-py-str s)
                       (let ((pad (make-string (- width len) :initial-element #\0)))
                         (if has-sign
                             (make-py-str (concatenate 'string
                                                       (string (char s 0))
                                                       pad
                                                       (subseq s 1)))
                             (make-py-str (concatenate 'string pad s)))))))))
        (t (call-next-method))))))

;;; ─── List methods ──────────────────────────────────────────────────────────

(defmethod py-getattr ((obj py-list) (name string))
  "Return callable method objects for common list methods."
  (let ((vec (py-list-value obj)))
    (flet ((wrap (fn) (make-py-function :name name :cl-fn fn)))
      (cond
        ((string= name "append")
         (wrap (lambda (item) (vector-push-extend item vec) +py-none+)))
        ((string= name "extend")
         (wrap (lambda (iterable)
                 (let ((iter (py-iter iterable)))
                   (handler-case
                       (loop (vector-push-extend (py-next iter) vec))
                     (stop-iteration () nil)))
                 +py-none+)))
        ((string= name "insert")
         (wrap (lambda (idx-obj item)
                 (let* ((len (length vec))
                        (idx (py-int-value idx-obj))
                        (i (max 0 (min (if (< idx 0) (+ len idx) idx) len))))
                   ;; Extend the vector first
                   (vector-push-extend +py-none+ vec)
                   ;; Shift elements right
                   (loop for j from (1- (length vec)) above i
                         do (setf (aref vec j) (aref vec (1- j))))
                   (setf (aref vec i) item))
                 +py-none+)))
        ((string= name "remove")
         (wrap (lambda (item)
                 (let ((pos (position-if (lambda (x) (py-eq x item)) vec)))
                   (if pos
                       (progn
                         (loop for i from pos below (1- (length vec))
                               do (setf (aref vec i) (aref vec (1+ i))))
                         (decf (fill-pointer vec))
                         +py-none+)
                       (py-raise "ValueError" "list.remove(x): x not in list"))))))
        ((string= name "pop")
         (wrap (lambda (&optional idx-obj)
                 (let* ((len (length vec))
                        (idx (if idx-obj (py-int-value idx-obj) -1))
                        (i (if (< idx 0) (+ len idx) idx)))
                   (when (or (< i 0) (>= i len))
                     (py-raise "IndexError" "pop index out of range"))
                   (let ((val (aref vec i)))
                     (loop for j from i below (1- len)
                           do (setf (aref vec j) (aref vec (1+ j))))
                     (decf (fill-pointer vec))
                     val)))))
        ((string= name "clear")
         (wrap (lambda () (setf (fill-pointer vec) 0) +py-none+)))
        ((string= name "index")
         (wrap (lambda (item &optional start-obj end-obj)
                 (let ((start (if start-obj (py-int-value start-obj) 0))
                       (end (if end-obj (py-int-value end-obj) (length vec))))
                   (loop for i from start below end
                         when (py-eq (aref vec i) item)
                           do (return (make-py-int i))
                         finally (py-raise "ValueError" "~A is not in list" (py-repr item)))))))
        ((string= name "count")
         (wrap (lambda (item)
                 (make-py-int (count-if (lambda (x) (py-eq x item)) vec)))))
        ((string= name "sort")
         (wrap (lambda ()
                 ;; Simple in-place sort using py-lt
                 (let ((items (coerce vec 'list)))
                   (setf items (sort items (lambda (a b) (py-lt a b))))
                   (loop for i from 0 for item in items do (setf (aref vec i) item)))
                 +py-none+)))
        ((string= name "reverse")
         (wrap (lambda ()
                 (let ((len (length vec)))
                   (loop for i below (floor len 2)
                         do (rotatef (aref vec i) (aref vec (- len 1 i)))))
                 +py-none+)))
        ((string= name "copy")
         (wrap (lambda ()
                 (make-py-list (coerce vec 'list)))))
        ((string= name "__len__")
         (wrap (lambda () (make-py-int (length vec)))))
        ((string= name "__contains__")
         (wrap (lambda (item)
                 (py-bool-from-cl (find-if (lambda (x) (py-eq x item)) vec)))))
        ((string= name "__class__")
         (make-py-type :name "list"))
        (t (call-next-method))))))

;;; ─── Dict methods ──────────────────────────────────────────────────────────

(defmethod py-getattr ((obj py-dict) (name string))
  (let ((ht (py-dict-value obj)))
    (flet ((wrap (fn) (make-py-function :name name :cl-fn fn)))
      (cond
        ((string= name "keys")
         (wrap (lambda ()
                 (make-py-list (mapcar #'cl-to-py (%hash-table-keys ht))))))
        ((string= name "values")
         (wrap (lambda ()
                 (make-py-list (%hash-table-values ht)))))
        ((string= name "items")
         (wrap (lambda ()
                 (let ((items '()))
                   (maphash (lambda (k v)
                              (push (make-py-tuple (list (cl-to-py k) v)) items))
                            ht)
                   (make-py-list (nreverse items))))))
        ((string= name "get")
         (wrap (lambda (key &optional default)
                 (multiple-value-bind (val found) (gethash (dict-hash-key key) ht)
                   (if found val (or default +py-none+))))))
        ((string= name "update")
         (wrap (lambda (other)
                 (maphash (lambda (k v) (setf (gethash k ht) v))
                          (py-dict-value other))
                 +py-none+)))
        ((string= name "pop")
         (wrap (lambda (key &optional default)
                 (let ((k (dict-hash-key key)))
                   (multiple-value-bind (val found) (gethash k ht)
                     (if found
                         (progn (remhash k ht) val)
                         (if default default
                             (py-raise "KeyError" "~A" (py-repr key)))))))))
        ((string= name "setdefault")
         (wrap (lambda (key &optional default)
                 (let ((k (dict-hash-key key)))
                   (multiple-value-bind (val found) (gethash k ht)
                     (if found val
                         (let ((d (or default +py-none+)))
                           (setf (gethash k ht) d)
                           d)))))))
        ((string= name "__contains__")
         (wrap (lambda (key)
                 (py-bool-from-cl (nth-value 1 (gethash (dict-hash-key key) ht))))))
        (t (call-next-method))))))

;;; ─── Set methods ───────────────────────────────────────────────────────────

(defmethod py-getattr ((obj py-set) (name string))
  (let ((ht (py-set-value obj)))
    (flet ((wrap (fn) (make-py-function :name name :cl-fn fn)))
      (cond
        ((string= name "add")
         (wrap (lambda (item)
                 (setf (gethash (set-hash-key item) ht) item)
                 +py-none+)))
        ((string= name "discard")
         (wrap (lambda (item)
                 (remhash (set-hash-key item) ht)
                 +py-none+)))
        ((string= name "remove")
         (wrap (lambda (item)
                 (unless (remhash (set-hash-key item) ht)
                   (py-raise "KeyError" "~A" (py-repr item)))
                 +py-none+)))
        ((string= name "__contains__")
         (wrap (lambda (item)
                 (py-bool-from-cl (nth-value 1 (gethash (set-hash-key item) ht))))))
        (t (call-next-method))))))

;;; ─── Frozenset methods ─────────────────────────────────────────────────────

(defmethod py-getattr ((obj py-frozenset) (name string))
  (let ((ht (py-frozenset-value obj)))
    (flet ((wrap (fn) (make-py-function :name name :cl-fn fn)))
      (cond
        ((string= name "__contains__")
         (wrap (lambda (item)
                 (py-bool-from-cl (nth-value 1 (gethash (set-hash-key item) ht))))))
        (t (call-next-method))))))

(defmethod py-getattr ((obj py-function) (name string))
  ;; Built-in attributes for function objects
  (cond
    ((string= name "__name__") (make-py-str (or (py-function-name obj) "<lambda>")))
    ((string= name "__doc__")  (let ((doc (py-function-docstring obj)))
                                (if doc (make-py-str doc) +py-none+)))
    ((string= name "__annotations__") (make-py-dict))  ; stub — annotations not tracked yet
    (t (call-next-method))))

(defmethod py-getattr ((obj py-type) (name string))
  ;; Built-in attributes for type objects
  (cond
    ((string= name "__name__") (make-py-str (py-type-name obj)))
    ((string= name "__mro__")
     ;; Compute C3-linearized MRO
     (make-py-tuple (%compute-c3-mro obj)))
    (t
     ;; Check the type's own dict and parent classes
     (multiple-value-bind (val found) (%lookup-in-class-hierarchy obj name)
       (when found
         (cond
           ((typep val 'py-staticmethod-wrapper)
            (return-from py-getattr (py-staticmethod-function val)))
           ((typep val 'py-classmethod-wrapper)
            (return-from py-getattr
              (make-instance 'py-method :function (py-classmethod-function val) :self obj)))
           (t (return-from py-getattr val)))))
     (call-next-method))))

(defmethod py-setattr ((obj py-type) (name string) value)
  ;; Set attribute in the type's dict (class attributes)
  (let ((tdict (py-type-dict obj)))
    (unless tdict
      (setf tdict (make-hash-table :test #'equal))
      (setf (py-type-dict obj) tdict))
    (setf (gethash name tdict) value)))

(defun %is-data-descriptor-p (val)
  "Check if VAL is a data descriptor (has __set__ or __delete__)."
  (and (typep val 'py-object)
       (let ((cls (py-object-class val)))
         (when (typep cls 'py-type)
           (or (gethash "__set__" (py-type-dict cls))
               (gethash "__delete__" (py-type-dict cls)))))))

(defun %invoke-descriptor-get (desc obj cls)
  "Invoke __get__ on a descriptor if it has one, else return desc."
  (when (typep desc 'py-object)
    (let ((get-fn (%lookup-dunder desc "__get__")))
      (when get-fn
        (return-from %invoke-descriptor-get
          (py-call get-fn desc obj (or cls +py-none+))))))
  desc)

(defmethod py-getattr ((obj py-object) (name string))
  ;; 1. Check class dict for data descriptors (priority over instance dict)
  (let ((cls (py-object-class obj)))
    (multiple-value-bind (val found) (%lookup-in-class-hierarchy cls name)
      (when found
        ;; Data descriptor takes priority
        (when (%is-data-descriptor-p val)
          (return-from py-getattr (%invoke-descriptor-get val obj cls))))))
  ;; 2. Check instance dict
  (let ((d (py-object-dict obj)))
    (when (hash-table-p d)
      (multiple-value-bind (val found) (gethash name d)
        (when found (return-from py-getattr val)))))
  ;; 3. Check class dict for non-data descriptors, methods, etc.
  (let ((cls (py-object-class obj)))
    (multiple-value-bind (val found) (%lookup-in-class-hierarchy cls name)
      (when found
        (cond
          ;; @staticmethod — return unwrapped function (no self binding)
          ((typep val 'py-staticmethod-wrapper)
           (return-from py-getattr (py-staticmethod-function val)))
          ;; @classmethod — bind the class, not the instance
          ((typep val 'py-classmethod-wrapper)
           (return-from py-getattr
             (make-instance 'py-method :function (py-classmethod-function val) :self cls)))
          ;; @property — call the getter
          ((typep val 'py-property-wrapper)
           (let ((fget (py-property-fget val)))
             (if fget
                 (return-from py-getattr (py-call fget obj))
                 (py-raise "AttributeError" "unreadable attribute"))))
          ;; Non-data descriptor with __get__
          ((and (typep val 'py-object) (%lookup-dunder val "__get__"))
           (return-from py-getattr (%invoke-descriptor-get val obj cls)))
          ;; Regular function — return a bound method
          ((typep val 'py-function)
           (return-from py-getattr
             (make-instance 'py-method :function val :self obj)))
          ;; Anything else (class attributes, etc.)
          (t (return-from py-getattr val))))))
  (py-raise "AttributeError" "'~A' object has no attribute '~A'"
            (let ((cls (py-object-class obj)))
              (if (typep cls 'py-type) (py-type-name cls) (class-name (class-of obj))))
            name))

(defmethod py-setattr ((obj py-object) (name string) value)
  ;; Check for @property setter or data descriptor __set__ in class hierarchy
  (let ((cls (py-object-class obj)))
    (multiple-value-bind (val found) (%lookup-in-class-hierarchy cls name)
      (when found
        (cond
          ((typep val 'py-property-wrapper)
           (let ((fset (py-property-fset val)))
             (if fset
                 (progn (py-call fset obj value) (return-from py-setattr +py-none+))
                 (py-raise "AttributeError" "can't set attribute"))))
          ;; Data descriptor with __set__
          ((and (typep val 'py-object)
                (let ((set-fn (%lookup-dunder val "__set__")))
                  (when set-fn
                    (py-call set-fn val obj value)
                    t)))
           (return-from py-setattr +py-none+))))))
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
        (py-raise "AttributeError" "module '~A' has no attribute '~A'"
                  (py-module-name obj) name))))

(defmethod py-setattr ((obj py-module) (name string) value)
  (setf (gethash name (py-module-dict obj)) value))

;;; subscript access -------------------------------------------------------

(defun resolve-slice-index (idx len default)
  "Resolve a single slice index: if py-none, return DEFAULT; if py-int, return CL integer."
  (cond
    ((eq idx +py-none+) default)
    ((typep idx 'py-int) (py-int-value idx))
    (t (py-raise "TypeError" "slice indices must be integers or None, not ~A"
                 (py-type-name (py-type-of idx))))))

(defun compute-slice-indices (slice-obj len)
  "Compute (start stop step) for a py-slice given sequence length LEN.
   Faithfully implements CPython's PySlice_Unpack + PySlice_AdjustIndices."
  (let ((step-val (py-slice-step slice-obj))
        (start-val (py-slice-start slice-obj))
        (stop-val (py-slice-stop slice-obj)))
    ;; 1. Unpack step
    (let ((step (if (eq step-val +py-none+) 1 (py-int-value step-val))))
      (when (zerop step)
        (py-raise "ValueError" "slice step cannot be zero"))
      ;; 2. Unpack start
      (let ((start (cond
                     ((eq start-val +py-none+)
                      (if (> step 0) 0 (1- len)))
                     (t (let ((v (py-int-value start-val)))
                          (if (< v 0)
                              (max (+ len v) 0)
                              (min v len)))))))
        ;; 3. Unpack stop
        (let ((stop (cond
                      ((eq stop-val +py-none+)
                       (if (> step 0) len -1))
                      (t (let ((v (py-int-value stop-val)))
                           (if (< v 0)
                               (max (+ len v) -1)
                               (min v len)))))))
          (values start stop step))))))

(defun slice-collect (vec len slice-obj element-fn)
  "Collect elements from a sequence of length LEN using SLICE-OBJ.
   ELEMENT-FN is called with the index to get each element."
  (multiple-value-bind (start stop step) (compute-slice-indices slice-obj len)
    (let ((result '()))
      (if (> step 0)
          (loop for i from start below stop by step
                do (push (funcall element-fn i) result))
          (loop for i from start above stop by (- step)
                do (push (funcall element-fn i) result)))
      (nreverse result))))

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
        (py-raise "IndexError" "list index out of range")
        (aref vec i))))

(defmethod py-setitem ((obj py-list) (key py-int) value)
  (let* ((vec (py-list-value obj))
         (len (length vec))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (py-raise "IndexError" "list assignment index out of range")
        (setf (aref vec i) value))))

(defmethod py-delitem ((obj py-list) (key py-int))
  (let* ((vec (py-list-value obj))
         (len (length vec))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (py-raise "IndexError" "list assignment index out of range")
        (progn
          (loop for j from i below (1- len)
                do (setf (aref vec j) (aref vec (1+ j))))
          (decf (fill-pointer vec))))))

(defmethod py-getitem ((obj py-list) (key py-slice))
  (let* ((vec (py-list-value obj))
         (len (length vec)))
    (make-py-list (slice-collect vec len key (lambda (i) (aref vec i))))))

(defmethod py-setitem ((obj py-list) (key py-slice) value)
  "Slice assignment: x[start:stop] = iterable.  Only step=1 supported for now."
  (let* ((vec (py-list-value obj))
         (len (length vec)))
    (multiple-value-bind (start stop step) (compute-slice-indices key len)
      (declare (ignore step))
      ;; Collect new values from the iterable
      (let ((new-items
              (cond
                ((typep value 'py-list)
                 (coerce (py-list-value value) 'list))
                ((typep value 'py-tuple)
                 (coerce (py-tuple-value value) 'list))
                (t (list value)))))
        ;; Simple case: replace [start..stop) with new-items
        (let* ((before (loop for i from 0 below start collect (aref vec i)))
               (after  (loop for i from stop below len collect (aref vec i)))
               (all    (append before new-items after))
               (new-vec (make-array (length all)
                                    :fill-pointer (length all)
                                    :adjustable t
                                    :initial-contents all)))
          (setf (slot-value obj '%value) new-vec))))))

(defmethod py-delitem ((obj py-list) (key py-slice))
  "Delete a slice from a list: del x[start:stop]."
  (let* ((vec (py-list-value obj))
         (len (length vec)))
    (multiple-value-bind (start stop step) (compute-slice-indices key len)
      (declare (ignore step))
      (let* ((before (loop for i from 0 below start collect (aref vec i)))
             (after  (loop for i from stop below len collect (aref vec i)))
             (all    (append before after))
             (new-vec (make-array (length all)
                                  :fill-pointer (length all)
                                  :adjustable t
                                  :initial-contents all)))
        (setf (slot-value obj '%value) new-vec)))))

(defmethod py-getitem ((obj py-tuple) (key py-int))
  (let* ((vec (py-tuple-value obj))
         (len (length vec))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (py-raise "IndexError" "tuple index out of range")
        (svref vec i))))

(defmethod py-getitem ((obj py-tuple) (key py-slice))
  (let* ((vec (py-tuple-value obj))
         (len (length vec)))
    (make-py-tuple (slice-collect vec len key (lambda (i) (svref vec i))))))

(defmethod py-getitem ((obj py-str) (key py-int))
  (let* ((s   (py-str-value obj))
         (len (length s))
         (idx (py-int-value key))
         (i   (if (< idx 0) (+ len idx) idx)))
    (if (or (< i 0) (>= i len))
        (py-raise "IndexError" "string index out of range")
        (make-py-str (string (char s i))))))

(defmethod py-getitem ((obj py-str) (key py-slice))
  (let* ((s   (py-str-value obj))
         (len (length s)))
    (make-py-str (coerce (slice-collect s len key (lambda (i) (char s i))) 'string))))

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
      (py-raise "KeyError" "~A" (py-repr key)))
    val))

(defmethod py-setitem ((obj py-dict) key value)
  (setf (gethash (dict-hash-key key) (py-dict-value obj)) value))

(defmethod py-delitem ((obj py-dict) key)
  (unless (remhash (dict-hash-key key) (py-dict-value obj))
    (py-raise "KeyError" "~A" (py-repr key))))

(defmethod py-delitem ((obj py-object) key)
  (let ((fn (%lookup-dunder obj "__delitem__")))
    (if fn (py-call fn obj key)
        (py-raise "TypeError" "'~A' object doesn't support item deletion"
                  (class-name (class-of obj))))))

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

(defmethod py-iter ((obj py-generator)) obj)

(defmethod py-next ((obj py-generator))
  (py-generator-send obj :next-signal))

(defmethod py-getattr ((obj py-generator) (name string))
  (cond
    ((string= name "send")
     (make-py-function :name "send"
                       :cl-fn (lambda (value)
                                 (py-generator-send obj value))))
    ((string= name "close")
     (make-py-function :name "close"
                       :cl-fn (lambda ()
                                 (setf (py-generator-finished obj) t)
                                 +py-none+)))
    ((string= name "__next__")
     (make-py-function :name "__next__"
                       :cl-fn (lambda ()
                                 (py-next obj))))
    (t (call-next-method))))

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
  (let ((vals (%hash-table-values (py-set-value obj)))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length vals))
           (prog1 (nth i vals) (incf i))
           (error 'stop-iteration))))))

(defmethod py-iter ((obj py-frozenset))
  (let ((vals (%hash-table-values (py-frozenset-value obj)))
        (i 0))
    (make-py-iterator
     (lambda ()
       (if (< i (length vals))
           (prog1 (nth i vals) (incf i))
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

(defmethod py-call ((cls py-type) &rest args)
  "Instantiate a class: create an instance, then call __init__ if defined.
   If the class is in the exception hierarchy, create a py-exception-object.
   Uses MRO lookup to find inherited __init__."
  (let ((name (py-type-name cls)))
    (if (gethash name *exception-hierarchy*)
        ;; Exception class — create py-exception-object directly
        (let ((exc-obj (make-py-exception-object name args)))
          ;; Still call __init__ if user defined one
          (multiple-value-bind (init-fn found)
              (%lookup-in-class-hierarchy cls "__init__")
            (when found
              (apply #'py-call init-fn exc-obj args)))
          exc-obj)
        ;; Normal class
        (let ((instance (make-instance 'py-object
                                       :py-class cls
                                       :py-dict (make-hash-table :test #'equal))))
          (multiple-value-bind (init-fn found)
              (%lookup-in-class-hierarchy cls "__init__")
            (when found
              (apply #'py-call init-fn instance args)))
          instance))))

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
  (nth-value 1 (gethash (set-hash-key item) (py-set-value obj))))

(defmethod py-contains ((obj py-frozenset) item)
  (nth-value 1 (gethash (set-hash-key item) (py-frozenset-value obj))))

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
(defmethod py-type-of ((obj py-coroutine)) "coroutine")
(defmethod py-type-of ((obj py-range))     "range")
(defmethod py-type-of ((obj py-object))    (string (class-name (class-of obj))))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Dunder method fallbacks for user-defined classes
;;;; ═══════════════════════════════════════════════════════════════════════════

(defmethod py-repr ((obj py-object))
  (let ((fn (%lookup-dunder obj "__repr__")))
    (if fn
        (py-str-value (py-call fn obj))
        (format nil "<~A object>"
                (let ((cls (py-object-class obj)))
                  (if (typep cls 'py-type) (py-type-name cls)
                      (class-name (class-of obj))))))))

(defmethod py-len ((obj py-object))
  (let ((fn (%lookup-dunder obj "__len__")))
    (if fn
        (let ((result (py-call fn obj)))
          (if (typep result 'py-int) (py-int-value result) result))
        (py-raise "TypeError" "object of type '~A' has no len()"
                  (class-name (class-of obj))))))

(defmethod py-add ((a py-object) b)
  (let ((fn (%lookup-dunder a "__add__")))
    (if fn (py-call fn a b)
        ;; Try reflected
        (let ((rfn (when (typep b 'py-object) (%lookup-dunder b "__radd__"))))
          (if rfn (py-call rfn b a)
              (py-raise "TypeError" "unsupported operand type(s) for +"))))))

;; Reflected: when left operand is a built-in type and right is py-object with __radd__
(defmethod py-add (a (b py-object))
  (let ((rfn (%lookup-dunder b "__radd__")))
    (if rfn (py-call rfn b a)
        (py-raise "TypeError" "unsupported operand type(s) for +"))))

(defmethod py-sub ((a py-object) b)
  (let ((fn (%lookup-dunder a "__sub__")))
    (if fn (py-call fn a b)
        (let ((rfn (when (typep b 'py-object) (%lookup-dunder b "__rsub__"))))
          (if rfn (py-call rfn b a)
              (py-raise "TypeError" "unsupported operand type(s) for -"))))))

(defmethod py-sub (a (b py-object))
  (let ((rfn (%lookup-dunder b "__rsub__")))
    (if rfn (py-call rfn b a)
        (py-raise "TypeError" "unsupported operand type(s) for -"))))

(defmethod py-mul ((a py-object) b)
  (let ((fn (%lookup-dunder a "__mul__")))
    (if fn (py-call fn a b)
        (let ((rfn (when (typep b 'py-object) (%lookup-dunder b "__rmul__"))))
          (if rfn (py-call rfn b a)
              (py-raise "TypeError" "unsupported operand type(s) for *"))))))

(defmethod py-mul (a (b py-object))
  (let ((rfn (%lookup-dunder b "__rmul__")))
    (if rfn (py-call rfn b a)
        (py-raise "TypeError" "unsupported operand type(s) for *"))))

(defmethod py-eq ((a py-object) (b py-object))
  (let ((fn (%lookup-dunder a "__eq__")))
    (if fn
        (let ((result (py-call fn a b)))
          (py-bool-val result))
        (eq a b))))

(defmethod py-ne ((a py-object) (b py-object))
  (let ((fn (%lookup-dunder a "__ne__")))
    (if fn
        (py-bool-val (py-call fn a b))
        ;; Default: negate __eq__
        (not (py-eq a b)))))

(defmethod py-lt ((a py-object) (b py-object))
  (let ((fn (%lookup-dunder a "__lt__")))
    (if fn
        (let ((result (py-call fn a b)))
          (py-bool-val result))
        (py-raise "TypeError" "'<' not supported"))))

(defmethod py-le ((a py-object) (b py-object))
  (let ((fn (%lookup-dunder a "__le__")))
    (if fn
        (py-bool-val (py-call fn a b))
        (py-raise "TypeError" "'<=' not supported"))))

(defmethod py-gt ((a py-object) (b py-object))
  (let ((fn (%lookup-dunder a "__gt__")))
    (if fn
        (py-bool-val (py-call fn a b))
        (py-raise "TypeError" "'>' not supported"))))

(defmethod py-ge ((a py-object) (b py-object))
  (let ((fn (%lookup-dunder a "__ge__")))
    (if fn
        (py-bool-val (py-call fn a b))
        (py-raise "TypeError" "'>=' not supported"))))

(defmethod py-hash ((obj py-object))
  (let ((fn (%lookup-dunder obj "__hash__")))
    (if fn
        (let ((result (py-call fn obj)))
          (if (typep result 'py-int)
              (py-int-value result)
              (sxhash obj)))
        (sxhash obj))))

(defmethod py-bool-val ((obj py-object))
  (let ((fn (%lookup-dunder obj "__bool__")))
    (if fn
        (let ((result (py-call fn obj)))
          (if (typep result 'py-bool) (py-bool-raw result) (not (null result))))
        ;; Fallback: check __len__, then default True
        (let ((len-fn (%lookup-dunder obj "__len__")))
          (if len-fn
              (let ((result (py-call len-fn obj)))
                (not (and (typep result 'py-int) (zerop (py-int-value result)))))
              t)))))

(defmethod py-getitem ((obj py-object) key)
  (let ((fn (%lookup-dunder obj "__getitem__")))
    (if fn (py-call fn obj key)
        (py-raise "TypeError" "'~A' object is not subscriptable"
                  (class-name (class-of obj))))))

(defmethod py-setitem ((obj py-object) key value)
  (let ((fn (%lookup-dunder obj "__setitem__")))
    (if fn (py-call fn obj key value)
        (py-raise "TypeError" "'~A' object does not support item assignment"
                  (class-name (class-of obj))))))

(defmethod py-contains ((obj py-object) item)
  (let ((fn (%lookup-dunder obj "__contains__")))
    (if fn
        (py-bool-val (py-call fn obj item))
        ;; Fallback: iterate
        (handler-case
            (let ((iter (py-iter obj)))
              (loop (let ((next (py-next iter)))
                      (when (py-eq next item) (return t)))))
          (stop-iteration () nil)))))

(defmethod py-iter ((obj py-object))
  (let ((fn (%lookup-dunder obj "__iter__")))
    (if fn (py-call fn obj)
        (py-raise "TypeError" "'~A' object is not iterable"
                  (class-name (class-of obj))))))

(defmethod py-next ((obj py-object))
  (let ((fn (%lookup-dunder obj "__next__")))
    (if fn (py-call fn obj)
        (py-raise "TypeError" "'~A' object is not an iterator"
                  (class-name (class-of obj))))))

(defmethod py-call ((obj py-object) &rest args)
  (let ((fn (%lookup-dunder obj "__call__")))
    (if fn (apply #'py-call fn obj args)
        (py-raise "TypeError" "'~A' object is not callable"
                  (class-name (class-of obj))))))

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
                   :message msg
                   :py-dict (make-hash-table :test #'equal))))

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

(defmethod py-getattr ((obj py-exception-object) (name string))
  ;; Built-in attributes for exception instances
  (cond
    ((string= name "args")
     (make-py-tuple (or (py-exception-args obj) '())))
    ((string= name "__class__")
     (make-py-type :name (py-exception-class-name obj)))
    (t (call-next-method))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Keyword argument passing for builtins
;;;; ─────────────────────────────────────────────────────────────────────────

(defvar *current-kwargs* nil
  "Alist of (name . py-value) for keyword arguments passed to the current call.
   Set by the evaluator before calling builtins via py-call.")

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
