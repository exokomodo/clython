;;;; modules/itertools.lisp — itertools built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Helpers
;;;; ─────────────────────────────────────────────────────────────────────────

(defmacro %with-iteration-stop (&body body)
  "Run BODY, returning normally when StopIteration is signalled."
  (let ((blk (gensym "DONE")))
    `(block ,blk
       (handler-bind
           ((clython.runtime:stop-iteration
              (lambda (c) (declare (ignore c)) (return-from ,blk)))
            (clython.runtime:py-exception
              (lambda (c)
                (let ((v (clython.runtime:py-exception-value c)))
                  (when (and (typep v 'clython.runtime:py-exception-object)
                             (string= (clython.runtime:py-exception-class-name v)
                                      "StopIteration"))
                    (return-from ,blk))))))
         ,@body))))

(defun %itertools-collect (obj)
  "Fully drain any Python iterable into a CL list of py-objects."
  (let ((it (clython.runtime:py-iter obj))
        (acc nil))
    (%with-iteration-stop
      (loop (push (clython.runtime:py-next it) acc)))
    (nreverse acc)))

(defun %itertools-kwarg (name)
  "Look up NAME in the current call's kwargs, or NIL when absent."
  (cdr (assoc name clython.runtime:*current-kwargs* :test #'string=)))

(defun %itertools-fn (name lambda-list-fn)
  (clython.runtime:make-py-function :name name :cl-fn lambda-list-fn))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Module constructor
;;;; ─────────────────────────────────────────────────────────────────────────

(defun make-itertools-module ()
  "Create an itertools module with common functions."
  (let ((mod (clython.runtime:make-py-module "itertools")))
    (macrolet ((def (name &body body)
                 `(setf (gethash ,name (clython.runtime:py-module-dict mod))
                        (%itertools-fn ,name (lambda (&rest args)
                                               (declare (ignorable args))
                                               ,@body)))))

      (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
            (clython.runtime:make-py-str "itertools"))

      ;; ── islice(iterable, [start,] stop [, step]) ───────────────────────────
      (def "islice"
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
               (it (clython.runtime:py-iter iterable))
               (result nil) (i 0))
          (%with-iteration-stop
            (loop
              (when (and stop (>= i stop)) (return))
              (let ((item (clython.runtime:py-next it)))
                (when (and (>= i start)
                           (zerop (mod (- i start) (max 1 step))))
                  (push item result))
                (incf i))))
          (clython.runtime:make-py-list (nreverse result))))

      ;; ── chain(*iterables) ──────────────────────────────────────────────────
      (def "chain"
        (clython.runtime:make-py-list
         (loop for arg in args append (%itertools-collect arg))))

      ;; ── count(start=0, step=1) — infinite lazy generator ───────────────────
      (def "count"
        (let ((start (if args (clython.runtime:py->cl (first args)) 0))
              (step  (if (second args) (clython.runtime:py->cl (second args)) 1)))
          (clython.runtime:make-py-generator
           (lambda (yield-fn)
             (let ((n start))
               (loop
                 (funcall yield-fn (clython.runtime:cl->py n))
                 (incf n step)))))))

      ;; ── cycle(iterable) — infinite lazy generator ──────────────────────────
      (def "cycle"
        (let ((items (%itertools-collect (first args))))
          (clython.runtime:make-py-generator
           (lambda (yield-fn)
             (when items
               (loop (dolist (item items) (funcall yield-fn item))))))))

      ;; ── repeat(obj, times=None) ────────────────────────────────────────────
      (def "repeat"
        (let* ((obj (first args))
               (times (if (second args) (clython.runtime:py->cl (second args)) nil)))
          (if times
              (clython.runtime:make-py-list (loop repeat times collect obj))
              (clython.runtime:make-py-generator
               (lambda (yield-fn) (loop (funcall yield-fn obj)))))))

      ;; ── takewhile(predicate, iterable) ─────────────────────────────────────
      (def "takewhile"
        (let ((pred (first args))
              (it   (clython.runtime:py-iter (second args)))
              (acc  nil))
          (%with-iteration-stop
            (loop
              (let ((item (clython.runtime:py-next it)))
                (unless (clython.runtime:py-bool-val
                         (clython.runtime:py-call pred item))
                  (return))
                (push item acc))))
          (clython.runtime:make-py-list (nreverse acc))))

      ;; ── dropwhile(predicate, iterable) ─────────────────────────────────────
      (def "dropwhile"
        (let ((pred (first args))
              (it   (clython.runtime:py-iter (second args)))
              (acc  nil)
              (dropping t))
          (%with-iteration-stop
            (loop
              (let ((item (clython.runtime:py-next it)))
                (when (and dropping
                           (not (clython.runtime:py-bool-val
                                 (clython.runtime:py-call pred item))))
                  (setf dropping nil))
                (unless dropping (push item acc)))))
          (clython.runtime:make-py-list (nreverse acc))))

      ;; ── filterfalse(predicate, iterable) ───────────────────────────────────
      (def "filterfalse"
        (let ((pred (first args)))
          (clython.runtime:make-py-list
           (remove-if (lambda (item)
                        (if (or (null pred)
                                (eq pred clython.runtime:+py-none+))
                            (clython.runtime:py-bool-val item)
                            (clython.runtime:py-bool-val
                             (clython.runtime:py-call pred item))))
                      (%itertools-collect (second args))))))

      ;; ── compress(data, selectors) ──────────────────────────────────────────
      (def "compress"
        (let ((data (%itertools-collect (first args)))
              (sel  (%itertools-collect (second args))))
          (clython.runtime:make-py-list
           (loop for d in data
                 for s in sel
                 when (clython.runtime:py-bool-val s) collect d))))

      ;; ── accumulate(iterable, func=operator.add) ────────────────────────────
      (def "accumulate"
        (let* ((items (%itertools-collect (first args)))
               (func  (second args))
               (acc   nil)
               (total nil))
          (dolist (item items)
            (setf total
                  (cond ((null total) item)
                        ((and func (not (eq func clython.runtime:+py-none+)))
                         (clython.runtime:py-call func total item))
                        (t (clython.runtime:py-add total item))))
            (push total acc))
          (clython.runtime:make-py-list (nreverse acc))))

      ;; ── starmap(function, iterable-of-argtuples) ───────────────────────────
      (def "starmap"
        (let ((func (first args)))
          (clython.runtime:make-py-list
           (mapcar (lambda (tup)
                     (apply #'clython.runtime:py-call func
                            (%itertools-collect tup)))
                   (%itertools-collect (second args))))))

      ;; ── groupby(iterable, key=None) ────────────────────────────────────────
      ;; Simplification: groups are eagerly materialised lists, not sub-iterators.
      (def "groupby"
        (let* ((items (%itertools-collect (first args)))
               (keyfn (or (second args) (%itertools-kwarg "key")))
               (groups nil)
               (cur-key nil) (cur-group nil) (started nil))
          (flet ((key-of (item)
                   (if (and keyfn (not (eq keyfn clython.runtime:+py-none+)))
                       (clython.runtime:py-call keyfn item)
                       item))
                 (flush ()
                   (when started
                     (push (clython.runtime:make-py-tuple
                            (list cur-key
                                  (clython.runtime:make-py-list
                                   (nreverse cur-group))))
                           groups))))
            (dolist (item items)
              (let ((k (key-of item)))
                (cond
                  ((not started)
                   (setf started t cur-key k cur-group (list item)))
                  ((clython.runtime:py-eq k cur-key)
                   (push item cur-group))
                  (t (flush)
                     (setf cur-key k cur-group (list item))))))
            (flush))
          (clython.runtime:make-py-list (nreverse groups))))

      ;; ── zip_longest(*iterables, fillvalue=None) ────────────────────────────
      (def "zip_longest"
        (let* ((fill (or (%itertools-kwarg "fillvalue")
                         clython.runtime:+py-none+))
               (seqs (mapcar #'%itertools-collect args))
               (len  (if seqs (reduce #'max (mapcar #'length seqs)) 0)))
          (clython.runtime:make-py-list
           (loop for i from 0 below len
                 collect (clython.runtime:make-py-tuple
                          (mapcar (lambda (s)
                                    (if (< i (length s)) (nth i s) fill))
                                  seqs))))))

      ;; ── product(*iterables, repeat=1) ──────────────────────────────────────
      (def "product"
        (let* ((rep-arg (%itertools-kwarg "repeat"))
               (rep (if rep-arg (clython.runtime:py->cl rep-arg) 1))
               (pools (loop repeat rep
                            append (mapcar #'%itertools-collect args)))
               (result (list nil)))
          (dolist (pool pools)
            (setf result
                  (loop for prefix in result
                        append (loop for item in pool
                                     collect (append prefix (list item))))))
          (clython.runtime:make-py-list
           (mapcar #'clython.runtime:make-py-tuple result))))

      ;; ── combinations(iterable, r) ──────────────────────────────────────────
      (def "combinations"
        (let* ((pool (%itertools-collect (first args)))
               (r (clython.runtime:py->cl (second args)))
               (n (length pool))
               (acc nil))
          (labels ((walk (start chosen k)
                     (if (zerop k)
                         (push (reverse chosen) acc)
                         (loop for i from start below n
                               do (walk (1+ i) (cons (nth i pool) chosen)
                                        (1- k))))))
            (when (<= 0 r n) (walk 0 nil r)))
          (clython.runtime:make-py-list
           (mapcar #'clython.runtime:make-py-tuple (nreverse acc)))))

      ;; ── permutations(iterable, r=None) ─────────────────────────────────────
      (def "permutations"
        (let* ((pool (%itertools-collect (first args)))
               (n (length pool))
               (r (if (and (second args)
                           (not (eq (second args) clython.runtime:+py-none+)))
                      (clython.runtime:py->cl (second args))
                      n))
               (acc nil))
          (labels ((walk (used chosen k)
                     (if (zerop k)
                         (push (reverse chosen) acc)
                         (loop for i from 0 below n
                               unless (member i used)
                                 do (walk (cons i used)
                                          (cons (nth i pool) chosen)
                                          (1- k))))))
            (when (<= 0 r n) (walk nil nil r)))
          (clython.runtime:make-py-list
           (mapcar #'clython.runtime:make-py-tuple (nreverse acc))))))

    mod))
