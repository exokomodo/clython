;;;; imports.lisp — module finder, loader, and built-in module registry
;;;;
;;;; Module implementations live in src/modules/. To add a module:
;;;;   1. Create src/modules/<name>.lisp with (defun make-<name>-module () ...)
;;;;   2. Add (:file "<name>") to the :modules section of clython.asd
;;;;   3. Register it in register-builtin-modules below.

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

(defun make-stub-module (name)
  "Create a minimal stub module with just __name__."
  (let ((mod (clython.runtime:make-py-module name)))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str name))
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

(defun %py-to-json (obj)
  "Convert a Python object to a JSON string."
  (typecase obj
    (clython.runtime:py-dict
     (let ((pairs '()))
       (maphash (lambda (k v)
                  ;; k is an unwrapped CL key (string, int, etc.)
                  (let ((json-key (cond ((stringp k) (format nil "\"~A\"" k))
                                        ((integerp k) (format nil "~D" k))
                                        (t (format nil "\"~A\"" k)))))
                    (push (format nil "~A: ~A" json-key (%py-to-json v)) pairs)))
                (clython.runtime:py-dict-value obj))
       (format nil "{~{~A~^, ~}}" (nreverse pairs))))
    (clython.runtime:py-list
     (format nil "[~{~A~^, ~}]"
             (mapcar #'%py-to-json (coerce (clython.runtime:py-list-value obj) 'list))))
    (clython.runtime:py-str
     (format nil "\"~A\"" (clython.runtime:py-str-value obj)))
    (clython.runtime:py-int
     (format nil "~D" (clython.runtime:py-int-value obj)))
    (clython.runtime:py-float
     (let ((v (clython.runtime:py-float-value obj)))
       (format nil "~F" v)))
    (clython.runtime:py-bool
     (if (clython.runtime:py-bool-val obj) "true" "false"))
    (t (if (eq obj clython.runtime:+py-none+) "null"
           (format nil "\"~A\"" (clython.runtime:py-repr obj))))))

(defun list->adjustable-vector (items)
  "Convert a CL list to an adjustable vector with fill pointer."
  (let* ((n (length items))
         (v (make-array n :adjustable t :fill-pointer n)))
    (loop for item in items
          for i from 0
          do (setf (aref v i) item))
    v))

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
  (setf (gethash "asyncio" *builtin-modules*) #'make-asyncio-module)
  (setf (gethash "os" *builtin-modules*) #'make-os-module)
  (setf (gethash "os.path" *builtin-modules*) #'make-os-path-module)
  (setf (gethash "json" *builtin-modules*) #'make-json-module)
  (setf (gethash "collections" *builtin-modules*) #'make-collections-module)
  (setf (gethash "decimal" *builtin-modules*) #'make-decimal-module)
  (setf (gethash "fractions" *builtin-modules*) #'make-fractions-module)
  (setf (gethash "keyword" *builtin-modules*) #'make-keyword-module)
  (setf (gethash "itertools" *builtin-modules*) #'make-itertools-module)
  (setf (gethash "string" *builtin-modules*) #'make-string-module)
  (setf (gethash "functools" *builtin-modules*) #'make-functools-module)
  (setf (gethash "io" *builtin-modules*) #'make-io-module)
  (setf (gethash "random" *builtin-modules*) #'make-random-module)
  ;; C extension / stdlib stubs needed for CPython stdlib .py files to parse
  (setf (gethash "re" *builtin-modules*) #'make-re-module)
  (dolist (name '("_string" "_collections" "_decimal" "_pydecimal"
                  "_weakrefset" "_py_abc" "abc" "types" "warnings"
                  "stat" "posix" "errno" "copy" "heapq" "reprlib"
                  "numbers" "codecs" "copyreg" "operator" "threading" "enum"
                  "_sre" "sre_compile" "sre_parse" "sre_constants" "random"
                  "importlib" "dataclasses" "subprocess" "inspect"
                  "contextlib" "weakref" "ntpath" "genericpath"
                  "_imp" "signal" "abc" "token" "tokenize"))
    (unless (gethash name *builtin-modules*)
      (let ((n name))  ; capture for closure
        (setf (gethash n *builtin-modules*)
              (lambda () (make-stub-module n)))))))

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

;; Register __import__ builtin (must happen after imports package is loaded)
(setf (gethash "__import__" clython.builtins:*builtins*)
      (clython.runtime:make-py-function
       :name "__import__"
       :cl-fn (lambda (name-obj)
                (let ((name (clython.runtime:py-str-value name-obj)))
                  (import-module name)))))
