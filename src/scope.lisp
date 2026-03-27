;;;; scope.lisp — LEGB scoping for Clython
;;;;
;;;; Implements the Python LEGB (Local → Enclosing → Global → Builtin) scope
;;;; resolution model using chained environment objects.

(defpackage :clython.scope
  (:use :cl)
  (:export
   #:environment
   #:env-bindings
   #:env-parent
   #:env-globals
   #:env-nonlocals
   #:make-global-env
   #:env-get
   #:env-set
   #:env-set-global
   #:env-del
   #:env-extend
   #:env-declare-global
   #:env-declare-nonlocal))

(in-package :clython.scope)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Environment class
;;;; ─────────────────────────────────────────────────────────────────────────

(defclass environment ()
  ((bindings  :initarg :bindings
              :accessor env-bindings
              :initform (make-hash-table :test #'equal)
              :documentation "Hash-table mapping name strings to py-object values.")
   (parent    :initarg :parent
              :accessor env-parent
              :initform nil
              :documentation "Enclosing environment, or NIL for the global scope.")
   (globals   :initarg :globals
              :accessor env-globals
              :initform (make-hash-table :test #'equal)
              :documentation "Set of names declared `global` in this scope.")
   (nonlocals :initarg :nonlocals
              :accessor env-nonlocals
              :initform (make-hash-table :test #'equal)
              :documentation "Set of names declared `nonlocal` in this scope."))
  (:documentation "A lexical scope with bindings, parent link, and global/nonlocal declarations."))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Constructors
;;;; ─────────────────────────────────────────────────────────────────────────

(defun make-global-env ()
  "Create a fresh global environment pre-populated with Python builtins."
  (let ((env (make-instance 'environment)))
    ;; Copy all builtins into the global scope
    (maphash (lambda (name fn)
               (setf (gethash name (env-bindings env)) fn))
             clython.builtins:*builtins*)
    ;; Also bind True, False, None as names
    (setf (gethash "True"  (env-bindings env)) clython.runtime:+py-true+)
    (setf (gethash "False" (env-bindings env)) clython.runtime:+py-false+)
    (setf (gethash "None"  (env-bindings env)) clython.runtime:+py-none+)
    env))

(defun env-extend (parent)
  "Create a child scope whose parent is PARENT."
  (make-instance 'environment :parent parent))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Global / nonlocal declarations
;;;; ─────────────────────────────────────────────────────────────────────────

(defun env-declare-global (name env)
  "Mark NAME as a global variable in ENV."
  (setf (gethash name (env-globals env)) t))

(defun env-declare-nonlocal (name env)
  "Mark NAME as a nonlocal variable in ENV."
  (setf (gethash name (env-nonlocals env)) t))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Root-finding helper
;;;; ─────────────────────────────────────────────────────────────────────────

(defun %find-root (env)
  "Walk up the parent chain to find the global (root) environment."
  (loop while (env-parent env) do (setf env (env-parent env)))
  env)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Lookup (LEGB)
;;;; ─────────────────────────────────────────────────────────────────────────

(defun env-get (name env)
  "Look up NAME following LEGB rules. Signals an error on NameError."
  ;; If this scope declares the name as global, go straight to root
  (when (gethash name (env-globals env))
    (let ((root (%find-root env)))
      (multiple-value-bind (val found) (gethash name (env-bindings root))
        (if found
            (return-from env-get val)
            (error "NameError: name '~A' is not defined" name)))))
  ;; If this scope declares the name as nonlocal, skip local and search enclosing
  (when (gethash name (env-nonlocals env))
    (let ((e (env-parent env)))
      (loop while e do
        (multiple-value-bind (val found) (gethash name (env-bindings e))
          (when found (return-from env-get val)))
        (setf e (env-parent e))))
    (error "NameError: name '~A' is not defined" name))
  ;; Normal LEGB: search local → parent chain
  (let ((e env))
    (loop while e do
      (multiple-value-bind (val found) (gethash name (env-bindings e))
        (when found (return-from env-get val)))
      (setf e (env-parent e))))
  ;; Builtin fallback — check the builtins registry directly
  (multiple-value-bind (builtin found) (gethash name clython.builtins:*builtins*)
    (when found (return-from env-get builtin)))
  (error "NameError: name '~A' is not defined" name))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Assignment
;;;; ─────────────────────────────────────────────────────────────────────────

(defun env-set (name value env)
  "Set NAME to VALUE in the appropriate scope, respecting global/nonlocal."
  ;; global declaration → set in root
  (when (gethash name (env-globals env))
    (let ((root (%find-root env)))
      (setf (gethash name (env-bindings root)) value)
      (return-from env-set value)))
  ;; nonlocal declaration → set in nearest enclosing scope that has it
  (when (gethash name (env-nonlocals env))
    (let ((e (env-parent env)))
      (loop while e do
        (multiple-value-bind (val found) (gethash name (env-bindings e))
          (declare (ignore val))
          (when found
            (setf (gethash name (env-bindings e)) value)
            (return-from env-set value)))
        (setf e (env-parent e))))
    ;; If not found in any enclosing scope, set in immediate parent
    (when (env-parent env)
      (setf (gethash name (env-bindings (env-parent env))) value)
      (return-from env-set value)))
  ;; Normal: set in current (local) scope
  (setf (gethash name (env-bindings env)) value))

(defun env-set-global (name value env)
  "Set NAME to VALUE in the global (root) scope."
  (let ((root (%find-root env)))
    (setf (gethash name (env-bindings root)) value)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Deletion
;;;; ─────────────────────────────────────────────────────────────────────────

(defun env-del (name env)
  "Delete NAME from the current scope."
  (unless (remhash name (env-bindings env))
    (error "NameError: name '~A' is not defined" name)))
