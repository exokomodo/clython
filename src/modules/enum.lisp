;;;; modules/enum.lisp — enum built-in module
;;;;
;;;; Implements Enum, IntEnum, and auto() for Python's enum module.
;;;; When a class inherits from Enum, each non-dunder class attribute
;;;; becomes an enum member with .name and .value, and the class becomes
;;;; callable to look up members by value.

(in-package :clython.imports)

;;; ─── Enum member factory ─────────────────────────────────────────────────

(defun %make-enum-member (cls member-name member-value)
  "Create an enum member instance — a py-object of class CLS with .name and .value."
  (let* ((obj  (make-instance 'clython.runtime:py-object))
         (idict (make-hash-table :test #'equal)))
    (setf (clython.runtime:py-object-class obj) cls)
    (setf (gethash "_name_"  idict) (clython.runtime:make-py-str member-name))
    (setf (gethash "_value_" idict) member-value)
    ;; Expose as .name and .value
    (setf (gethash "name"  idict) (clython.runtime:make-py-str member-name))
    (setf (gethash "value" idict) member-value)
    (setf (clython.runtime:py-object-dict obj) idict)
    obj))

;;; ─── Apply enum transformation to a class ────────────────────────────────

(defun %apply-enum (cls)
  "Transform CLS into a proper enum class.
   - Turns non-dunder class-level values into member objects
   - Adds a _member_map_ dict and _members_ list to the class
   - Makes the class callable to look up members by value
   Returns CLS (mutated in place)."
  (let* ((tdict    (clython.runtime:py-type-dict cls))
         (members  '())          ; (name . py-object) pairs in definition order
         (by-value (make-hash-table :test #'equal)))

    ;; Collect member definitions (non-dunder, non-callable attributes)
    (let ((member-names '()))
      (maphash (lambda (k v)
                 (when (and (> (length k) 0)
                            (not (and (>= (length k) 4)
                                      (string= (subseq k 0 2) "__")
                                      (string= (subseq k (- (length k) 2)) "__")))
                            (not (typep v 'clython.runtime:py-function))
                            (not (typep v 'clython.runtime:py-type)))
                   (push k member-names)))
               tdict)
      ;; Sort by insertion order isn't available, so just alphabetical for now
      (setf member-names (sort member-names #'string<))

      ;; Build member objects and replace raw values in the class dict
      (dolist (mname member-names)
        (let* ((raw-val (gethash mname tdict))
               (member  (%make-enum-member cls mname raw-val)))
          (setf (gethash mname tdict) member)
          (push (cons mname member) members)
          ;; Index by value for reverse lookup
          (let ((val-key (clython.runtime:py-repr raw-val)))
            (setf (gethash val-key by-value) member)))))

    (setf members (nreverse members))

    ;; Store _member_map_ and _members_ list on the class
    (let ((member-map-dict (clython.runtime:make-py-dict)))
      (dolist (pair members)
        (clython.runtime:py-setitem member-map-dict
                                    (clython.runtime:make-py-str (car pair))
                                    (cdr pair)))
      (setf (gethash "_member_map_" tdict) member-map-dict))

    (setf (gethash "_members_" tdict)
          (clython.runtime:make-py-list (mapcar #'cdr members)))

    ;; Make the class callable for value lookup: MyEnum(1) → MyEnum.X
    (let ((bv by-value))
      (setf (gethash "__new__" tdict)
            (clython.runtime:make-py-function
             :name "__new__"
             :cl-fn (lambda (meta-or-val &rest rest)
                      ;; Called as MyEnum(value) — meta-or-val is the class (from py-call dispatch)
                      ;; or the value if py-call strips the class
                      (let ((search-val (if rest (first rest) meta-or-val)))
                        (let ((key (clython.runtime:py-repr search-val)))
                          (multiple-value-bind (found hit) (gethash key bv)
                            (if hit
                                found
                                (clython.runtime:py-raise
                                 "ValueError"
                                 "~A is not a valid ~A"
                                 (clython.runtime:py-repr search-val)
                                 (clython.runtime:py-type-name cls))))))))))

    cls))

;;; ─── EnumMeta __init_subclass__ ──────────────────────────────────────────

(defun %make-enum-base ()
  "Create the Enum base class with an __init_subclass__ classmethod
   that transforms subclasses into proper enum classes."
  (let* ((tdict (make-hash-table :test #'equal))
         (enum-cls (clython.runtime:make-py-type
                    :name "Enum"
                    :bases '()
                    :tdict tdict)))
    ;; __init_subclass__ fires when a class inheriting from Enum is created.
    ;; eval.lisp calls this with the new subclass as the single argument.
    (setf (gethash "__init_subclass__" tdict)
          (clython.runtime:make-py-function
           :name "__init_subclass__"
           :cl-fn (lambda (subclass &rest args)
                    (declare (ignore args))
                    (when (typep subclass 'clython.runtime:py-type)
                      (%apply-enum subclass))
                    clython.runtime:+py-none+)))

    ;; __repr__ for enum members (accessed via py-getattr dispatch on instances)
    (setf (gethash "__repr__" tdict)
          (clython.runtime:make-py-function
           :name "__repr__"
           :cl-fn (lambda (self)
                    (let* ((idict (clython.runtime:py-object-dict self))
                           (cls   (clython.runtime:py-object-class self))
                           (cname (if cls (clython.runtime:py-type-name cls) "Enum"))
                           (mname (gethash "name" idict))
                           (name-str (if mname
                                         (clython.runtime:py-str-value mname)
                                         "?")))
                      (clython.runtime:make-py-str
                       (format nil "<~A.~A: ~A>"
                               cname name-str
                               (let ((v (gethash "value" idict)))
                                 (if v (clython.runtime:py-repr v) "?"))))))))

    ;; __str__
    (setf (gethash "__str__" tdict)
          (clython.runtime:make-py-function
           :name "__str__"
           :cl-fn (lambda (self)
                    (let* ((idict (clython.runtime:py-object-dict self))
                           (cls   (clython.runtime:py-object-class self))
                           (cname (if cls (clython.runtime:py-type-name cls) "Enum"))
                           (mname (gethash "name" idict))
                           (name-str (if mname
                                         (clython.runtime:py-str-value mname)
                                         "?")))
                      (clython.runtime:make-py-str
                       (format nil "~A.~A" cname name-str))))))

    ;; __eq__
    (setf (gethash "__eq__" tdict)
          (clython.runtime:make-py-function
           :name "__eq__"
           :cl-fn (lambda (self other)
                    (clython.runtime:cl->py
                     (and (typep other 'clython.runtime:py-object)
                          (eq self other))))))

    ;; __hash__
    (setf (gethash "__hash__" tdict)
          (clython.runtime:make-py-function
           :name "__hash__"
           :cl-fn (lambda (self)
                    (clython.runtime:make-py-int (sxhash self)))))

    enum-cls))

;;; ─── IntEnum ──────────────────────────────────────────────────────────────

(defun %make-intenum-base (enum-base)
  "Create IntEnum — inherits from Enum; members are also ints."
  (let* ((tdict (make-hash-table :test #'equal))
         (intenum-cls (clython.runtime:make-py-type
                       :name "IntEnum"
                       :bases (list enum-base)
                       :tdict tdict)))
    ;; __init_subclass__ delegates to Enum's version
    (setf (gethash "__init_subclass__" tdict)
          (clython.runtime:make-py-function
           :name "__init_subclass__"
           :cl-fn (lambda (subclass &rest args)
                    (declare (ignore args))
                    (when (typep subclass 'clython.runtime:py-type)
                      (%apply-enum subclass))
                    clython.runtime:+py-none+)))
    intenum-cls))

;;; ─── auto() ───────────────────────────────────────────────────────────────

(let ((auto-counter 0))
  (defun %make-auto-fn ()
    "Return a py-function that generates sequential integer values."
    (clython.runtime:make-py-function
     :name "auto"
     :cl-fn (lambda (&rest args)
              (declare (ignore args))
              (incf auto-counter)
              (clython.runtime:make-py-int auto-counter)))))

;;; ─── Module constructor ───────────────────────────────────────────────────

(defun make-enum-module ()
  "Create the enum built-in module."
  (let ((mod      (clython.runtime:make-py-module "enum"))
        (d        nil)
        (enum-cls (%make-enum-base)))
    (setf d (clython.runtime:py-module-dict mod))

    (setf (gethash "Enum"    d) enum-cls)
    (setf (gethash "IntEnum" d) (%make-intenum-base enum-cls))
    (setf (gethash "auto"    d) (%make-auto-fn))

    ;; Flag stubs
    (setf (gethash "Flag"    d) enum-cls)   ; alias for now
    (setf (gethash "IntFlag" d) enum-cls)   ; alias for now

    (setf (gethash "__name__" d) (clython.runtime:make-py-str "enum"))
    mod))
