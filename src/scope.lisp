;;;; scope.lisp — LEGB scope resolution for Clython
;;;;
;;;; Implements Python's Local → Enclosing → Global → Built-in name resolution
;;;; as described in https://docs.python.org/3.12/reference/executionmodel.html

(defpackage :clython.scope
  (:use :cl)
  (:import-from :clython.builtins #:lookup-builtin)
  (:export
   ;; Scope class and accessors
   #:py-scope
   #:scope-bindings
   #:scope-parent
   #:scope-type
   #:scope-globals-declared
   #:scope-nonlocals-declared

   ;; Conditions
   #:py-name-error
   #:py-name-error-name
   #:py-unbound-local-error

   ;; Core operations
   #:scope-lookup
   #:scope-bind
   #:scope-delete

   ;; Scope constructors
   #:make-global-scope
   #:make-local-scope
   #:make-class-scope

   ;; Scope declaration helpers
   #:scope-declare-global
   #:scope-declare-nonlocal))

(in-package :clython.scope)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Conditions
;;;; ─────────────────────────────────────────────────────────────────────────

(define-condition py-name-error (error)
  ((name :initarg :name :reader py-name-error-name))
  (:report (lambda (c stream)
             (format stream "NameError: name ~S is not defined"
                     (py-name-error-name c)))))

(define-condition py-unbound-local-error (py-name-error)
  ()
  (:report (lambda (c stream)
             (format stream "UnboundLocalError: local variable ~S referenced before assignment"
                     (py-name-error-name c)))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; py-scope class
;;;; ─────────────────────────────────────────────────────────────────────────

(defclass py-scope ()
  ((bindings
    :initform (make-hash-table :test #'equal)
    :accessor scope-bindings
    :documentation "String → py-object bindings for this scope.")
   (parent
    :initarg :parent
    :initform nil
    :accessor scope-parent
    :documentation "Enclosing scope, or NIL if this is the outermost scope.")
   (scope-type
    :initarg :scope-type
    :initform :local
    :accessor scope-type
    :documentation "One of :local, :enclosing, :global, :builtin, :class.")
   (globals-declared
    :initform (make-hash-table :test #'equal)
    :accessor scope-globals-declared
    :documentation "Set of names explicitly declared global in this scope.")
   (nonlocals-declared
    :initform (make-hash-table :test #'equal)
    :accessor scope-nonlocals-declared
    :documentation "Set of names explicitly declared nonlocal in this scope.")))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Internal helpers
;;;; ─────────────────────────────────────────────────────────────────────────

(defun %globals-declared-p (scope name)
  "Return T if NAME was declared global in SCOPE."
  (gethash name (scope-globals-declared scope)))

(defun %nonlocals-declared-p (scope name)
  "Return T if NAME was declared nonlocal in SCOPE."
  (gethash name (scope-nonlocals-declared scope)))

(defun %find-global-scope (scope)
  "Walk up the parent chain and return the outermost non-builtin scope."
  (if (or (null (scope-parent scope))
          (eq (scope-type (scope-parent scope)) :builtin))
      scope
      (%find-global-scope (scope-parent scope))))

(defun %find-enclosing-scope (scope name)
  "Search parent scopes (excluding the immediate local) for NAME,
   stopping before the global scope.  Class scopes are skipped per
   Python semantics (inner functions do not inherit class-scope names).
   Returns the scope that binds NAME, or NIL if not found."
  (let ((parent (scope-parent scope)))
    (cond
      ;; Reached global or builtin level — stop
      ((null parent) nil)
      ((member (scope-type parent) '(:global :builtin)) nil)
      ;; Class scopes are invisible to nested function lookups — skip
      ((eq (scope-type parent) :class)
       (%find-enclosing-scope parent name))
      ;; Check this enclosing scope
      ((nth-value 1 (gethash name (scope-bindings parent))) parent)
      ;; Keep climbing
      (t (%find-enclosing-scope parent name)))))

(defun %scope-lookup-raw (scope name)
  "Internal lookup — returns (values value foundp).
   Does NOT signal conditions; the caller decides."
  (gethash name (scope-bindings scope)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Public API
;;;; ─────────────────────────────────────────────────────────────────────────

(defun scope-lookup (scope name)
  "Look up NAME in SCOPE following Python LEGB rules.
   Signals PY-UNBOUND-LOCAL-ERROR if NAME is known local but unbound,
   or PY-NAME-ERROR if NAME cannot be found anywhere."
  (check-type name string)

  ;; 1. Declared global — jump straight to global scope
  (when (%globals-declared-p scope name)
    (let* ((global-scope (%find-global-scope scope))
           (val (gethash name (scope-bindings global-scope))))
      (when val (return-from scope-lookup val))
      ;; Not in global scope — try builtins
      (let ((builtin (lookup-builtin name)))
        (when builtin (return-from scope-lookup builtin)))
      (error 'py-name-error :name name)))

  ;; 2. Declared nonlocal — skip local, search enclosing only
  (when (%nonlocals-declared-p scope name)
    (let ((enc-scope (%find-enclosing-scope scope name)))
      (when enc-scope
        (return-from scope-lookup
          (gethash name (scope-bindings enc-scope))))
      ;; Nonlocal but not found in any enclosing scope
      (error 'py-name-error :name name)))

  ;; 3. L — local scope
  (multiple-value-bind (val foundp)
      (gethash name (scope-bindings scope))
    (when foundp (return-from scope-lookup val)))

  ;; 4. E — enclosing scopes (skip if we are already at global/builtin level)
  (unless (member (scope-type scope) '(:global :builtin))
    (let ((enc-scope (%find-enclosing-scope scope name)))
      (when enc-scope
        (return-from scope-lookup
          (gethash name (scope-bindings enc-scope))))))

  ;; 5. G — global scope
  (let ((global-scope (%find-global-scope scope)))
    (unless (eq global-scope scope)       ; avoid double-checking at global level
      (multiple-value-bind (val foundp)
          (gethash name (scope-bindings global-scope))
        (when foundp (return-from scope-lookup val)))))

  ;; 6. B — built-ins
  (let ((builtin (lookup-builtin name)))
    (when builtin (return-from scope-lookup builtin)))

  ;; Not found anywhere
  (error 'py-name-error :name name))

(defun scope-bind (scope name value)
  "Bind NAME to VALUE in SCOPE.
   If NAME is declared global in SCOPE, the binding is placed in the
   global scope instead.  Returns VALUE."
  (check-type name string)
  (let ((target-scope
          (if (%globals-declared-p scope name)
              (%find-global-scope scope)
              scope)))
    (setf (gethash name (scope-bindings target-scope)) value)
    value))

(defun scope-delete (scope name)
  "Remove the binding for NAME from SCOPE (or the global scope if declared global).
   Signals PY-NAME-ERROR if NAME is not bound."
  (check-type name string)
  (let* ((target-scope
           (if (%globals-declared-p scope name)
               (%find-global-scope scope)
               scope))
         (bindings (scope-bindings target-scope)))
    (unless (nth-value 1 (gethash name bindings))
      (error 'py-name-error :name name))
    (remhash name bindings)
    (values)))

(defun scope-declare-global (scope name)
  "Record that NAME is declared global in SCOPE."
  (check-type name string)
  (setf (gethash name (scope-globals-declared scope)) t))

(defun scope-declare-nonlocal (scope name)
  "Record that NAME is declared nonlocal in SCOPE."
  (check-type name string)
  (setf (gethash name (scope-nonlocals-declared scope)) t))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Scope constructors
;;;; ─────────────────────────────────────────────────────────────────────────

(defun make-global-scope ()
  "Create a fresh global scope.  Its parent is NIL (builtins are
   resolved via LOOKUP-BUILTIN rather than a live scope object)."
  (make-instance 'py-scope :parent nil :scope-type :global))

(defun make-local-scope (parent)
  "Create a new local scope enclosed by PARENT."
  (check-type parent py-scope)
  (let ((scope-kind
          ;; If the immediate parent is already local/enclosing, this new
          ;; scope is also :local; parent becomes :enclosing from its child's
          ;; perspective.  We mark this scope :local; walkers that need to
          ;; distinguish can inspect scope-type of ancestors.
          (if (member (scope-type parent) '(:local :enclosing))
              :local
              :local)))
    (make-instance 'py-scope :parent parent :scope-type scope-kind)))

(defun make-class-scope (parent)
  "Create a class-body scope enclosed by PARENT.
   Class scopes have special name-resolution: they do NOT participate in
   the enclosing (E) leg for inner functions — inner function lookups skip
   the class scope and continue outward.  We record the type as :class so
   that %find-enclosing-scope can skip it."
  (check-type parent py-scope)
  (make-instance 'py-scope :parent parent :scope-type :class))
