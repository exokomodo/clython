;;;; exceptions.lisp — Python 3.12 built-in exception hierarchy as CL conditions
;;;; Reference: https://docs.python.org/3.12/library/exceptions.html

(defpackage :clython.exceptions
  (:use :cl)
  (:export
   ;; Base hierarchy
   #:py-base-exception
   #:py-base-exception-args
   #:py-base-exception-traceback
   #:py-base-exception-cause
   #:py-base-exception-context
   #:py-exception
   #:py-keyboard-interrupt
   #:py-system-exit
   #:py-system-exit-code
   #:py-generator-exit

   ;; Arithmetic
   #:py-arithmetic-error
   #:py-zero-division-error
   #:py-overflow-error
   #:py-floating-point-error

   ;; Assertion
   #:py-assertion-error

   ;; Attribute
   #:py-attribute-error
   #:py-attribute-error-name
   #:py-attribute-error-obj

   ;; EOF
   #:py-eof-error

   ;; Import
   #:py-import-error
   #:py-import-error-name
   #:py-import-error-path
   #:py-module-not-found-error

   ;; Lookup
   #:py-lookup-error
   #:py-index-error
   #:py-key-error

   ;; Name
   #:py-name-error
   #:py-name-error-name
   #:py-unbound-local-error

   ;; OS
   #:py-os-error
   #:py-os-error-errno
   #:py-os-error-strerror
   #:py-os-error-filename
   #:py-file-not-found-error
   #:py-permission-error
   #:py-file-exists-error
   #:py-is-a-directory-error
   #:py-not-a-directory-error

   ;; Runtime
   #:py-runtime-error
   #:py-recursion-error
   #:py-not-implemented-error

   ;; Iteration
   #:py-stop-iteration
   #:py-stop-iteration-value
   #:py-stop-async-iteration

   ;; Syntax
   #:py-syntax-error
   #:py-syntax-error-filename
   #:py-syntax-error-lineno
   #:py-syntax-error-offset
   #:py-syntax-error-text
   #:py-indentation-error
   #:py-tab-error

   ;; Type / Value
   #:py-type-error
   #:py-value-error
   #:py-unicode-error

   ;; Warnings
   #:py-warning
   #:py-deprecation-warning
   #:py-runtime-warning
   #:py-syntax-warning
   #:py-user-warning
   #:py-future-warning
   #:py-pending-deprecation-warning
   #:py-resource-warning

   ;; Exception group (3.11+)
   #:py-exception-group
   #:py-exception-group-message
   #:py-exception-group-exceptions))

(in-package :clython.exceptions)

;;; ---------------------------------------------------------------------------
;;; Helper: format args list the way Python does
;;; ---------------------------------------------------------------------------

(defun format-args (args)
  "Format a list of args like Python's str(exception)."
  (cond
    ((null args) "")
    ((null (cdr args)) (format nil "~A" (car args)))
    (t (format nil "(~{~A~^, ~})" args))))

;;; ---------------------------------------------------------------------------
;;; Base hierarchy
;;; ---------------------------------------------------------------------------

(define-condition py-base-exception (error)
  ((args
    :initarg :args
    :initform nil
    :accessor py-base-exception-args
    :documentation "Tuple of arguments passed to the exception constructor.")
   (traceback
    :initarg :traceback
    :initform nil
    :accessor py-base-exception-traceback
    :documentation "The traceback object associated with this exception (__traceback__).")
   (cause
    :initarg :cause
    :initform nil
    :accessor py-base-exception-cause
    :documentation "Explicitly chained exception (__cause__, from 'raise X from Y').")
   (context
    :initarg :context
    :initform nil
    :accessor py-base-exception-context
    :documentation "Implicitly chained exception (__context__)."))
  (:report (lambda (c stream)
             (format stream "~A: ~A"
                     (type-of c)
                     (format-args (py-base-exception-args c))))))

(define-condition py-exception (py-base-exception)
  ()
  (:report (lambda (c stream)
             (format stream "~A: ~A"
                     (type-of c)
                     (format-args (py-base-exception-args c))))))

(define-condition py-keyboard-interrupt (py-base-exception)
  ()
  (:report (lambda (c stream)
             (format stream "KeyboardInterrupt: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-system-exit (py-base-exception)
  ((code
    :initarg :code
    :initform nil
    :accessor py-system-exit-code
    :documentation "The exit status or message passed to SystemExit."))
  (:report (lambda (c stream)
             (format stream "SystemExit: ~A" (py-system-exit-code c)))))

(define-condition py-generator-exit (py-base-exception)
  ()
  (:report (lambda (c stream)
             (format stream "GeneratorExit: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Arithmetic errors
;;; ---------------------------------------------------------------------------

(define-condition py-arithmetic-error (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "ArithmeticError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-zero-division-error (py-arithmetic-error)
  ()
  (:report (lambda (c stream)
             (format stream "ZeroDivisionError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-overflow-error (py-arithmetic-error)
  ()
  (:report (lambda (c stream)
             (format stream "OverflowError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-floating-point-error (py-arithmetic-error)
  ()
  (:report (lambda (c stream)
             (format stream "FloatingPointError: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Assertion
;;; ---------------------------------------------------------------------------

(define-condition py-assertion-error (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "AssertionError: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Attribute
;;; ---------------------------------------------------------------------------

(define-condition py-attribute-error (py-exception)
  ((name
    :initarg :name
    :initform nil
    :accessor py-attribute-error-name
    :documentation "The attribute name that was not found.")
   (obj
    :initarg :obj
    :initform nil
    :accessor py-attribute-error-obj
    :documentation "The object that raised the AttributeError."))
  (:report (lambda (c stream)
             (if (py-attribute-error-name c)
                 (format stream "AttributeError: ~A" (py-attribute-error-name c))
                 (format stream "AttributeError: ~A"
                         (format-args (py-base-exception-args c)))))))

;;; ---------------------------------------------------------------------------
;;; EOF
;;; ---------------------------------------------------------------------------

(define-condition py-eof-error (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "EOFError: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Import
;;; ---------------------------------------------------------------------------

(define-condition py-import-error (py-exception)
  ((name
    :initarg :name
    :initform nil
    :accessor py-import-error-name
    :documentation "The name of the module that was attempted to be imported.")
   (path
    :initarg :path
    :initform nil
    :accessor py-import-error-path
    :documentation "The path to the file which triggered the exception."))
  (:report (lambda (c stream)
             (format stream "ImportError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-module-not-found-error (py-import-error)
  ()
  (:report (lambda (c stream)
             (format stream "ModuleNotFoundError: No module named ~A"
                     (or (py-import-error-name c)
                         (format-args (py-base-exception-args c)))))))

;;; ---------------------------------------------------------------------------
;;; Lookup
;;; ---------------------------------------------------------------------------

(define-condition py-lookup-error (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "LookupError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-index-error (py-lookup-error)
  ()
  (:report (lambda (c stream)
             (format stream "IndexError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-key-error (py-lookup-error)
  ()
  (:report (lambda (c stream)
             (format stream "KeyError: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Name
;;; ---------------------------------------------------------------------------

(define-condition py-name-error (py-exception)
  ((name
    :initarg :name
    :initform nil
    :accessor py-name-error-name
    :documentation "The name that was not found."))
  (:report (lambda (c stream)
             (format stream "NameError: ~A"
                     (or (py-name-error-name c)
                         (format-args (py-base-exception-args c)))))))

(define-condition py-unbound-local-error (py-name-error)
  ()
  (:report (lambda (c stream)
             (format stream "UnboundLocalError: ~A"
                     (or (py-name-error-name c)
                         (format-args (py-base-exception-args c)))))))

;;; ---------------------------------------------------------------------------
;;; OS errors
;;; ---------------------------------------------------------------------------

(define-condition py-os-error (py-exception)
  ((errno
    :initarg :errno
    :initform nil
    :accessor py-os-error-errno
    :documentation "The numeric errno from the OS.")
   (strerror
    :initarg :strerror
    :initform nil
    :accessor py-os-error-strerror
    :documentation "The human-readable string corresponding to errno.")
   (filename
    :initarg :filename
    :initform nil
    :accessor py-os-error-filename
    :documentation "The file name passed to the function that raised the OSError."))
  (:report (lambda (c stream)
             (if (py-os-error-strerror c)
                 (format stream "OSError: [Errno ~A] ~A~@[: ~A~]"
                         (py-os-error-errno c)
                         (py-os-error-strerror c)
                         (py-os-error-filename c))
                 (format stream "OSError: ~A"
                         (format-args (py-base-exception-args c)))))))

(define-condition py-file-not-found-error (py-os-error)
  ()
  (:report (lambda (c stream)
             (format stream "FileNotFoundError: [Errno ~A] ~A~@[: ~A~]"
                     (or (py-os-error-errno c) 2)
                     (or (py-os-error-strerror c) "No such file or directory")
                     (py-os-error-filename c)))))

(define-condition py-permission-error (py-os-error)
  ()
  (:report (lambda (c stream)
             (format stream "PermissionError: [Errno ~A] ~A~@[: ~A~]"
                     (or (py-os-error-errno c) 13)
                     (or (py-os-error-strerror c) "Permission denied")
                     (py-os-error-filename c)))))

(define-condition py-file-exists-error (py-os-error)
  ()
  (:report (lambda (c stream)
             (format stream "FileExistsError: [Errno ~A] ~A~@[: ~A~]"
                     (or (py-os-error-errno c) 17)
                     (or (py-os-error-strerror c) "File exists")
                     (py-os-error-filename c)))))

(define-condition py-is-a-directory-error (py-os-error)
  ()
  (:report (lambda (c stream)
             (format stream "IsADirectoryError: [Errno ~A] ~A~@[: ~A~]"
                     (or (py-os-error-errno c) 21)
                     (or (py-os-error-strerror c) "Is a directory")
                     (py-os-error-filename c)))))

(define-condition py-not-a-directory-error (py-os-error)
  ()
  (:report (lambda (c stream)
             (format stream "NotADirectoryError: [Errno ~A] ~A~@[: ~A~]"
                     (or (py-os-error-errno c) 20)
                     (or (py-os-error-strerror c) "Not a directory")
                     (py-os-error-filename c)))))

;;; ---------------------------------------------------------------------------
;;; Runtime
;;; ---------------------------------------------------------------------------

(define-condition py-runtime-error (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "RuntimeError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-recursion-error (py-runtime-error)
  ()
  (:report (lambda (c stream)
             (format stream "RecursionError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-not-implemented-error (py-runtime-error)
  ()
  (:report (lambda (c stream)
             (format stream "NotImplementedError: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Iteration
;;; ---------------------------------------------------------------------------

(define-condition py-stop-iteration (py-exception)
  ((value
    :initarg :value
    :initform nil
    :accessor py-stop-iteration-value
    :documentation "The return value of a generator or the value passed to StopIteration."))
  (:report (lambda (c stream)
             (format stream "StopIteration: ~A"
                     (or (py-stop-iteration-value c)
                         (format-args (py-base-exception-args c)))))))

(define-condition py-stop-async-iteration (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "StopAsyncIteration: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Syntax
;;; ---------------------------------------------------------------------------

(define-condition py-syntax-error (py-exception)
  ((filename
    :initarg :filename
    :initform nil
    :accessor py-syntax-error-filename
    :documentation "The name of the file the syntax error occurred in.")
   (lineno
    :initarg :lineno
    :initform nil
    :accessor py-syntax-error-lineno
    :documentation "Which line in the file the error occurred on.")
   (offset
    :initarg :offset
    :initform nil
    :accessor py-syntax-error-offset
    :documentation "The column in the line where the error occurred.")
   (text
    :initarg :text
    :initform nil
    :accessor py-syntax-error-text
    :documentation "The source code text where the error occurred."))
  (:report (lambda (c stream)
             (let ((msg (format-args (py-base-exception-args c))))
               (format stream "SyntaxError: ~A" msg)
               (when (py-syntax-error-filename c)
                 (format stream " (~A" (py-syntax-error-filename c))
                 (when (py-syntax-error-lineno c)
                   (format stream ", line ~A" (py-syntax-error-lineno c)))
                 (format stream ")"))))))

(define-condition py-indentation-error (py-syntax-error)
  ()
  (:report (lambda (c stream)
             (let ((msg (format-args (py-base-exception-args c))))
               (format stream "IndentationError: ~A" msg)
               (when (py-syntax-error-filename c)
                 (format stream " (~A" (py-syntax-error-filename c))
                 (when (py-syntax-error-lineno c)
                   (format stream ", line ~A" (py-syntax-error-lineno c)))
                 (format stream ")"))))))

(define-condition py-tab-error (py-indentation-error)
  ()
  (:report (lambda (c stream)
             (let ((msg (format-args (py-base-exception-args c))))
               (format stream "TabError: ~A" msg)
               (when (py-syntax-error-filename c)
                 (format stream " (~A" (py-syntax-error-filename c))
                 (when (py-syntax-error-lineno c)
                   (format stream ", line ~A" (py-syntax-error-lineno c)))
                 (format stream ")"))))))

;;; ---------------------------------------------------------------------------
;;; Type / Value
;;; ---------------------------------------------------------------------------

(define-condition py-type-error (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "TypeError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-value-error (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "ValueError: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-unicode-error (py-value-error)
  ()
  (:report (lambda (c stream)
             (format stream "UnicodeError: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Warnings
;;; ---------------------------------------------------------------------------

(define-condition py-warning (py-exception)
  ()
  (:report (lambda (c stream)
             (format stream "Warning: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-deprecation-warning (py-warning)
  ()
  (:report (lambda (c stream)
             (format stream "DeprecationWarning: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-runtime-warning (py-warning)
  ()
  (:report (lambda (c stream)
             (format stream "RuntimeWarning: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-syntax-warning (py-warning)
  ()
  (:report (lambda (c stream)
             (format stream "SyntaxWarning: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-user-warning (py-warning)
  ()
  (:report (lambda (c stream)
             (format stream "UserWarning: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-future-warning (py-warning)
  ()
  (:report (lambda (c stream)
             (format stream "FutureWarning: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-pending-deprecation-warning (py-warning)
  ()
  (:report (lambda (c stream)
             (format stream "PendingDeprecationWarning: ~A"
                     (format-args (py-base-exception-args c))))))

(define-condition py-resource-warning (py-warning)
  ()
  (:report (lambda (c stream)
             (format stream "ResourceWarning: ~A"
                     (format-args (py-base-exception-args c))))))

;;; ---------------------------------------------------------------------------
;;; Exception group (Python 3.11+)
;;; ---------------------------------------------------------------------------

(define-condition py-exception-group (py-exception)
  ((message
    :initarg :message
    :initform ""
    :accessor py-exception-group-message
    :documentation "The message describing the exception group.")
   (exceptions
    :initarg :exceptions
    :initform nil
    :accessor py-exception-group-exceptions
    :documentation "The list of contained exceptions."))
  (:report (lambda (c stream)
             (format stream "ExceptionGroup: ~A (~A sub-exception~:P)"
                     (py-exception-group-message c)
                     (length (py-exception-group-exceptions c))))))
