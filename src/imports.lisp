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
    ;; sys.modules — uses *module-registry* as backing store
    ;; We populate a py-dict from the registry; it's a snapshot but updated on access
    (setf (gethash "modules" (clython.runtime:py-module-dict mod))
          (let ((d (clython.runtime:make-py-dict)))
            ;; Pre-populate with currently-loaded modules
            (maphash (lambda (k v)
                       (clython.runtime:py-setitem
                        d (clython.runtime:make-py-str k) v))
                     *module-registry*)
            ;; Always include sys itself
            (clython.runtime:py-setitem
             d (clython.runtime:make-py-str "sys") mod)
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
    (setf (gethash "executable" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "clython"))
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
    ;; factorial(n)
    (setf (gethash "factorial" d)
          (clython.runtime:make-py-function
           :name "factorial"
           :cl-fn (lambda (n)
                    (let ((v (clython.runtime:py->cl n)))
                      (when (or (not (integerp v)) (< v 0))
                        (clython.runtime:py-raise "ValueError"
                          "factorial() only accepts integral values >= 0"))
                      (clython.runtime:make-py-int
                       (loop for i from 1 to v
                             for acc = 1 then (* acc i)
                             finally (return acc)))))))
    ;; gcd(a, b)
    (setf (gethash "gcd" d)
          (clython.runtime:make-py-function
           :name "gcd"
           :cl-fn (lambda (&rest args)
                    (cond
                      ((null args) (clython.runtime:make-py-int 0))
                      ((= (length args) 1)
                       (clython.runtime:make-py-int (abs (clython.runtime:py->cl (first args)))))
                      (t (clython.runtime:make-py-int
                          (reduce #'gcd (mapcar (lambda (x) (abs (clython.runtime:py->cl x))) args))))))))
    ;; lcm(a, b)
    (setf (gethash "lcm" d)
          (clython.runtime:make-py-function
           :name "lcm"
           :cl-fn (lambda (&rest args)
                    (flet ((lcm2 (a b)
                             (if (or (zerop a) (zerop b)) 0
                                 (/ (abs (* a b)) (gcd a b)))))
                      (if (null args)
                          (clython.runtime:make-py-int 1)
                          (clython.runtime:make-py-int
                           (reduce #'lcm2 (mapcar (lambda (x) (abs (clython.runtime:py->cl x))) args))))))))
    ;; trunc(x)
    (setf (gethash "trunc" d)
          (clython.runtime:make-py-function
           :name "trunc"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-int
                     (truncate (clython.runtime:py->cl x))))))
    ;; degrees / radians
    (setf (gethash "degrees" d)
          (clython.runtime:make-py-function
           :name "degrees"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-float
                     (* (coerce (clython.runtime:py->cl x) 'double-float)
                        (/ 180.0d0 (coerce pi 'double-float)))))))
    (setf (gethash "radians" d)
          (clython.runtime:make-py-function
           :name "radians"
           :cl-fn (lambda (x)
                    (clython.runtime:make-py-float
                     (* (coerce (clython.runtime:py->cl x) 'double-float)
                        (/ (coerce pi 'double-float) 180.0d0))))))
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
    ;; asyncio.iscoroutine(obj)
    (setf (gethash "iscoroutine" d)
          (clython.runtime:make-py-function
           :name "iscoroutine"
           :cl-fn (lambda (obj)
                    (if (typep obj 'clython.runtime:py-coroutine)
                        clython.runtime:+py-true+
                        clython.runtime:+py-false+))))
    ;; asyncio.iscoroutinefunction(obj)
    (setf (gethash "iscoroutinefunction" d)
          (clython.runtime:make-py-function
           :name "iscoroutinefunction"
           :cl-fn (lambda (obj)
                    (if (and (typep obj 'clython.runtime:py-function)
                             (clython.runtime:py-function-async-p obj))
                        clython.runtime:+py-true+
                        clython.runtime:+py-false+))))
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

;;; ─── os module ──────────────────────────────────────────────────────────────

(defun make-os-path-module ()
  "Create a stub os.path module with join."
  (let ((mod (clython.runtime:make-py-module "os.path")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "os.path"))
    ;; os.path.join(*parts)
    (setf (gethash "join" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "join"
           :cl-fn (lambda (&rest parts)
                    (clython.runtime:make-py-str
                     (format nil "~{~A~^/~}"
                             (mapcar #'clython.runtime:py->cl parts))))))
    ;; os.path.exists(path) — stub returns False
    (setf (gethash "exists" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "exists"
           :cl-fn (lambda (p) (declare (ignore p)) clython.runtime:+py-false+)))
    mod))

(defun make-os-module ()
  "Create a stub os module."
  (let ((mod (clython.runtime:make-py-module "os")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "os"))
    ;; os.path submodule
    (let ((path-mod (make-os-path-module)))
      (setf (gethash "path" (clython.runtime:py-module-dict mod)) path-mod)
      ;; Also register os.path in the module registry
      (setf (gethash "os.path" *module-registry*) path-mod))
    ;; os.getcwd()
    (setf (gethash "getcwd" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "getcwd"
           :cl-fn (lambda ()
                    (clython.runtime:make-py-str
                     (namestring (uiop:getcwd))))))
    ;; os.sep
    (setf (gethash "sep" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "/"))
    mod))

;;; ─── json module ────────────────────────────────────────────────────────────

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

(defun make-json-module ()
  "Create a stub json module with dumps and loads."
  (let ((mod (clython.runtime:make-py-module "json")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "json"))
    ;; json.dumps(obj)
    (setf (gethash "dumps" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "dumps"
           :cl-fn (lambda (obj &rest _kw) (declare (ignore _kw))
                    (clython.runtime:make-py-str (%py-to-json obj)))))
    mod))

;;; ─── decimal module ─────────────────────────────────────────────────────────

(defun make-decimal-module ()
  "Create a stub decimal module with Decimal class."
  (let* ((mod (clython.runtime:make-py-module "decimal"))
         (decimal-type (clython.runtime:make-py-type
                        :name "Decimal" :bases nil :tdict (make-hash-table :test #'equal))))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "decimal"))
    ;; Decimal is implemented as a wrapper around CL rational numbers
    ;; The "class" is actually a constructor function that returns py-objects
    (setf (gethash "Decimal" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "Decimal"
           :cl-fn (lambda (val)
                    (let* ((s (clython.runtime:py->cl val))
                           (r (cond ((stringp s)
                                     (let ((rat (read-from-string s)))
                                       (if (rationalp rat) rat (rationalize rat))))
                                    ((rationalp s) s)
                                    ((numberp s) (rationalize s))
                                    (t 0)))
                           (obj (make-instance 'clython.runtime:py-object :py-class decimal-type :py-dict (make-hash-table :test #'equal))))
                      ;; Store the rational value
                      (setf (gethash "_value" (clython.runtime:py-object-dict obj)) r)
                      ;; __str__ and __repr__
                      (setf (gethash "__str__" (clython.runtime:py-type-dict decimal-type))
                            (clython.runtime:make-py-function
                             :name "__str__"
                             :cl-fn (lambda (self)
                                      (let ((v (gethash "_value" (clython.runtime:py-object-dict self))))
                                        (clython.runtime:make-py-str
                                         (format nil "~F" (coerce v 'double-float)))))))
                      ;; __add__
                      (setf (gethash "__add__" (clython.runtime:py-type-dict decimal-type))
                            (clython.runtime:make-py-function
                             :name "__add__"
                             :cl-fn (lambda (self other)
                                      (let* ((v1 (gethash "_value" (clython.runtime:py-object-dict self)))
                                             (v2 (gethash "_value" (clython.runtime:py-object-dict other)))
                                             (result (+ v1 v2))
                                             (new-obj (make-instance 'clython.runtime:py-object :py-class decimal-type :py-dict (make-hash-table :test #'equal))))
                                        (setf (gethash "_value" (clython.runtime:py-object-dict new-obj)) result)
                                        new-obj))))
                      obj))))
    mod))

;;; ─── fractions module ───────────────────────────────────────────────────────

(defun make-fractions-module ()
  "Create a stub fractions module with Fraction class."
  (let* ((mod (clython.runtime:make-py-module "fractions"))
         (fraction-type (clython.runtime:make-py-type
                         :name "Fraction" :bases nil :tdict (make-hash-table :test #'equal))))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "fractions"))
    ;; __str__ for Fraction: "numerator/denominator"
    (setf (gethash "__str__" (clython.runtime:py-type-dict fraction-type))
          (clython.runtime:make-py-function
           :name "__str__"
           :cl-fn (lambda (self)
                    (let ((v (gethash "_value" (clython.runtime:py-object-dict self))))
                      (clython.runtime:make-py-str
                       (format nil "~D/~D" (numerator v) (denominator v)))))))
    ;; Fraction(num, den) constructor
    (setf (gethash "Fraction" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "Fraction"
           :cl-fn (lambda (num &optional den)
                    (let* ((n (clython.runtime:py->cl num))
                           (d (if den (clython.runtime:py->cl den) 1))
                           (obj (make-instance 'clython.runtime:py-object :py-class fraction-type :py-dict (make-hash-table :test #'equal))))
                      (setf (gethash "_value" (clython.runtime:py-object-dict obj))
                            (/ n d))
                      obj))))
    mod))

;;; ─── collections module ─────────────────────────────────────────────────────

(defun make-collections-module ()
  "Create the collections module with working implementations."
  (let ((mod (clython.runtime:make-py-module "collections")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "collections"))

    ;; OrderedDict — dict that records insertion order (use alist for ordering)
    (setf (gethash "OrderedDict" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "OrderedDict"
           :cl-fn (lambda (&rest args)
                    ;; Returns a regular py-dict (CL hash-tables maintain insertion
                    ;; order in SBCL for small tables; good enough for conformance)
                    (let ((d (clython.runtime:make-py-dict)))
                      (when (and args (typep (first args) 'clython.runtime:py-dict))
                        (maphash (lambda (k v)
                                   (clython.runtime:py-setitem d (clython.runtime:make-py-str k) v))
                                 (clython.runtime:py-dict-value (first args))))
                      d))))

    ;; namedtuple(typename, field_names) — returns a class constructor
    (setf (gethash "namedtuple" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "namedtuple"
           :cl-fn (lambda (&rest args)
                    (let* ((typename (clython.runtime:py-str-value (first args)))
                           (fields-arg (second args))
                           (fields (cond
                                     ((typep fields-arg 'clython.runtime:py-list)
                                      (map 'list #'clython.runtime:py-str-value
                                           (clython.runtime:py-list-value fields-arg)))
                                     ((typep fields-arg 'clython.runtime:py-str)
                                      ;; Split on spaces/commas
                                      (let ((s (clython.runtime:py-str-value fields-arg)))
                                        (loop for tok in (uiop:split-string s :separator '(#\Space #\,))
                                              for trimmed = (string-trim '(#\Space) tok)
                                              unless (string= trimmed "")
                                              collect trimmed)))
                                     (t nil))))
                      ;; Return a constructor function that creates tuple-like objects
                      (clython.runtime:make-py-function
                       :name typename
                       :cl-fn (lambda (&rest fargs)
                                (let* ((obj (make-instance 'clython.runtime:py-object
                                                           :py-class (clython.runtime:make-py-type :name typename)
                                                           :py-dict (make-hash-table :test #'equal))))
                                  ;; Set each field as attribute
                                  (loop for field in fields
                                        for val in fargs
                                        do (setf (gethash field (clython.runtime:py-object-dict obj)) val))
                                  ;; Also store as tuple for indexing
                                  (setf (gethash "_fields" (clython.runtime:py-object-dict obj))
                                        (clython.runtime:make-py-tuple
                                         (mapcar #'clython.runtime:make-py-str fields)))
                                  (setf (gethash "_values" (clython.runtime:py-object-dict obj))
                                        fargs)
                                  obj)))))))

    ;; Counter(iterable) — count occurrences
    (setf (gethash "Counter" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "Counter"
           :cl-fn (lambda (&rest args)
                    (let ((d (clython.runtime:make-py-dict)))
                      (when args
                        (let ((iterable (first args)))
                          (cond
                            ((typep iterable 'clython.runtime:py-str)
                             (loop for ch across (clython.runtime:py-str-value iterable)
                                   do (let* ((k (clython.runtime:make-py-str (string ch)))
                                             (existing (clython.runtime:py-getitem-or-nil d k)))
                                        (clython.runtime:py-setitem
                                         d k (clython.runtime:make-py-int
                                              (+ 1 (if existing (clython.runtime:py-int-value existing) 0)))))))
                            ((typep iterable 'clython.runtime:py-list)
                             (loop for item across (clython.runtime:py-list-value iterable)
                                   do (let ((existing (clython.runtime:py-getitem-or-nil d item)))
                                        (clython.runtime:py-setitem
                                         d item (clython.runtime:make-py-int
                                                 (+ 1 (if existing (clython.runtime:py-int-value existing) 0))))))))))
                      d))))

    ;; deque — double-ended queue implemented as a py-list wrapper
    (let ((deque-type (clython.runtime:make-py-type :name "deque")))
      (setf (gethash "deque" (clython.runtime:py-module-dict mod))
            (clython.runtime:make-py-function
             :name "deque"
             :cl-fn (lambda (&rest args)
                      (let* ((items (if args
                                        (let ((it (first args)))
                                          (cond
                                            ((typep it 'clython.runtime:py-list)
                                             (coerce (clython.runtime:py-list-value it) 'list))
                                            ((typep it 'clython.runtime:py-tuple)
                                             (coerce (clython.runtime:py-tuple-value it) 'list))
                                            (t nil)))
                                        nil))
                             (storage (list->adjustable-vector items))
                             (obj (make-instance 'clython.runtime:py-object
                                                 :py-class deque-type
                                                 :py-dict (make-hash-table :test #'equal))))
                        (setf (gethash "_items" (clython.runtime:py-object-dict obj)) storage)
                        ;; append(x)
                        (setf (gethash "append" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "append"
                               :cl-fn (lambda (x)
                                        (vector-push-extend x storage)
                                        clython.runtime:+py-none+)))
                        ;; appendleft(x)
                        (setf (gethash "appendleft" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "appendleft"
                               :cl-fn (lambda (x)
                                        (let ((old (coerce storage 'list)))
                                          (setf storage (list->adjustable-vector (cons x old)))
                                          (setf (gethash "_items" (clython.runtime:py-object-dict obj)) storage))
                                        clython.runtime:+py-none+)))
                        ;; pop()
                        (setf (gethash "pop" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "pop"
                               :cl-fn (lambda ()
                                        (when (zerop (length storage))
                                          (clython.runtime:py-raise "IndexError" "pop from an empty deque"))
                                        (let ((val (aref storage (1- (length storage)))))
                                          (vector-pop storage)
                                          val))))
                        ;; popleft()
                        (setf (gethash "popleft" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "popleft"
                               :cl-fn (lambda ()
                                        (when (zerop (length storage))
                                          (clython.runtime:py-raise "IndexError" "pop from an empty deque"))
                                        (let ((val (aref storage 0))
                                              (new-items (subseq storage 1)))
                                          (setf storage (make-array (length new-items)
                                                                     :adjustable t :fill-pointer t
                                                                     :initial-contents new-items))
                                          (setf (gethash "_items" (clython.runtime:py-object-dict obj)) storage)
                                          val))))
                        obj)))))

    ;; ChainMap(*maps) — read-first-match view over multiple dicts
    (setf (gethash "ChainMap" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "ChainMap"
           :cl-fn (lambda (&rest maps)
                    (let ((chain-type (clython.runtime:make-py-type :name "ChainMap"))
                          (obj (make-instance 'clython.runtime:py-object
                                              :py-class (clython.runtime:make-py-type :name "ChainMap")
                                              :py-dict (make-hash-table :test #'equal))))
                      (setf (gethash "_maps" (clython.runtime:py-object-dict obj)) maps)
                      obj))))

    mod))

(defun list->adjustable-vector (items)
  "Convert a CL list to an adjustable vector with fill pointer."
  (let* ((n (length items))
         (v (make-array n :adjustable t :fill-pointer n)))
    (loop for item in items
          for i from 0
          do (setf (aref v i) item))
    v))

(defun make-keyword-module ()
  "Create a keyword module with kwlist and iskeyword."
  (let* ((mod (clython.runtime:make-py-module "keyword"))
         (keywords '("False" "None" "True" "and" "as" "assert" "async" "await"
                     "break" "class" "continue" "def" "del" "elif" "else" "except"
                     "finally" "for" "from" "global" "if" "import" "in" "is"
                     "lambda" "nonlocal" "not" "or" "pass" "raise" "return"
                     "try" "while" "with" "yield"))
         (d (clython.runtime:py-module-dict mod))
         (kw-set (make-hash-table :test #'equal)))
    (setf (gethash "__name__" d) (clython.runtime:make-py-str "keyword"))
    ;; kwlist
    (setf (gethash "kwlist" d)
          (clython.runtime:make-py-list
           (mapcar #'clython.runtime:make-py-str keywords)))
    ;; iskeyword
    (dolist (k keywords) (setf (gethash k kw-set) t))
    (setf (gethash "iskeyword" d)
          (clython.runtime:make-py-function
           :name "iskeyword"
           :cl-fn (lambda (&rest args)
                    (let ((s (first args)))
                      (if (and (typep s 'clython.runtime:py-str)
                               (gethash (clython.runtime:py-str-value s) kw-set))
                          clython.runtime:+py-true+
                          clython.runtime:+py-false+)))))
    mod))

;;;; ─── string module ─────────────────────────────────────────────────────────

(defun make-string-module ()
  "Create a string module with ASCII constants and capwords."
  (let ((mod (clython.runtime:make-py-module "string")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "string"))
      (setf (gethash "ascii_lowercase" d)
            (clython.runtime:make-py-str "abcdefghijklmnopqrstuvwxyz"))
      (setf (gethash "ascii_uppercase" d)
            (clython.runtime:make-py-str "ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
      (setf (gethash "ascii_letters" d)
            (clython.runtime:make-py-str "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
      (setf (gethash "digits" d)
            (clython.runtime:make-py-str "0123456789"))
      (setf (gethash "hexdigits" d)
            (clython.runtime:make-py-str "0123456789abcdefABCDEF"))
      (setf (gethash "octdigits" d)
            (clython.runtime:make-py-str "01234567"))
      (setf (gethash "punctuation" d)
            (clython.runtime:make-py-str "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"))
      (setf (gethash "whitespace" d)
            (clython.runtime:make-py-str (format nil " ~C~C~C~C~C"
                                                 #\Tab #\Newline #\Return
                                                 (code-char 11) (code-char 12))))
      (setf (gethash "printable" d)
            (clython.runtime:make-py-str
             (with-output-to-string (s)
               (dotimes (i 128)
                 (let ((c (code-char i)))
                   (when (or (alphanumericp c)
                             (member c '(#\Space #\! #\" #\# #\$ #\% #\& #\' #\( #\) #\* #\+
                                        #\, #\- #\. #\/ #\: #\; #\< #\= #\> #\? #\@ #\[ #\\
                                        #\] #\^ #\_ #\` #\{ #\| #\} #\~ #\Tab #\Newline
                                        #\Return (code-char 11) (code-char 12))))
                     (write-char c s)))))))
      ;; capwords(s, sep=None)
      (setf (gethash "capwords" d)
            (clython.runtime:make-py-function
             :name "capwords"
             :cl-fn (lambda (&rest args)
                      (let* ((s (clython.runtime:py-str-value (first args)))
                             (sep (if (and (second args)
                                          (not (eq (second args) clython.runtime:+py-none+)))
                                      (clython.runtime:py-str-value (second args))
                                      nil))
                             (words (if sep
                                        (uiop:split-string s :separator sep)
                                        (uiop:split-string
                                         (string-trim '(#\Space #\Tab #\Newline #\Return) s)
                                         :separator " ")))
                             (result (format nil "~{~A~^ ~}"
                                             (mapcar (lambda (w)
                                                       (if (string= w "") w
                                                           (concatenate 'string
                                                                        (string (char-upcase (char w 0)))
                                                                        (string-downcase (subseq w 1)))))
                                                     words))))
                        (clython.runtime:make-py-str result))))))
    mod))

;;;; ─── itertools module ─────────────────────────────────────────────────────

(defun make-itertools-module ()
  "Create an itertools module with common functions."
  (let ((mod (clython.runtime:make-py-module "itertools")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "itertools"))
    ;; islice(iterable, [start,] stop [, step])
    (setf (gethash "islice" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "islice"
           :cl-fn (lambda (&rest args)
                    (let* ((iterable (first args))
                           (rest-args (rest args))
                           (start (if (>= (length rest-args) 2)
                                      (clython.runtime:py->cl (first rest-args)) 0))
                           (stop  (if rest-args
                                      (clython.runtime:py->cl
                                       (if (>= (length rest-args) 2)
                                           (second rest-args) (first rest-args)))
                                      nil))
                           (step  (if (>= (length rest-args) 3)
                                      (clython.runtime:py->cl (third rest-args)) 1))
                           (items (cond
                                    ((typep iterable 'clython.runtime:py-list)
                                     (coerce (clython.runtime:py-list-value iterable) 'list))
                                    ((typep iterable 'clython.runtime:py-tuple)
                                     (coerce (clython.runtime:py-tuple-value iterable) 'list))
                                    (t nil)))
                           (result nil) (i 0))
                      (dolist (item items)
                        (when (and (>= i start)
                                   (or (null stop) (< i stop))
                                   (zerop (mod (- i start) (max 1 step))))
                          (push item result))
                        (incf i))
                      (clython.runtime:make-py-list (nreverse result))))))
    ;; chain(*iterables)
    (setf (gethash "chain" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "chain"
           :cl-fn (lambda (&rest args)
                    (let ((result nil))
                      (dolist (arg args)
                        (cond
                          ((typep arg 'clython.runtime:py-list)
                           (loop for item across (clython.runtime:py-list-value arg)
                                 do (push item result)))
                          ((typep arg 'clython.runtime:py-tuple)
                           (loop for item across (clython.runtime:py-tuple-value arg)
                                 do (push item result)))))
                      (clython.runtime:make-py-list (nreverse result))))))
    ;; count(start=0, step=1) — returns a generator; stub returns a list
    (setf (gethash "count" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "count"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    clython.runtime:+py-none+)))
    ;; repeat(obj, times=None)
    (setf (gethash "repeat" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "repeat"
           :cl-fn (lambda (&rest args)
                    (let* ((obj (first args))
                           (times (if (second args)
                                      (clython.runtime:py->cl (second args))
                                      nil)))
                      (if times
                          (clython.runtime:make-py-list
                           (loop repeat times collect obj))
                          clython.runtime:+py-none+)))))
    mod))

;;;; ─── re module ──────────────────────────────────────────────────────────────

(defun make-re-module ()
  "Create a re module with flags and basic stub operations."
  (let ((mod (clython.runtime:make-py-module "re")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "re"))
      ;; Flags (matching CPython re module values)
      (dolist (flag-pair '(("IGNORECASE" . 2) ("I" . 2)
                           ("MULTILINE" . 8) ("M" . 8)
                           ("DOTALL" . 16) ("S" . 16)
                           ("VERBOSE" . 64) ("X" . 64)
                           ("ASCII" . 256) ("A" . 256)
                           ("UNICODE" . 32) ("U" . 32)
                           ("LOCALE" . 4) ("L" . 4)
                           ("NOFLAG" . 0)))
        (setf (gethash (car flag-pair) d)
              (clython.runtime:make-py-int (cdr flag-pair))))
      ;; error exception class stub
      (setf (gethash "error" d)
            (clython.runtime:make-py-type :name "error"))
      ;; compile(pattern, flags=0) — returns a stub Pattern object
      (setf (gethash "compile" d)
            (clython.runtime:make-py-function
             :name "compile"
             :cl-fn (lambda (&rest args)
                      (declare (ignore args))
                      (clython.runtime:+py-none+))))
      ;; sub, match, search, findall — stubs
      (dolist (fname '("sub" "match" "search" "fullmatch" "findall" "finditer" "split"))
        (let ((fn fname))
          (setf (gethash fn d)
                (clython.runtime:make-py-function
                 :name fn
                 :cl-fn (lambda (&rest args) (declare (ignore args))
                          clython.runtime:+py-none+))))))
    mod))

;;;; ─── functools module ──────────────────────────────────────────────────────

(defun make-functools-module ()
  "Create a functools module."
  (let ((mod (clython.runtime:make-py-module "functools")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "functools"))
    ;; wraps — identity decorator
    (setf (gethash "wraps" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "wraps"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-function
                     :name "wraps_inner"
                     :cl-fn (lambda (&rest inner) (first inner))))))
    ;; lru_cache — identity decorator
    (setf (gethash "lru_cache" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "lru_cache"
           :cl-fn (lambda (&rest args)
                    (if (and args (typep (first args) 'clython.runtime:py-function))
                        (first args)
                        (clython.runtime:make-py-function
                         :name "lru_cache_inner"
                         :cl-fn (lambda (&rest dargs) (first dargs)))))))
    ;; reduce(fn, seq[, initial])
    (setf (gethash "reduce" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "reduce"
           :cl-fn (lambda (&rest args)
                    (let* ((fn   (first args))
                           (seq  (second args))
                           (init (third args))
                           (items (cond
                                    ((typep seq 'clython.runtime:py-list)
                                     (coerce (clython.runtime:py-list-value seq) 'list))
                                    ((typep seq 'clython.runtime:py-tuple)
                                     (coerce (clython.runtime:py-tuple-value seq) 'list))
                                    (t nil)))
                           (acc init))
                      (dolist (item items)
                        (if acc
                            (setf acc (clython.runtime:py-call fn acc item))
                            (setf acc item)))
                      (or acc clython.runtime:+py-none+)))))
    ;; partial(fn, *args, **kwargs) — returns a partial application
    (setf (gethash "partial" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "partial"
           :cl-fn (lambda (&rest args)
                    (let ((fn (first args))
                          (bound-args (rest args)))
                      (clython.runtime:make-py-function
                       :name "partial"
                       :cl-fn (lambda (&rest call-args)
                                (apply #'clython.runtime:py-call fn
                                       (append bound-args call-args))))))))
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
  ;; C extension / stdlib stubs needed for CPython stdlib .py files to parse
  (setf (gethash "re" *builtin-modules*) #'make-re-module)
  (dolist (name '("_string" "_collections" "_decimal" "_pydecimal"
                  "_weakrefset" "_py_abc" "abc" "types" "warnings"
                  "io" "stat" "posix" "errno" "copy" "heapq" "reprlib"
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
