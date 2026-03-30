;;;; modules/collections.lisp — collections built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

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
    (let ((chainmap-type (clython.runtime:make-py-type :name "ChainMap")))
      ;; Install __getitem__ on the type so cm['key'] works
      (setf (gethash "__getitem__" (clython.runtime:py-type-dict chainmap-type))
            (clython.runtime:make-py-function
             :name "__getitem__"
             :cl-fn (lambda (self key)
                      (let ((maps (gethash "_maps" (clython.runtime:py-object-dict self))))
                        (dolist (m maps
                                   (clython.runtime:py-raise "KeyError"
                                     "~A" (clython.runtime:py-repr key)))
                          (when (typep m 'clython.runtime:py-dict)
                            (let ((val (clython.runtime:py-getitem-or-nil m key)))
                              (when val (return val)))))))))
      (setf (gethash "ChainMap" (clython.runtime:py-module-dict mod))
            (clython.runtime:make-py-function
             :name "ChainMap"
             :cl-fn (lambda (&rest maps)
                      (let ((obj (make-instance 'clython.runtime:py-object
                                                :py-class chainmap-type
                                                :py-dict (make-hash-table :test #'equal))))
                        (setf (gethash "_maps" (clython.runtime:py-object-dict obj)) maps)
                        obj)))))

    ;; defaultdict(default_factory) — dict with default value factory
    (let ((dd-type (clython.runtime:make-py-type :name "defaultdict")))
      (setf (gethash "defaultdict" (clython.runtime:py-module-dict mod))
            (clython.runtime:make-py-function
             :name "defaultdict"
             :cl-fn (lambda (&rest args)
                      (let* ((factory (if args (first args) clython.runtime:+py-none+))
                             (d (clython.runtime:make-py-dict))
                             (obj (make-instance 'clython.runtime:py-object
                                                 :py-class dd-type
                                                 :py-dict (make-hash-table :test #'equal))))
                        (setf (gethash "_dict" (clython.runtime:py-object-dict obj)) d)
                        (setf (gethash "_factory" (clython.runtime:py-object-dict obj)) factory)
                        (setf (gethash "__getitem__" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "__getitem__"
                               :cl-fn (lambda (key)
                                        (let* ((k (clython.runtime:py->cl key))
                                               (ht (clython.runtime:py-dict-value d)))
                                          (multiple-value-bind (val found) (gethash k ht)
                                            (if found val
                                                (let ((default (clython.runtime:py-call factory)))
                                                  (setf (gethash k ht) default)
                                                  default)))))))
                        (setf (gethash "__setitem__" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "__setitem__"
                               :cl-fn (lambda (key val)
                                        (setf (gethash (clython.runtime:py->cl key)
                                                       (clython.runtime:py-dict-value d))
                                              val)
                                        clython.runtime:+py-none+)))
                        (setf (gethash "__str__" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "__str__"
                               :cl-fn (lambda ()
                                        (clython.runtime:make-py-str
                                         (clython.runtime:py-repr d)))))
                        obj)))))

    mod))

