;;;; builtins.lisp — Python built-in functions
;;;;
;;;; Each built-in is a py-function whose :cl-fn slot holds a CL lambda.
;;;; The global *builtins* hash-table maps name strings → py-function objects.

(defpackage :clython.builtins
  (:use :cl :clython.runtime)
  (:import-from :clython.runtime
                #:py-bool-from-cl
                #:py-bool-raw
                #:stop-iteration)
  (:export
   #:*builtins*
   ;; Individual built-in py-function objects
   #:+builtin-print+
   #:+builtin-repr+
   #:+builtin-str+
   #:+builtin-int+
   #:+builtin-float+
   #:+builtin-bool+
   #:+builtin-type+
   #:+builtin-len+
   #:+builtin-isinstance+
   #:+builtin-issubclass+
   #:+builtin-range+
   #:+builtin-list+
   #:+builtin-tuple+
   #:+builtin-dict+
   #:+builtin-set+
   #:+builtin-frozenset+
   #:+builtin-abs+
   #:+builtin-min+
   #:+builtin-max+
   #:+builtin-sum+
   #:+builtin-id+
   #:+builtin-hash+
   #:+builtin-callable+
   #:+builtin-iter+
   #:+builtin-next+
   #:+builtin-chr+
   #:+builtin-ord+
   #:+builtin-hex+
   #:+builtin-oct+
   #:+builtin-bin+
   #:+builtin-any+
   #:+builtin-all+
   #:+builtin-sorted+
   #:+builtin-reversed+
   #:+builtin-enumerate+
   #:+builtin-zip+
   #:+builtin-map+
   #:+builtin-filter+
   #:+builtin-input+
   #:+builtin-getattr+
   #:+builtin-setattr+
   #:+builtin-hasattr+
   #:+builtin-delattr+
   #:+builtin-staticmethod+
   #:+builtin-classmethod+
   #:+builtin-property+))

(in-package :clython.builtins)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Helper macro
;;;; ─────────────────────────────────────────────────────────────────────────

(defmacro defbuiltin (var-name py-name (&rest params) &body body)
  "Define a built-in function stored in VAR-NAME with Python name PY-NAME.
   PARAMS are CL lambda-list parameters; BODY is the implementation."
  `(defvar ,var-name
     (make-py-function
      :name ,py-name
      :cl-fn (lambda (,@params) ,@body))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Iteration helper (collect items from any iterable into a CL list)
;;;; ─────────────────────────────────────────────────────────────────────────

(defun collect-iter (iterable)
  "Exhaust a Python iterable and return a CL list of py-objects."
  (let ((it (py-iter iterable))
        (result '()))
    (handler-case
        (loop (push (py-next it) result))
      (stop-iteration () (nreverse result)))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; print
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-print+ "print" (&rest args)
  (let* ((kwargs *current-kwargs*)
         (sep-pair (assoc "sep" kwargs :test #'string=))
         (end-pair (assoc "end" kwargs :test #'string=))
         (sep (if (and sep-pair (typep (cdr sep-pair) 'py-str))
                  (py-str-value (cdr sep-pair))
                  " "))
         (end (if (and end-pair (typep (cdr end-pair) 'py-str))
                  (py-str-value (cdr end-pair))
                  (string #\Newline))))
    (format t "~{~A~}" (loop for (obj . rest) on (mapcar #'py-str-of args)
                              collect obj
                              when rest collect sep))
    (write-string end)
    +py-none+))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; repr / str
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-repr+ "repr" (obj)
  (make-py-str (py-repr obj)))

(defbuiltin +builtin-str+ "str" (&rest args)
  (if (null args)
      (make-py-str "")
      (make-py-str (py-str-of (first args)))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; int / float / bool / type
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-int+ "int" (&rest args)
  (if (null args)
      (make-py-int 0)
      (let ((obj (first args))
            (base (second args)))
        (cond
          ((typep obj 'py-int)   obj)
          ((typep obj 'py-float) (make-py-int (truncate (py-float-value obj))))
          ((typep obj 'py-bool)  (make-py-int (if (py-bool-raw obj) 1 0)))
          ((typep obj 'py-str)
           (make-py-int
            (parse-integer (py-str-value obj)
                           :radix (if base (py-int-value base) 10))))
          (t (clython.runtime:py-raise "TypeError" "int() argument must be a string, a bytes-like object or a real number, not '~A'"
                    (py-type-of obj)))))))

(defbuiltin +builtin-float+ "float" (&rest args)
  (if (null args)
      (make-py-float 0.0d0)
      (let ((obj (first args)))
        (cond
          ((typep obj 'py-float) obj)
          ((typep obj 'py-int)   (make-py-float (float (py-int-value obj) 1.0d0)))
          ((typep obj 'py-bool)  (make-py-float (if (py-bool-raw obj) 1.0d0 0.0d0)))
          ((typep obj 'py-str)
           (make-py-float (float (read-from-string (py-str-value obj)) 1.0d0)))
          (t (clython.runtime:py-raise "TypeError" "float() argument must be a string or a real number, not '~A'"
                    (py-type-of obj)))))))

(defbuiltin +builtin-bool+ "bool" (&rest args)
  (if (null args)
      +py-false+
      (py-bool-from-cl (py-bool-val (first args)))))

(defbuiltin +builtin-type+ "type" (obj)
  (make-py-type :name (py-type-of obj)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; len
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-len+ "len" (obj)
  (make-py-int (py-len obj)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; isinstance / issubclass
;;;; ─────────────────────────────────────────────────────────────────────────

(defun %py-type-name->cl-class (name)
  "Map a Python type name to a CL class for isinstance checks."
  (cond
    ((string= name "NoneType")  'py-none)
    ((string= name "bool")      'py-bool)
    ((string= name "int")       'py-int)
    ((string= name "float")     'py-float)
    ((string= name "complex")   'py-complex)
    ((string= name "str")       'py-str)
    ((string= name "bytes")     'py-bytes)
    ((string= name "list")      'py-list)
    ((string= name "tuple")     'py-tuple)
    ((string= name "dict")      'py-dict)
    ((string= name "set")       'py-set)
    ((string= name "frozenset") 'py-frozenset)
    ((string= name "function")  'py-function)
    ((string= name "type")      'py-type)
    ((string= name "module")    'py-module)
    (t nil)))

(defun %is-subtype-p (cls target)
  "Check if CLS is TARGET or has TARGET as an ancestor in its bases."
  (when (typep cls 'py-type)
    (or (eq cls target)
        (some (lambda (base) (%is-subtype-p base target))
              (py-type-bases cls)))))

(defbuiltin +builtin-isinstance+ "isinstance" (obj typeobj)
  (py-bool-from-cl
   (let* ((name (cond
                  ((typep typeobj 'py-type) (py-type-name typeobj))
                  ((typep typeobj 'py-function) (py-function-name typeobj))
                  (t "")))
          (cl-class (%py-type-name->cl-class name)))
     (if cl-class
         (typep obj cl-class)
         ;; Check user-defined classes with full hierarchy walk
         (and (typep typeobj 'py-type)
              (let ((obj-cls (py-object-class obj)))
                (%is-subtype-p obj-cls typeobj)))))))

(defbuiltin +builtin-issubclass+ "issubclass" (subtype supertype)
  ;; Simplified: compare type names
  (py-bool-from-cl
   (string= (py-type-name subtype) (py-type-name supertype))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; range
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-range+ "range" (&rest args)
  (cond
    ((= (length args) 1)
     (make-py-range 0 (py-int-value (first args)) 1))
    ((= (length args) 2)
     (make-py-range (py-int-value (first args))
                    (py-int-value (second args))
                    1))
    ((= (length args) 3)
     (make-py-range (py-int-value (first args))
                    (py-int-value (second args))
                    (py-int-value (third args))))
    (t (clython.runtime:py-raise "TypeError" "range expected 1-3 arguments, got ~D" (length args)))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; list / tuple / dict / set
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-list+ "list" (&rest args)
  (if (null args)
      (make-py-list)
      (make-py-list (collect-iter (first args)))))

(defbuiltin +builtin-tuple+ "tuple" (&rest args)
  (if (null args)
      (make-py-tuple)
      (make-py-tuple (collect-iter (first args)))))

(defbuiltin +builtin-dict+ "dict" (&rest args)
  (if (null args)
      (make-py-dict)
      ;; Accept another dict and copy it
      (let ((result (make-py-dict))
            (src (first args)))
        (when (typep src 'py-dict)
          (maphash (lambda (k v)
                     (setf (gethash k (py-dict-value result)) v))
                   (py-dict-value src)))
        result)))

(defbuiltin +builtin-set+ "set" (&rest args)
  (if (null args)
      (make-py-set)
      (make-py-set (collect-iter (first args)))))

(defbuiltin +builtin-frozenset+ "frozenset" (&rest args)
  (if (null args)
      (make-py-frozenset)
      (make-py-frozenset (collect-iter (first args)))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; abs / min / max / sum
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-abs+ "abs" (obj)
  (py-abs obj))

(defbuiltin +builtin-min+ "min" (&rest args)
  (let ((items (if (and (= (length args) 1)
                        (not (typep (first args) 'py-int))
                        (not (typep (first args) 'py-float)))
                   (collect-iter (first args))
                   args)))
    (when (null items)
      (clython.runtime:py-raise "ValueError" "min() arg is an empty sequence"))
    (reduce (lambda (a b) (if (py-lt a b) a b)) items)))

(defbuiltin +builtin-max+ "max" (&rest args)
  (let ((items (if (and (= (length args) 1)
                        (not (typep (first args) 'py-int))
                        (not (typep (first args) 'py-float)))
                   (collect-iter (first args))
                   args)))
    (when (null items)
      (clython.runtime:py-raise "ValueError" "max() arg is an empty sequence"))
    (reduce (lambda (a b) (if (py-gt a b) a b)) items)))

(defbuiltin +builtin-sum+ "sum" (&rest args)
  (let ((iterable (first args))
        (start (if (second args) (second args) (make-py-int 0))))
    (reduce #'py-add (collect-iter iterable) :initial-value start)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; id / hash / callable
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-id+ "id" (obj)
  (make-py-int (py-id obj)))

(defbuiltin +builtin-hash+ "hash" (obj)
  (make-py-int (py-hash obj)))

(defbuiltin +builtin-callable+ "callable" (obj)
  (py-bool-from-cl (or (typep obj 'py-function)
                       (typep obj 'py-method)
                       (typep obj 'py-type))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; iter / next
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-iter+ "iter" (obj)
  (py-iter obj))

(defbuiltin +builtin-next+ "next" (&rest args)
  (let ((it (first args))
        (default (second args)))
    (handler-case
        (py-next it)
      (stop-iteration ()
        (if default
            default
            (py-raise "StopIteration" ""))))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; chr / ord
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-chr+ "chr" (obj)
  (make-py-str (string (code-char (py-int-value obj)))))

(defbuiltin +builtin-ord+ "ord" (obj)
  (let ((s (py-str-value obj)))
    (unless (= (length s) 1)
      (clython.runtime:py-raise "TypeError" "ord() expected a character, but string of length ~D found"
             (length s)))
    (make-py-int (char-code (char s 0)))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; hex / oct / bin
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-hex+ "hex" (obj)
  (make-py-str (format nil "0x~(~x~)" (py-int-value obj))))

(defbuiltin +builtin-oct+ "oct" (obj)
  (make-py-str (format nil "0o~o" (py-int-value obj))))

(defbuiltin +builtin-bin+ "bin" (obj)
  (make-py-str (format nil "0b~b" (py-int-value obj))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; any / all
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-any+ "any" (iterable)
  (py-bool-from-cl
   (some #'py-bool-val (collect-iter iterable))))

(defbuiltin +builtin-all+ "all" (iterable)
  (py-bool-from-cl
   (every #'py-bool-val (collect-iter iterable))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; sorted / reversed
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-sorted+ "sorted" (&rest args)
  (let* ((iterable (first args))
         (items (collect-iter iterable))
         (key-fn (getf (rest args) :key nil))
         (reverse-p (getf (rest args) :reverse nil))
         (sorted (sort (copy-list items)
                       (lambda (a b)
                         (if key-fn
                             (py-lt (py-call key-fn a) (py-call key-fn b))
                             (py-lt a b))))))
    (make-py-list (if (and reverse-p (py-bool-val reverse-p))
                      (nreverse sorted)
                      sorted))))

(defbuiltin +builtin-reversed+ "reversed" (obj)
  (let ((items (cond
                 ((typep obj 'py-list)
                  (reverse (coerce (py-list-value obj) 'list)))
                 ((typep obj 'py-tuple)
                  (reverse (coerce (py-tuple-value obj) 'list)))
                 (t (reverse (collect-iter obj))))))
    (make-py-iterator
     (let ((lst items))
       (lambda ()
         (if (null lst)
             (error 'stop-iteration)
             (pop lst)))))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; enumerate / zip / map / filter
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-enumerate+ "enumerate" (&rest args)
  (let* ((iterable (first args))
         (start (if (second args) (py-int-value (second args)) 0))
         (it (py-iter iterable))
         (counter start))
    (make-py-iterator
     (lambda ()
       (let ((val (py-next it)))  ; may signal stop-iteration
         (prog1 (make-py-tuple (list (make-py-int counter) val))
           (incf counter)))))))

(defbuiltin +builtin-zip+ "zip" (&rest iterables)
  (let ((iters (mapcar #'py-iter iterables)))
    (make-py-iterator
     (lambda ()
       (handler-case
           (make-py-tuple (mapcar #'py-next iters))
         (stop-iteration () (error 'stop-iteration)))))))

(defbuiltin +builtin-map+ "map" (fn &rest iterables)
  (let ((iters (mapcar #'py-iter iterables)))
    (make-py-iterator
     (lambda ()
       (let ((args (handler-case (mapcar #'py-next iters)
                     (stop-iteration () (error 'stop-iteration)))))
         (apply #'py-call fn args))))))

(defbuiltin +builtin-filter+ "filter" (fn iterable)
  (let ((it (py-iter iterable)))
    (make-py-iterator
     (lambda ()
       (loop
         (let ((item (py-next it)))  ; may signal stop-iteration
           (when (py-bool-val (if (typep fn 'py-none)
                                  item
                                  (py-call fn item)))
             (return item))))))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; input
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-input+ "input" (&rest args)
  (when args
    (format t "~A" (py-str-of (first args)))
    (force-output))
  (let ((line (read-line *standard-input* nil "")))
    (make-py-str line)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; getattr / setattr / hasattr / delattr
;;;; ─────────────────────────────────────────────────────────────────────────

(defbuiltin +builtin-getattr+ "getattr" (&rest args)
  (let ((obj     (first args))
        (name    (py-str-value (second args)))
        (default (third args)))
    (handler-case
        (py-getattr obj name)
      (error ()
        (if default
            default
            (clython.runtime:py-raise "AttributeError" "object has no attribute '~A'" name))))))

(defbuiltin +builtin-setattr+ "setattr" (obj name value)
  (py-setattr obj (py-str-value name) value)
  +py-none+)

(defbuiltin +builtin-hasattr+ "hasattr" (obj name)
  (py-bool-from-cl
   (handler-case
       (progn (py-getattr obj (py-str-value name)) t)
     (error () nil))))

(defbuiltin +builtin-delattr+ "delattr" (obj name)
  (py-delattr obj (py-str-value name))
  +py-none+)

;;; staticmethod / classmethod / property

(defbuiltin +builtin-staticmethod+ "staticmethod" (func)
  (make-instance 'py-staticmethod-wrapper :function func))

(defbuiltin +builtin-classmethod+ "classmethod" (func)
  (make-instance 'py-classmethod-wrapper :function func))

(defbuiltin +builtin-property+ "property" (&rest args)
  (make-instance 'py-property-wrapper
                 :fget (if (>= (length args) 1) (first args) nil)
                 :fset (if (>= (length args) 2) (second args) nil)))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Global builtins table
;;;; ─────────────────────────────────────────────────────────────────────────

(defvar *builtins* (make-hash-table :test #'equal)
  "Maps Python builtin name strings to their py-function objects.")

(defun %register-builtins ()
  (let ((pairs
         (list (cons "print"        +builtin-print+)
               (cons "repr"         +builtin-repr+)
               (cons "str"          +builtin-str+)
               (cons "int"          +builtin-int+)
               (cons "float"        +builtin-float+)
               (cons "bool"         +builtin-bool+)
               (cons "type"         +builtin-type+)
               (cons "len"          +builtin-len+)
               (cons "isinstance"   +builtin-isinstance+)
               (cons "issubclass"   +builtin-issubclass+)
               (cons "range"        +builtin-range+)
               (cons "list"         +builtin-list+)
               (cons "tuple"        +builtin-tuple+)
               (cons "dict"         +builtin-dict+)
               (cons "set"          +builtin-set+)
               (cons "frozenset"    +builtin-frozenset+)
               (cons "abs"          +builtin-abs+)
               (cons "min"          +builtin-min+)
               (cons "max"          +builtin-max+)
               (cons "sum"          +builtin-sum+)
               (cons "id"           +builtin-id+)
               (cons "hash"         +builtin-hash+)
               (cons "callable"     +builtin-callable+)
               (cons "iter"         +builtin-iter+)
               (cons "next"         +builtin-next+)
               (cons "chr"          +builtin-chr+)
               (cons "ord"          +builtin-ord+)
               (cons "hex"          +builtin-hex+)
               (cons "oct"          +builtin-oct+)
               (cons "bin"          +builtin-bin+)
               (cons "any"          +builtin-any+)
               (cons "all"          +builtin-all+)
               (cons "sorted"       +builtin-sorted+)
               (cons "reversed"     +builtin-reversed+)
               (cons "enumerate"    +builtin-enumerate+)
               (cons "zip"          +builtin-zip+)
               (cons "map"          +builtin-map+)
               (cons "filter"       +builtin-filter+)
               (cons "input"        +builtin-input+)
               (cons "getattr"      +builtin-getattr+)
               (cons "setattr"      +builtin-setattr+)
               (cons "hasattr"      +builtin-hasattr+)
               (cons "delattr"      +builtin-delattr+)
               (cons "staticmethod" +builtin-staticmethod+)
               (cons "classmethod"  +builtin-classmethod+)
               (cons "property"     +builtin-property+))))
    (dolist (pair pairs)
      (setf (gethash (car pair) *builtins*) (cdr pair)))))

(%register-builtins)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Exception classes — registered as callable py-type objects in *builtins*
;;;; ─────────────────────────────────────────────────────────────────────────

(defun %make-exception-type (name)
  "Create a callable py-function that acts as a Python exception class constructor.
   When called with args, it creates a py-exception-object instance."
  (make-py-function :name name
                    :cl-fn (lambda (&rest args)
                              (make-py-exception-object name args))))

(defun %register-exception-builtins ()
  "Register all Python built-in exception names in *builtins*."
  (dolist (name '("BaseException"
                  "Exception"
                  "ArithmeticError"
                  "ZeroDivisionError"
                  "OverflowError"
                  "FloatingPointError"
                  "AssertionError"
                  "AttributeError"
                  "EOFError"
                  "ImportError"
                  "ModuleNotFoundError"
                  "LookupError"
                  "IndexError"
                  "KeyError"
                  "NameError"
                  "UnboundLocalError"
                  "OSError"
                  "FileNotFoundError"
                  "PermissionError"
                  "FileExistsError"
                  "IsADirectoryError"
                  "NotADirectoryError"
                  "RuntimeError"
                  "RecursionError"
                  "NotImplementedError"
                  "StopIteration"
                  "StopAsyncIteration"
                  "SyntaxError"
                  "IndentationError"
                  "TabError"
                  "TypeError"
                  "ValueError"
                  "UnicodeError"
                  "KeyboardInterrupt"
                  "SystemExit"
                  "GeneratorExit"))
    (setf (gethash name *builtins*) (%make-exception-type name))))

(%register-exception-builtins)


