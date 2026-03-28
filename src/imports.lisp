;;;; imports.lisp — Python import system for Clython
;;;;
;;;; Implements module finding, loading, and caching. Supports:
;;;; - Built-in module stubs (sys, _io, builtins, _thread, _signal)
;;;; - Loading pure-Python stdlib modules from CPython's stdlib
;;;; - Module caching to avoid re-evaluation
;;;; - Circular import guards

(defpackage :clython.imports
  (:use :cl)
  (:export
   #:import-module
   #:*module-registry*
   #:*sys-path*
   #:*builtin-modules*
   #:*eval-source-fn*
   #:initialize-import-system))

(in-package :clython.imports)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Module registry (cache)
;;;; ─────────────────────────────────────────────────────────────────────────

(defvar *module-registry* (make-hash-table :test #'equal)
  "Maps fully-qualified module name → py-module. Once imported, modules are cached.")

(defvar *eval-source-fn* nil
  "Callback: (lambda (source env) ...) — evaluates Python source in an environment.
   Set by eval.lisp at load time to break the circular dependency.")

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; sys.path equivalent
;;;; ─────────────────────────────────────────────────────────────────────────

(defvar *sys-path* (list "." "/usr/lib/python3.11" "/usr/lib/python3.11/lib-dynload")
  "List of directory paths to search for modules.")

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Built-in module stubs
;;;; ─────────────────────────────────────────────────────────────────────────

(defvar *builtin-modules* (make-hash-table :test #'equal)
  "Maps module name → thunk that returns a py-module for C extension stubs.")

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
    (setf (gethash "modules" (clython.runtime:py-module-dict mod))
          ;; Wrap *module-registry* — we'll expose it as a dict-like object later
          ;; For now, a simple py-dict
          (let ((d (clython.runtime:make-py-dict)))
            d))
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
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "sys"))
    mod))

(defun make-stub-module (name)
  "Create a minimal stub module with just __name__."
  (let ((mod (clython.runtime:make-py-module name)))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str name))
    mod))

(defun make-builtins-module ()
  "Create the builtins module referencing our builtins."
  (let ((mod (clython.runtime:make-py-module "builtins")))
    ;; Copy all builtins into the module dict
    (maphash (lambda (name fn)
               (setf (gethash name (clython.runtime:py-module-dict mod)) fn))
             clython.builtins:*builtins*)
    (setf (gethash "True" (clython.runtime:py-module-dict mod)) clython.runtime:+py-true+)
    (setf (gethash "False" (clython.runtime:py-module-dict mod)) clython.runtime:+py-false+)
    (setf (gethash "None" (clython.runtime:py-module-dict mod)) clython.runtime:+py-none+)
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "builtins"))
    mod))

(defun %math-wrap-2 (name cl-fn)
  "Wrap a two-arg CL math function as a Python callable."
  (clython.runtime:make-py-function
   :name name
   :cl-fn (lambda (x y)
            (clython.runtime:make-py-float
             (funcall cl-fn
                      (coerce (clython.runtime:py->cl x) 'double-float)
                      (coerce (clython.runtime:py->cl y) 'double-float))))))

(defun make-math-module ()
  "Create the math built-in module."
  (let ((mod (clython.runtime:make-py-module "math"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))
    ;; Constants
    (setf (gethash "pi" d) (clython.runtime:make-py-float (coerce pi 'double-float)))
    (setf (gethash "e" d) (clython.runtime:make-py-float (exp 1.0d0)))
    (setf (gethash "tau" d) (clython.runtime:make-py-float (* 2.0d0 (coerce pi 'double-float))))
    (setf (gethash "inf" d) (clython.runtime:make-py-float
                              #+sbcl sb-ext:double-float-positive-infinity
                              #-sbcl most-positive-double-float))
    (setf (gethash "nan" d) (clython.runtime:make-py-float
                              #+sbcl (sb-int:with-float-traps-masked (:invalid)
                                       (- sb-ext:double-float-positive-infinity
                                          sb-ext:double-float-positive-infinity))
                              #-sbcl 0.0d0))
    ;; Single-arg functions
    (dolist (pair '((sqrt . cl:sqrt) (sin . cl:sin) (cos . cl:cos) (tan . cl:tan)
                    (asin . cl:asin) (acos . cl:acos) (atan . cl:atan)
                    (exp . cl:exp) (log . cl:log)
                    (floor . cl:floor) (ceil . cl:ceiling)))
      (let ((name (symbol-name (car pair)))
            (fn (cdr pair)))
        (setf (gethash (string-downcase name) d)
              (clython.runtime:make-py-function
               :name (string-downcase name)
               :cl-fn (let ((f fn))  ; capture
                         (lambda (x)
                           (let ((result (funcall f (coerce (clython.runtime:py->cl x) 'double-float))))
                             (if (integerp result)
                                 (clython.runtime:make-py-int result)
                                 (clython.runtime:make-py-float (coerce result 'double-float))))))))))
    ;; fabs
    (setf (gethash "fabs" d)
          (clython.runtime:make-py-function
           :name "fabs"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-float
                     (abs (coerce (clython.runtime:py->cl x) 'double-float))))))
    ;; pow
    (setf (gethash "pow" d) (%math-wrap-2 "pow" #'expt))
    ;; isnan, isinf
    (setf (gethash "isnan" d)
          (clython.runtime:make-py-function
           :name "isnan"
           :cl-fn (lambda (x)
                    (let ((v (coerce (clython.runtime:py->cl x) 'double-float)))
                      (clython.runtime:cl->py #+sbcl (sb-ext:float-nan-p v) #-sbcl nil)))))
    (setf (gethash "isinf" d)
          (clython.runtime:make-py-function
           :name "isinf"
           :cl-fn (lambda (x)
                    (let ((v (coerce (clython.runtime:py->cl x) 'double-float)))
                      (clython.runtime:cl->py #+sbcl (sb-ext:float-infinity-p v) #-sbcl nil)))))
    ;; Module metadata
    (setf (gethash "__name__" d) (clython.runtime:make-py-str "math"))
    mod))

;;; asyncio module -----------------------------------------------------------
(defun make-asyncio-module ()
  "Create a minimal asyncio module with run() for driving coroutines."
  (let ((mod (clython.runtime:make-py-module "asyncio"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))
    ;; asyncio.run(coro) — runs a coroutine to completion
    (setf (gethash "run" d)
          (clython.runtime:make-py-function
           :name "run"
           :cl-fn (lambda (coro)
                    (if (typep coro 'clython.runtime:py-coroutine)
                        (clython.runtime:py-coroutine-run coro)
                        ;; If not a coroutine, just return it (matches CPython behavior for non-coro)
                        (clython.runtime:py-raise "TypeError"
                                                  "asyncio.run() requires a coroutine object")))))
    ;; asyncio.sleep(seconds) — in synchronous mode, returns a coroutine that resolves to None
    (setf (gethash "sleep" d)
          (clython.runtime:make-py-function
           :name "sleep"
           :cl-fn (lambda (seconds)
                    (declare (ignore seconds))
                    ;; Return a coroutine that resolves to None (no actual sleeping in sync mode)
                    (clython.runtime:make-py-coroutine
                     (lambda () clython.runtime:+py-none+)))
           :async-p t))
    ;; asyncio.gather(*coros) — run all coroutines, return list of results
    (setf (gethash "gather" d)
          (clython.runtime:make-py-function
           :name "gather"
           :cl-fn (lambda (&rest coros)
                    (clython.runtime:make-py-coroutine
                     (lambda ()
                       (clython.runtime:make-py-list
                        (mapcar (lambda (c)
                                  (if (typep c 'clython.runtime:py-coroutine)
                                      (clython.runtime:py-coroutine-run c)
                                      c))
                                coros)))))
           :async-p t))
    ;; Module metadata
    (setf (gethash "__name__" d) (clython.runtime:make-py-str "asyncio"))
    mod))

(defun register-builtin-modules ()
  "Register all built-in module stubs."
  (setf (gethash "sys" *builtin-modules*) #'make-sys-module)
  (setf (gethash "_io" *builtin-modules*) (lambda () (make-stub-module "_io")))
  (setf (gethash "builtins" *builtin-modules*) #'make-builtins-module)
  (setf (gethash "_thread" *builtin-modules*) (lambda () (make-stub-module "_thread")))
  (setf (gethash "_signal" *builtin-modules*) (lambda () (make-stub-module "_signal")))
  (setf (gethash "posixpath" *builtin-modules*) (lambda () (make-stub-module "posixpath")))
  (setf (gethash "_collections_abc" *builtin-modules*)
        (lambda () (make-stub-module "_collections_abc")))
  (setf (gethash "_sitebuiltins" *builtin-modules*)
        (lambda () (make-stub-module "_sitebuiltins")))
  (setf (gethash "_stat" *builtin-modules*) (lambda () (make-stub-module "_stat")))
  (setf (gethash "_weakref" *builtin-modules*) (lambda () (make-stub-module "_weakref")))
  (setf (gethash "_abc" *builtin-modules*) (lambda () (make-stub-module "_abc")))
  (setf (gethash "_operator" *builtin-modules*) (lambda () (make-stub-module "_operator")))
  (setf (gethash "_functools" *builtin-modules*) (lambda () (make-stub-module "_functools")))
  (setf (gethash "nt" *builtin-modules*) (lambda () (make-stub-module "nt")))
  (setf (gethash "marshal" *builtin-modules*) (lambda () (make-stub-module "marshal")))
  (setf (gethash "_imp" *builtin-modules*) (lambda () (make-stub-module "_imp")))
  (setf (gethash "winreg" *builtin-modules*) (lambda () (make-stub-module "winreg")))
  (setf (gethash "math" *builtin-modules*) #'make-math-module)
  (setf (gethash "asyncio" *builtin-modules*) #'make-asyncio-module))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Module finder
;;;; ─────────────────────────────────────────────────────────────────────────

(defun dotted-to-path (name)
  "Convert a dotted module name to a relative file path.
   e.g. 'os.path' → 'os/path'"
  (substitute #\/ #\. name))

(defun find-module-file (name)
  "Resolve a module name to a .py file path.
   Returns (values path is-package) or NIL if not found.
   Handles dotted names: 'os.path' → search for os/path.py or os/path/__init__.py"
  (let ((rel (dotted-to-path name)))
    (dolist (dir *sys-path*)
      ;; Try <dir>/<rel>.py — single module
      (let ((py-path (format nil "~A/~A.py" dir rel)))
        (when (probe-file py-path)
          (return-from find-module-file (values py-path nil))))
      ;; Try <dir>/<rel>/__init__.py — package
      (let ((init-path (format nil "~A/~A/__init__.py" dir rel)))
        (when (probe-file init-path)
          (return-from find-module-file (values init-path t)))))
    nil))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Module loader
;;;; ─────────────────────────────────────────────────────────────────────────

(defun import-module (name &optional env)
  "Import a module by name. Returns a py-module object.
   Checks cache, then built-ins, then searches *sys-path* for .py files."
  (declare (ignore env))
  ;; 1. Check cache
  (multiple-value-bind (cached found) (gethash name *module-registry*)
    (when found (return-from import-module cached)))

  ;; For dotted names, ensure parent modules are imported first
  (let ((dot-pos (position #\. name)))
    (when dot-pos
      (let ((parent-name (subseq name 0 dot-pos)))
        (import-module parent-name))))

  ;; 2. Check built-in module stubs
  (multiple-value-bind (maker found) (gethash name *builtin-modules*)
    (when found
      (let ((mod (funcall maker)))
        (setf (gethash name *module-registry*) mod)
        (return-from import-module mod))))

  ;; 3. Find .py file
  (multiple-value-bind (path is-package) (find-module-file name)
    (unless path
      (clython.runtime:py-raise "ModuleNotFoundError" "No module named '~A'" name))

    ;; 4. Create module with its own environment
    (let ((mod (clython.runtime:make-py-module name)))
      ;; Set module attributes
      (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
            (clython.runtime:make-py-str name))
      (setf (gethash "__file__" (clython.runtime:py-module-dict mod))
            (clython.runtime:make-py-str (namestring path)))
      (setf (gethash "__package__" (clython.runtime:py-module-dict mod))
            (if is-package
                (clython.runtime:make-py-str name)
                (let ((dot-pos (position #\. name :from-end t)))
                  (if dot-pos
                      (clython.runtime:make-py-str (subseq name 0 dot-pos))
                      (clython.runtime:make-py-str "")))))

      ;; 5. Register BEFORE evaluating (circular import guard)
      (setf (gethash name *module-registry*) mod)

      ;; 6. Read and evaluate the .py file in the module's own environment
      (handler-case
          (let* ((source (with-open-file (f path :direction :input
                                                 :external-format :utf-8)
                           (let ((s (make-string (file-length f))))
                             (read-sequence s f)
                             s)))
                 ;; Create a fresh global env for the module
                 (mod-env (clython.scope:make-global-env)))
            ;; Pre-set __name__, __file__, __package__ in the env
            (setf (gethash "__name__" (clython.scope:env-bindings mod-env))
                  (gethash "__name__" (clython.runtime:py-module-dict mod)))
            (setf (gethash "__file__" (clython.scope:env-bindings mod-env))
                  (gethash "__file__" (clython.runtime:py-module-dict mod)))
            (setf (gethash "__package__" (clython.scope:env-bindings mod-env))
                  (gethash "__package__" (clython.runtime:py-module-dict mod)))

            ;; Parse and evaluate using the callback
            (funcall *eval-source-fn* source mod-env)

            ;; 7. Copy bindings from module env into module dict
            (maphash (lambda (k v)
                       (setf (gethash k (clython.runtime:py-module-dict mod)) v))
                     (clython.scope:env-bindings mod-env)))
        (error (e)
          ;; If loading fails, remove from registry and re-signal
          (remhash name *module-registry*)
          (clython.runtime:py-raise "ImportError" "Error loading module '~A': ~A" name e)))

      ;; 8. For dotted names, set as attribute on parent module
      (let ((dot-pos (position #\. name :from-end t)))
        (when dot-pos
          (let* ((parent-name (subseq name 0 dot-pos))
                 (attr-name (subseq name (1+ dot-pos)))
                 (parent (gethash parent-name *module-registry*)))
            (when parent
              (setf (gethash attr-name (clython.runtime:py-module-dict parent)) mod)))))

      mod)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Initialization
;;;; ─────────────────────────────────────────────────────────────────────────

(defun initialize-import-system ()
  "Initialize the import system. Call once at startup."
  (clrhash *module-registry*)
  (register-builtin-modules))

;; Auto-initialize when loaded
(initialize-import-system)
