;;;; eval.lisp — Tree-walking AST evaluator for Clython
;;;;
;;;; Evaluates parsed AST nodes in an environment, producing Python objects.

(defpackage :clython.eval
  (:use :cl)
  (:export
   #:eval-node
   #:py-return-value
   #:py-return-value-val
   #:py-break
   #:py-continue
   #:py-exception
   #:py-exception-value))

(in-package :clython.eval)

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Control flow conditions
;;;; ═══════════════════════════════════════════════════════════════════════════

(define-condition py-return-value ()
  ((val :initarg :val :reader py-return-value-val :initform nil))
  (:documentation "Signalled by `return` to unwind to the enclosing function."))

(define-condition py-break ()
  ()
  (:documentation "Signalled by `break` to exit a loop."))

(define-condition py-continue ()
  ()
  (:documentation "Signalled by `continue` to skip to the next iteration."))

(define-condition py-exception (error)
  ((value :initarg :value :reader py-exception-value
          :initform nil))
  (:report (lambda (c stream)
             (let ((v (py-exception-value c)))
               (cond
                 ((typep v 'clython.runtime:py-exception-object)
                  (let ((name (clython.runtime:py-exception-class-name v))
                        (msg  (clython.runtime:py-exception-message v)))
                    (if (string= msg "")
                        (format stream "~A" name)
                        (format stream "~A: ~A" name msg))))
                 ((typep v 'clython.runtime:py-object)
                  (format stream "~A" (clython.runtime:py-str-of v)))
                 (t (format stream "~A" v))))))
  (:documentation "Signalled by `raise` — wraps a Python exception object."))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Generic function
;;;; ═══════════════════════════════════════════════════════════════════════════

(defvar *current-exception* nil
  "The currently active exception (py-exception condition), for bare `raise`.")

(defvar *generator-yield-fn* nil
  "When non-nil, we are executing inside a generator body.
   Calling this function yields a value and suspends execution.")

(defgeneric eval-node (node env)
  (:documentation "Evaluate an AST node in the given environment."))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Module evaluation
;;;; ═══════════════════════════════════════════════════════════════════════════

(defmethod eval-node ((node clython.ast:module-node) env)
  (let ((result clython.runtime:+py-none+)
        (body (clython.ast:module-node-body node)))
    ;; Parser produces body in reverse order; sort by line number
    (setf body (%sort-body body))
    (dolist (stmt body result)
      (setf result (eval-node stmt env)))))

(defun %sort-body (stmts)
  "Sort statement list by source line number (ascending).
   The parser may produce them in reverse order."
  (when (null stmts) (return-from %sort-body nil))
  (when (null (cdr stmts)) (return-from %sort-body stmts))
  ;; Check if already sorted
  (let ((first-line (clython.ast:node-line (first stmts)))
        (last-line (clython.ast:node-line (car (last stmts)))))
    (if (and first-line last-line (> first-line last-line))
        (stable-sort (copy-list stmts) #'<
                     :key (lambda (s) (or (clython.ast:node-line s) 0)))
        stmts)))

(defmethod eval-node ((node clython.ast:interactive-node) env)
  (let ((result clython.runtime:+py-none+))
    (dolist (stmt (%sort-body (clython.ast:interactive-node-body node)) result)
      (setf result (eval-node stmt env)))))

(defmethod eval-node ((node clython.ast:expression-node) env)
  (eval-node (clython.ast:expression-node-body node) env))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Literals / Atoms
;;;; ═══════════════════════════════════════════════════════════════════════════

(defun %unquote-string (s)
  "Strip quotes and string prefix from a Python string literal token value.
   E.g. \"hello\" → hello, 'hi' → hi, r\"raw\" → raw, \"\"\"triple\"\"\" → triple
   Handles raw strings (r prefix) by skipping escape processing."
  (let ((start 0)
        (len (length s))
        (raw-p nil))
    ;; Skip prefix characters (b, r, u, f, B, R, U, F)
    (loop while (and (< start len)
                     (find (char s start) "brufBRUF"))
          do (when (find (char s start) "rR") (setf raw-p t))
             (incf start))
    ;; Now determine quote style
    (when (< start len)
      (let ((qc (char s start)))
        (when (or (char= qc #\") (char= qc #\'))
          ;; Check for triple quotes
          (if (and (<= (+ start 3) len)
                   (char= (char s (+ start 1)) qc)
                   (char= (char s (+ start 2)) qc))
              ;; Triple-quoted: strip 3 chars from each end
              (setf s (subseq s (+ start 3) (- len 3)))
              ;; Single-quoted: strip 1 char from each end
              (setf s (subseq s (+ start 1) (- len 1)))))))
    ;; Process escape sequences (skip for raw strings)
    (if raw-p s (%process-escapes s))))

(defun %process-escapes (s)
  "Process Python escape sequences in a string."
  (with-output-to-string (out)
    (let ((i 0) (len (length s)))
      (loop while (< i len) do
        (let ((c (char s i)))
          (if (and (char= c #\\) (< (1+ i) len))
              (let ((next (char s (1+ i))))
                (case next
                  (#\n (write-char #\Newline out) (incf i 2))
                  (#\t (write-char #\Tab out) (incf i 2))
                  (#\r (write-char #\Return out) (incf i 2))
                  (#\\ (write-char #\\ out) (incf i 2))
                  (#\' (write-char #\' out) (incf i 2))
                  (#\" (write-char #\" out) (incf i 2))
                  (#\0 (write-char (code-char 0) out) (incf i 2))
                  (#\a (write-char (code-char 7) out) (incf i 2))
                  (#\b (write-char #\Backspace out) (incf i 2))
                  (#\f (write-char #\Page out) (incf i 2))
                  (#\v (write-char (code-char 11) out) (incf i 2))
                  (#\x
                   ;; \xNN hex escape
                   (if (< (+ i 3) len)
                       (let ((hex (subseq s (+ i 2) (+ i 4))))
                         (write-char (code-char (parse-integer hex :radix 16)) out)
                         (incf i 4))
                       (progn (write-char c out) (incf i))))
                  (t (write-char c out) (write-char next out) (incf i 2))))
              (progn (write-char c out) (incf i))))))))

(defmethod eval-node ((node clython.ast:constant-node) env)
  (declare (ignore env))
  (let ((val (clython.ast:constant-node-value node)))
    (cond
      ((eq val t)        clython.runtime:+py-true+)
      ((eq val nil)      clython.runtime:+py-false+)
      ((eq val :none)    clython.runtime:+py-none+)
      ((eq val :ellipsis) clython.runtime:+py-ellipsis+)
      ((integerp val)    (clython.runtime:make-py-int val))
      ((floatp val)      (clython.runtime:make-py-float (coerce val 'double-float)))
      ((complexp val)    (clython.runtime:make-py-complex val))
      ((stringp val)     (clython.runtime:make-py-str (%unquote-string val)))
      ;; Adjacent string concatenation: (:concat-strings "part1" "part2" ...)
      ((and (consp val) (eq (car val) :concat-strings))
       (clython.runtime:make-py-str
        (apply #'concatenate 'string
               (mapcar #'%unquote-string (cdr val)))))
      (t (error "Unknown constant value: ~S" val)))))

(defmethod eval-node ((node clython.ast:name-node) env)
  (clython.scope:env-get (clython.ast:name-node-id node) env))

(defun %eval-elts-with-star (elts env)
  "Evaluate a list of element nodes, expanding starred nodes inline."
  (let ((result nil))
    (dolist (elt elts (nreverse result))
      (if (typep elt 'clython.ast:starred-node)
          ;; Unpack the iterable
          (let ((val (eval-node (clython.ast:starred-node-value elt) env)))
            (cond
              ((typep val 'clython.runtime:py-list)
               (loop for item across (clython.runtime:py-list-value val)
                     do (push item result)))
              ((typep val 'clython.runtime:py-tuple)
               (loop for item across (clython.runtime:py-tuple-value val)
                     do (push item result)))
              (t ;; generic iterable — use py-iter/py-next
               (let ((it (clython.runtime:py-iter val)))
                 (handler-case
                     (loop (push (clython.runtime:py-next it) result))
                   (clython.runtime:stop-iteration () nil))))))
          (push (eval-node elt env) result)))))

(defmethod eval-node ((node clython.ast:list-node) env)
  (clython.runtime:make-py-list (%eval-elts-with-star
                                  (clython.ast:list-node-elts node) env)))

(defmethod eval-node ((node clython.ast:tuple-node) env)
  (clython.runtime:make-py-tuple (%eval-elts-with-star
                                   (clython.ast:tuple-node-elts node) env)))

(defmethod eval-node ((node clython.ast:dict-node) env)
  (let ((d (clython.runtime:make-py-dict)))
    (loop for k-node in (clython.ast:dict-node-keys node)
          for v-node in (clython.ast:dict-node-values node)
          do (if (null k-node)
                 ;; **unpacking: k-node is nil, v-node is the dict to unpack
                 (let ((src (eval-node v-node env)))
                   (when (typep src 'clython.runtime:py-dict)
                     (maphash (lambda (k v)
                                (clython.runtime:py-setitem
                                 d (clython.runtime:make-py-str k) v))
                              (clython.runtime:py-dict-value src))))
                 ;; Normal key: value
                 (let ((k (eval-node k-node env))
                       (v (eval-node v-node env)))
                   (clython.runtime:py-setitem d k v))))
    d))

(defmethod eval-node ((node clython.ast:set-node) env)
  (clython.runtime:make-py-set (%eval-elts-with-star
                                 (clython.ast:set-node-elts node) env)))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Expressions
;;;; ═══════════════════════════════════════════════════════════════════════════

;;; ─── Binary operations ──────────────────────────────────────────────────────

(defun %binop-dispatch (op left right)
  "Dispatch a binary operation keyword to the appropriate runtime function."
  (ecase op
    (:add       (clython.runtime:py-add left right))
    (:sub       (clython.runtime:py-sub left right))
    (:mult      (clython.runtime:py-mul left right))
    (:div       (clython.runtime:py-truediv left right))
    (:mod       (clython.runtime:py-mod left right))
    (:pow       (clython.runtime:py-pow left right))
    (:floor-div (clython.runtime:py-floordiv left right))
    (:l-shift   (clython.runtime:py-lshift left right))
    (:r-shift   (clython.runtime:py-rshift left right))
    (:bit-and   (clython.runtime:py-and left right))
    (:bit-or    (clython.runtime:py-or left right))
    (:bit-xor   (clython.runtime:py-xor left right))
    (:mat-mult  (clython.runtime:py-raise "TypeError" "@ operator not supported"))))

(defmethod eval-node ((node clython.ast:bin-op-node) env)
  (let ((left  (eval-node (clython.ast:bin-op-node-left node) env))
        (right (eval-node (clython.ast:bin-op-node-right node) env)))
    (%binop-dispatch (clython.ast:bin-op-node-op node) left right)))

;;; ─── Unary operations ──────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:unary-op-node) env)
  (let ((operand (eval-node (clython.ast:unary-op-node-operand node) env))
        (op (clython.ast:unary-op-node-op node)))
    (ecase op
      (:u-sub  (clython.runtime:py-neg operand))
      (:u-add  (clython.runtime:py-pos operand))
      (:invert (clython.runtime:py-invert operand))
      (:not    (clython.runtime:py-bool-from-cl
                (not (clython.runtime:py-bool-val operand)))))))

;;; ─── Boolean operations (short-circuit) ─────────────────────────────────────

(defmethod eval-node ((node clython.ast:bool-op-node) env)
  (let ((op (clython.ast:bool-op-node-op node))
        (values (clython.ast:bool-op-node-values node)))
    (ecase op
      (:and
       (let ((result clython.runtime:+py-true+))
         (dolist (v-node values result)
           (setf result (eval-node v-node env))
           (unless (clython.runtime:py-bool-val result)
             (return result)))))
      (:or
       (let ((result clython.runtime:+py-false+))
         (dolist (v-node values result)
           (setf result (eval-node v-node env))
           (when (clython.runtime:py-bool-val result)
             (return result))))))))

;;; ─── Comparisons (chained) ──────────────────────────────────────────────────

(defun %compare-dispatch (op left right)
  "Dispatch a comparison operator keyword. Returns CL boolean."
  (ecase op
    (:eq      (clython.runtime:py-eq left right))
    (:not-eq  (clython.runtime:py-ne left right))
    (:lt      (clython.runtime:py-lt left right))
    (:lt-e    (clython.runtime:py-le left right))
    (:gt      (clython.runtime:py-gt left right))
    (:gt-e    (clython.runtime:py-ge left right))
    (:is      (eq left right))
    (:is-not  (not (eq left right)))
    (:in      (clython.runtime:py-contains right left))
    (:not-in  (not (clython.runtime:py-contains right left)))))

(defmethod eval-node ((node clython.ast:compare-node) env)
  (let ((left (eval-node (clython.ast:compare-node-left node) env))
        (ops (clython.ast:compare-node-ops node))
        (comparators (clython.ast:compare-node-comparators node)))
    (loop for op in ops
          for comp-node in comparators
          for right = (eval-node comp-node env)
          unless (%compare-dispatch op left right)
            do (return clython.runtime:+py-false+)
          do (setf left right)
          finally (return clython.runtime:+py-true+))))

;;; ─── Ternary (if expression) ────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:if-exp-node) env)
  (if (clython.runtime:py-bool-val (eval-node (clython.ast:if-exp-node-test node) env))
      (eval-node (clython.ast:if-exp-node-body node) env)
      (eval-node (clython.ast:if-exp-node-orelse node) env)))

;;; ─── Function/method calls ─────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:call-node) env)
  ;; Special-case builtins that need access to the calling environment
  (let ((func-node (clython.ast:call-node-func node)))
    (when (typep func-node 'clython.ast:name-node)
      (let ((fname (clython.ast:name-node-id func-node)))
        ;; super() with no args
        (when (and (string= fname "super")
                   (null (clython.ast:call-node-args node)))
          (let ((cls (ignore-errors (clython.scope:env-get "__class__" env)))
                (self (ignore-errors (clython.scope:env-get "self" env))))
            (when (and cls self)
              (return-from eval-node
                (make-instance 'clython.runtime:py-super :type cls :obj self)))))
        ;; globals() — return dict of global scope bindings
        (when (and (string= fname "globals")
                   (null (clython.ast:call-node-args node)))
          (let ((d (clython.runtime:make-py-dict))
                (global-env (loop with e = env
                                  while (clython.scope:env-parent e)
                                  do (setf e (clython.scope:env-parent e))
                                  finally (return e))))
            (maphash (lambda (k v)
                       (clython.runtime:py-setitem d (clython.runtime:make-py-str k) v))
                     (clython.scope:env-bindings global-env))
            (return-from eval-node d)))
        ;; locals() — return dict of current scope bindings
        (when (and (string= fname "locals")
                   (null (clython.ast:call-node-args node)))
          (let ((d (clython.runtime:make-py-dict)))
            (maphash (lambda (k v)
                       (clython.runtime:py-setitem d (clython.runtime:make-py-str k) v))
                     (clython.scope:env-bindings env))
            (return-from eval-node d))))))
  (let* ((func (eval-node (clython.ast:call-node-func node) env))
         (args (loop for a in (clython.ast:call-node-args node)
                     if (typep a 'clython.ast:starred-node)
                       ;; Star unpacking: *args → splice the iterable into the arg list
                       append (let ((val (eval-node (clython.ast:starred-node-value a) env)))
                                (coerce (cond
                                          ((typep val 'clython.runtime:py-list)
                                           (clython.runtime:py-list-value val))
                                          ((typep val 'clython.runtime:py-tuple)
                                           (clython.runtime:py-tuple-value val))
                                          (t (error "Cannot unpack ~A" val)))
                                        'list))
                     else
                       collect (eval-node a env)))
         (kw-nodes (clython.ast:call-node-keywords node))
         ;; Evaluate keyword arguments into an alist ((name . value) ...)
         (kwargs (mapcar (lambda (kw)
                           (cons (clython.ast:keyword-arg kw)
                                 (eval-node (clython.ast:keyword-value kw) env)))
                         kw-nodes)))
    ;; Check if this is a user-defined py-function with AST body (not a cl-fn builtin)
    (if (and (typep func 'clython.runtime:py-function)
             (clython.runtime:py-function-body func)
             (not (clython.runtime:py-function-cl-fn func)))
        ;; User-defined function: set up scope, bind params, eval body
        (%call-user-function func args kwargs)
        ;; Builtin or cl-fn backed function: pass kwargs via special variable
        (let ((clython.runtime:*current-kwargs* kwargs))
          (apply #'clython.runtime:py-call func args)))))

(defun %call-user-function-from-cl-fn (params body closure-env args &optional is-generator is-async)
  "Called from the cl-fn closure installed on user-defined functions.
   This allows py-call to work for decorators, callbacks, etc."
  (cond
    (is-generator
     (%make-generator-from-body params body closure-env args clython.runtime:*current-kwargs*))
    (is-async
     (%make-coroutine-from-body params body closure-env args clython.runtime:*current-kwargs*))
    (t
     (let ((call-env (clython.scope:env-extend closure-env)))
       (%bind-params params args call-env clython.runtime:*current-kwargs*)
       (handler-case
           (progn
             (dolist (stmt body)
               (eval-node stmt call-env))
             clython.runtime:+py-none+)
         (py-return-value (ret)
           (py-return-value-val ret)))))))

(defun %make-generator-from-body (params body closure-env args kwargs)
  "Create a py-generator that lazily executes BODY using a thread."
  (let ((call-env (clython.scope:env-extend closure-env)))
    (%bind-params params args call-env kwargs)
    (clython.runtime:make-py-generator
     (lambda (yield-fn)
       (let ((*generator-yield-fn* yield-fn))
         ;; Execute body — return just ends the generator
         (handler-case
             (dolist (stmt body)
               (eval-node stmt call-env))
           (py-return-value () nil)))))))  ;; return in generator = StopIteration

(defun %make-coroutine-from-body (params body closure-env args kwargs)
  "Create a py-coroutine that lazily executes BODY when awaited."
  (let ((call-env (clython.scope:env-extend closure-env)))
    (%bind-params params args call-env kwargs)
    (clython.runtime:make-py-coroutine
     (lambda ()
       (handler-case
           (progn
             (dolist (stmt body)
               (eval-node stmt call-env))
             clython.runtime:+py-none+)
         (py-return-value (ret)
           (py-return-value-val ret)))))))

(defun %call-user-function (func args &optional kwargs)
  "Call a user-defined py-function with the given evaluated arguments."
  (let* ((closure-env (clython.runtime:py-function-env func))
         (params (clython.runtime:py-function-params func))
         (body (clython.runtime:py-function-body func)))
    (cond
      ;; Generator function
      ((clython.runtime:py-function-generator func)
       (%make-generator-from-body params body closure-env args kwargs))
      ;; Async function: return a coroutine object
      ((clython.runtime:py-function-async-p func)
       (%make-coroutine-from-body params body closure-env args kwargs))
      ;; Normal function call
      (t
       (let ((call-env (clython.scope:env-extend closure-env)))
         (%bind-params params args call-env kwargs)
         (handler-case
             (progn
               (dolist (stmt body)
                 (eval-node stmt call-env))
               clython.runtime:+py-none+)
           (py-return-value (ret)
             (py-return-value-val ret))))))))

(defun %bind-params (params args env &optional kwargs)
  "Bind function parameters to argument values in ENV.
   PARAMS is a py-arguments object. KWARGS is an alist of (name . value)."
  (when (null params) (return-from %bind-params))
  (let* ((positional-params
           (append (or (clython.ast:arguments-posonlyargs params) nil)
                   (or (clython.ast:arguments-args params) nil)))
         (defaults (or (clython.ast:arguments-defaults params) nil))
         (num-positional (length positional-params))
         (num-defaults (length defaults))
         (num-required (- num-positional num-defaults))
         (vararg (clython.ast:arguments-vararg params))
         (kwonlyargs (or (clython.ast:arguments-kwonlyargs params) nil))
         (kw-defaults (or (clython.ast:arguments-kw-defaults params) nil))
         (kwarg (clython.ast:arguments-kwarg params))
         (remaining-kwargs (copy-list (or kwargs nil))))
    ;; Bind positional args (also check kwargs for missing positional params)
    (loop for i below num-positional
          for param in positional-params
          for name = (clython.ast:arg-arg param)
          do (cond
               ((< i (length args))
                (clython.scope:env-set name (nth i args) env))
               ;; Check kwargs for this parameter
               ((assoc name remaining-kwargs :test #'string=)
                (let ((pair (assoc name remaining-kwargs :test #'string=)))
                  (clython.scope:env-set name (cdr pair) env)
                  (setf remaining-kwargs (remove pair remaining-kwargs))))
               ;; Use default if available
               (t (let ((default-idx (- i num-required)))
                    (if (and (>= default-idx 0) (< default-idx num-defaults))
                        (clython.scope:env-set name (nth default-idx defaults) env)
                        (clython.runtime:py-raise "TypeError" "~A() missing required positional argument: '~A'"
                               "function" name))))))
    ;; Bind *args
    (when vararg
      (let ((extra-args (if (> (length args) num-positional)
                            (nthcdr num-positional args)
                            nil)))
        (clython.scope:env-set (clython.ast:arg-arg vararg)
                               (clython.runtime:make-py-tuple extra-args)
                               env)))
    ;; Bind keyword-only args (check kwargs, then use defaults)
    (loop for param in kwonlyargs
          for default in kw-defaults
          for name = (clython.ast:arg-arg param)
          do (let ((kwpair (assoc name remaining-kwargs :test #'string=)))
               (cond
                 (kwpair
                  (clython.scope:env-set name (cdr kwpair) env)
                  (setf remaining-kwargs (remove kwpair remaining-kwargs)))
                 (default
                  (clython.scope:env-set name default env)))))
    ;; Bind **kwargs (collect remaining kwargs)
    (when kwarg
      (let ((d (clython.runtime:make-py-dict)))
        (dolist (pair remaining-kwargs)
          (when (car pair)
            (clython.runtime:py-setitem d
                                        (clython.runtime:make-py-str (car pair))
                                        (cdr pair))))
        (clython.scope:env-set (clython.ast:arg-arg kwarg) d env)))))

;;; ─── Attribute access ───────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:attribute-node) env)
  (let ((obj (eval-node (clython.ast:attribute-node-value node) env))
        (attr (clython.ast:attribute-node-attr node)))
    (clython.runtime:py-getattr obj attr)))

;;; ─── Subscript access ──────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:subscript-node) env)
  (let ((obj (eval-node (clython.ast:subscript-node-value node) env))
        (key (eval-node (clython.ast:subscript-node-slice node) env)))
    (clython.runtime:py-getitem obj key)))

;;; ─── Slice ──────────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:slice-node) env)
  (let ((lower (if (clython.ast:slice-node-lower node)
                   (eval-node (clython.ast:slice-node-lower node) env)
                   clython.runtime:+py-none+))
        (upper (if (clython.ast:slice-node-upper node)
                   (eval-node (clython.ast:slice-node-upper node) env)
                   clython.runtime:+py-none+))
        (step  (if (clython.ast:slice-node-step node)
                   (eval-node (clython.ast:slice-node-step node) env)
                   clython.runtime:+py-none+)))
    (clython.runtime:make-py-slice lower upper step)))

;;; ─── Starred expression ────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:starred-node) env)
  ;; In load context, evaluate the inner expression
  (eval-node (clython.ast:starred-node-value node) env))

;;; ─── Named expression (walrus operator) ────────────────────────────────────

(defmethod eval-node ((node clython.ast:named-expr-node) env)
  (let* ((value (eval-node (clython.ast:named-expr-node-value node) env))
         (target (clython.ast:named-expr-node-target node))
         (name (clython.ast:name-node-id target)))
    (clython.scope:env-set name value env)
    value))

;;; ─── Lambda ─────────────────────────────────────────────────────────────────

;;; ─── Yield expressions ─────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:yield-node) env)
  (unless *generator-yield-fn*
    (error "SyntaxError: 'yield' outside function"))
  (let ((val (if (clython.ast:yield-node-value node)
                 (eval-node (clython.ast:yield-node-value node) env)
                 clython.runtime:+py-none+)))
    (funcall *generator-yield-fn* val)))

(defmethod eval-node ((node clython.ast:yield-from-node) env)
  (unless *generator-yield-fn*
    (error "SyntaxError: 'yield from' outside function"))
  (let* ((iterable (eval-node (clython.ast:yield-from-node-value node) env))
         (iterator (clython.runtime:py-iter iterable)))
    (handler-case
        (loop
          (let ((val (clython.runtime:py-next iterator)))
            (funcall *generator-yield-fn* val)))
      (clython.runtime:stop-iteration () nil))
    clython.runtime:+py-none+))

;;; ─── Lambda ───────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:lambda-node) env)
  (let* ((evaled-params (%eval-defaults (clython.ast:lambda-node-args node) env))
         (body (list (make-instance 'clython.ast:return-node
                                    :value (clython.ast:lambda-node-body node)))))
    (clython.runtime:make-py-function
     :name "<lambda>"
     :params evaled-params
     :body body
     :env env
     :cl-fn (lambda (&rest args)
              (%call-user-function-from-cl-fn
               evaled-params body env args nil)))))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Comprehensions
;;;; ═══════════════════════════════════════════════════════════════════════════

(defun %eval-comprehension-generators (generators elt-fn env)
  "Evaluate nested comprehension generators, calling ELT-FN for each iteration."
  (if (null generators)
      (funcall elt-fn)
      (let* ((gen (first generators))
             (iter-val (eval-node (clython.ast:comprehension-iter gen) env))
             (iterator (clython.runtime:py-iter iter-val))
             (target (clython.ast:comprehension-target gen))
             (ifs (clython.ast:comprehension-ifs gen)))
        (handler-case
            (loop
              (let ((item (clython.runtime:py-next iterator)))
                (%assign-target target item env)
                ;; Check if conditions
                (when (every (lambda (if-node)
                               (clython.runtime:py-bool-val (eval-node if-node env)))
                             ifs)
                  (%eval-comprehension-generators (rest generators) elt-fn env))))
          (clython.runtime:stop-iteration () nil)))))

(defun %eval-genexp-generators (generators outer-iter node env yield-fn)
  "Evaluate generator expression generators, yielding each element via yield-fn.
   OUTER-ITER is the pre-evaluated outermost iterable."
  (let* ((gen (first generators))
         (iterator (if outer-iter
                       (clython.runtime:py-iter outer-iter)
                       (clython.runtime:py-iter
                        (eval-node (clython.ast:comprehension-iter gen) env))))
         (target (clython.ast:comprehension-target gen))
         (ifs (clython.ast:comprehension-ifs gen)))
    (handler-case
        (loop
          (let ((item (clython.runtime:py-next iterator)))
            (%assign-target target item env)
            (when (every (lambda (if-node)
                           (clython.runtime:py-bool-val (eval-node if-node env)))
                         ifs)
              (if (rest generators)
                  (%eval-genexp-generators (rest generators) nil node env yield-fn)
                  (funcall yield-fn
                           (eval-node (clython.ast:generator-exp-node-elt node) env))))))
      (clython.runtime:stop-iteration () nil))))

(defmethod eval-node ((node clython.ast:list-comp-node) env)
  (let ((comp-env (clython.scope:env-extend env))
        (results '()))
    (%eval-comprehension-generators
     (clython.ast:list-comp-node-generators node)
     (lambda ()
       (push (eval-node (clython.ast:list-comp-node-elt node) comp-env) results))
     comp-env)
    (clython.runtime:make-py-list (nreverse results))))

(defmethod eval-node ((node clython.ast:set-comp-node) env)
  (let ((comp-env (clython.scope:env-extend env))
        (results '()))
    (%eval-comprehension-generators
     (clython.ast:set-comp-node-generators node)
     (lambda ()
       (push (eval-node (clython.ast:set-comp-node-elt node) comp-env) results))
     comp-env)
    (clython.runtime:make-py-set (nreverse results))))

(defmethod eval-node ((node clython.ast:dict-comp-node) env)
  (let ((comp-env (clython.scope:env-extend env))
        (d (clython.runtime:make-py-dict)))
    (%eval-comprehension-generators
     (clython.ast:dict-comp-node-generators node)
     (lambda ()
       (let ((k (eval-node (clython.ast:dict-comp-node-key node) comp-env))
             (v (eval-node (clython.ast:dict-comp-node-value node) comp-env)))
         (clython.runtime:py-setitem d k v)))
     comp-env)
    d))

(defmethod eval-node ((node clython.ast:generator-exp-node) env)
  ;; Create a lazy generator using a thread
  (let ((generators (clython.ast:generator-exp-node-generators node))
        (comp-env (clython.scope:env-extend env)))
    ;; Pre-evaluate the outermost iterable now (at creation time, per Python semantics)
    (let ((outer-iter (eval-node (clython.ast:comprehension-iter (first generators))
                                  comp-env)))
      (clython.runtime:make-py-generator
       (lambda (yield-fn)
         (let ((*generator-yield-fn* yield-fn)
               (inner-env (clython.scope:env-extend comp-env)))
           (%eval-genexp-generators generators outer-iter node inner-env yield-fn)))))))

;;;; ═══════════════════════════════════════════════════════════════════════════
;;;; Statements
;;;; ═══════════════════════════════════════════════════════════════════════════

;;; ─── Expression statement ──────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:expr-stmt-node) env)
  (eval-node (clython.ast:expr-stmt-node-value node) env)
  clython.runtime:+py-none+)

;;; ─── Assignment ─────────────────────────────────────────────────────────────

(defun %assign-target (target value env)
  "Assign VALUE to TARGET in ENV, handling names, subscripts, attributes, and unpacking."
  (cond
    ;; Simple name assignment
    ((typep target 'clython.ast:name-node)
     (clython.scope:env-set (clython.ast:name-node-id target) value env))
    ;; Subscript assignment: obj[key] = value
    ((typep target 'clython.ast:subscript-node)
     (let ((obj (eval-node (clython.ast:subscript-node-value target) env))
           (key (eval-node (clython.ast:subscript-node-slice target) env)))
       (clython.runtime:py-setitem obj key value)))
    ;; Attribute assignment: obj.attr = value
    ((typep target 'clython.ast:attribute-node)
     (let ((obj (eval-node (clython.ast:attribute-node-value target) env))
           (attr (clython.ast:attribute-node-attr target)))
       (clython.runtime:py-setattr obj attr value)))
    ;; Tuple/list unpacking
    ((or (typep target 'clython.ast:tuple-node)
         (typep target 'clython.ast:list-node))
     (let* ((elts (if (typep target 'clython.ast:tuple-node)
                      (clython.ast:tuple-node-elts target)
                      (clython.ast:list-node-elts target)))
            (iter (clython.runtime:py-iter value))
            (items '()))
       ;; Collect all items from the iterable
       (handler-case
           (loop (push (clython.runtime:py-next iter) items))
         (clython.runtime:stop-iteration () nil))
       (setf items (nreverse items))
       ;; Check for starred element
       (let ((star-idx (position-if (lambda (e) (typep e 'clython.ast:starred-node)) elts)))
         (if star-idx
             ;; Starred unpacking
             (let* ((before star-idx)
                    (after (- (length elts) star-idx 1))
                    (star-count (- (length items) before after)))
               (loop for i below before
                     do (%assign-target (nth i elts) (nth i items) env))
               (%assign-target (clython.ast:starred-node-value (nth star-idx elts))
                               (clython.runtime:make-py-list
                                (subseq items before (+ before star-count)))
                               env)
               (loop for i from 1 to after
                     do (%assign-target (nth (+ star-idx i) elts)
                                        (nth (+ before star-count i -1) items)
                                        env)))
             ;; Simple unpacking
             (loop for elt in elts
                   for val in items
                   do (%assign-target elt val env))))))
    ;; Starred in assignment target context
    ((typep target 'clython.ast:starred-node)
     (%assign-target (clython.ast:starred-node-value target) value env))
    (t (clython.runtime:py-raise "SyntaxError" "cannot assign to ~A" (type-of target)))))

(defmethod eval-node ((node clython.ast:assign-node) env)
  (let ((value (eval-node (clython.ast:assign-node-value node) env)))
    (dolist (target (clython.ast:assign-node-targets node))
      (%assign-target target value env))
    clython.runtime:+py-none+))

;;; ─── Augmented assignment ──────────────────────────────────────────────────

(defun %iop-dunder-name (op)
  "Return the in-place dunder name for augmented assignment op keyword, or NIL."
  (case op
    (:add       "__iadd__")
    (:sub       "__isub__")
    (:mult      "__imul__")
    (:div       "__itruediv__")
    (:floor-div "__ifloordiv__")
    (:mod       "__imod__")
    (:pow       "__ipow__")
    (:bit-and   "__iand__")
    (:bit-or    "__ior__")
    (:bit-xor   "__ixor__")
    (:l-shift   "__ilshift__")
    (:r-shift   "__irshift__")
    (otherwise nil)))

(defmethod eval-node ((node clython.ast:aug-assign-node) env)
  (let* ((target (clython.ast:aug-assign-node-target node))
         (op (clython.ast:aug-assign-node-op node))
         (rhs (eval-node (clython.ast:aug-assign-node-value node) env))
         (current (eval-node target env))
         ;; Try in-place dunder first (e.g. __iadd__ for +=)
         (iop-name (%iop-dunder-name op))
         (iop-fn (when (and iop-name (typep current 'clython.runtime:py-object))
                   (clython.runtime:%lookup-dunder current iop-name)))
         (new-val (if iop-fn
                      (clython.runtime:py-call iop-fn current rhs)
                      (%binop-dispatch op current rhs))))
    (%assign-target target new-val env)
    clython.runtime:+py-none+))

;;; ─── Annotated assignment ──────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:ann-assign-node) env)
  (when (clython.ast:ann-assign-node-value node)
    (let ((value (eval-node (clython.ast:ann-assign-node-value node) env)))
      (%assign-target (clython.ast:ann-assign-node-target node) value env)))
  clython.runtime:+py-none+)

;;; ─── Return ─────────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:return-node) env)
  (let ((value (if (clython.ast:return-node-value node)
                   (eval-node (clython.ast:return-node-value node) env)
                   clython.runtime:+py-none+)))
    (signal 'py-return-value :val value)
    ;; If not caught (shouldn't happen in normal execution)
    value))

;;; ─── If statement ──────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:if-node) env)
  (if (clython.runtime:py-bool-val (eval-node (clython.ast:if-node-test node) env))
      (dolist (stmt (%sort-body (clython.ast:if-node-body node)) clython.runtime:+py-none+)
        (eval-node stmt env))
      (dolist (stmt (%sort-body (clython.ast:if-node-orelse node)) clython.runtime:+py-none+)
        (eval-node stmt env))))

;;; ─── While loop ─────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:while-node) env)
  (let ((broke nil))
    (block while-loop
      (loop while (clython.runtime:py-bool-val
                   (eval-node (clython.ast:while-node-test node) env))
            do (block while-body
                 (handler-case
                     (dolist (stmt (%sort-body (clython.ast:while-node-body node)))
                       (eval-node stmt env))
                   (py-break ()
                     (setf broke t)
                     (return-from while-loop nil))
                   (py-continue ()
                     (return-from while-body nil))))))
    (unless broke
      (dolist (stmt (%sort-body (clython.ast:while-node-orelse node)))
        (eval-node stmt env))))
  clython.runtime:+py-none+)

;;; ─── For loop ──────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:for-node) env)
  (let* ((iter-val (eval-node (clython.ast:for-node-iter node) env))
         (iterator (clython.runtime:py-iter iter-val))
         (target (clython.ast:for-node-target node))
         (broke nil))
    (block for-loop
      (handler-case
          (loop
            (let ((item (clython.runtime:py-next iterator)))
              (%assign-target target item env)
              (block for-body
                (handler-case
                    (dolist (stmt (%sort-body (clython.ast:for-node-body node)))
                      (eval-node stmt env))
                  (py-break ()
                    (setf broke t)
                    (return-from for-loop nil))
                  (py-continue ()
                    (return-from for-body nil))))))
        (clython.runtime:stop-iteration () nil)
        (py-exception (e)
          ;; Check if this is a StopIteration from user code
          (let ((v (py-exception-value e)))
            (unless (and (typep v 'clython.runtime:py-exception-object)
                         (string= (clython.runtime:py-exception-class-name v)
                                  "StopIteration"))
              (error e))))
        (clython.runtime:py-runtime-error (e)
          (unless (string= (clython.runtime:py-runtime-error-class-name e)
                           "StopIteration")
            (error e)))))
    ;; else clause (runs if no break)
    (unless broke
      (dolist (stmt (%sort-body (clython.ast:for-node-orelse node)))
        (eval-node stmt env)))
    clython.runtime:+py-none+))

;;; ─── Generator helpers ─────────────────────────────────────────────────────

(defun %ast-contains-yield-p (nodes)
  "Check if a list of AST nodes (function body) contains any yield or yield-from.
   Does NOT recurse into nested function/class definitions."
  (labels ((check (node)
             (cond
               ((null node) nil)
               ((typep node 'clython.ast:yield-node) t)
               ((typep node 'clython.ast:yield-from-node) t)
               ;; Don't recurse into nested functions or classes
               ((typep node 'clython.ast:function-def-node) nil)
               ((typep node 'clython.ast:class-def-node) nil)
               ((typep node 'clython.ast:lambda-node) nil)
               ;; Recurse into compound statements
               ((typep node 'clython.ast:if-node)
                (or (some #'check (clython.ast:if-node-body node))
                    (some #'check (clython.ast:if-node-orelse node))))
               ((typep node 'clython.ast:while-node)
                (or (some #'check (clython.ast:while-node-body node))
                    (some #'check (clython.ast:while-node-orelse node))))
               ((typep node 'clython.ast:for-node)
                (or (some #'check (clython.ast:for-node-body node))
                    (some #'check (clython.ast:for-node-orelse node))))
               ((typep node 'clython.ast:try-node)
                (or (some #'check (clython.ast:try-node-body node))
                    (some (lambda (h)
                            (some #'check (clython.ast:exception-handler-body h)))
                          (clython.ast:try-node-handlers node))
                    (some #'check (clython.ast:try-node-orelse node))
                    (some #'check (clython.ast:try-node-finalbody node))))
               ((typep node 'clython.ast:with-node)
                (some #'check (clython.ast:with-node-body node)))
               ((typep node 'clython.ast:expr-stmt-node)
                (check (clython.ast:expr-stmt-node-value node)))
               ((typep node 'clython.ast:assign-node)
                (check (clython.ast:assign-node-value node)))
               ((typep node 'clython.ast:aug-assign-node)
                (check (clython.ast:aug-assign-node-value node)))
               ((typep node 'clython.ast:return-node)
                (and (clython.ast:return-node-value node)
                     (check (clython.ast:return-node-value node))))
               (t nil))))
    (some #'check nodes)))

;;; ─── Function definition ──────────────────────────────────────────────────

(defun %extract-docstring (body)
  "If the first statement in BODY is a string constant (expr-stmt of a constant-node), return its value (unquoted)."
  (when body
    (let ((first-stmt (first body)))
      (when (typep first-stmt 'clython.ast:expr-stmt-node)
        (let ((val (clython.ast:expr-stmt-node-value first-stmt)))
          (when (and (typep val 'clython.ast:constant-node)
                     (stringp (clython.ast:constant-node-value val)))
            (%unquote-string (clython.ast:constant-node-value val))))))))

(defmethod eval-node ((node clython.ast:function-def-node) env)
  (let* ((name (clython.ast:function-def-node-name node))
         (params (clython.ast:function-def-node-args node))
         (body (%sort-body (clython.ast:function-def-node-body node)))
         (docstring (%extract-docstring body))
         ;; Evaluate default values now (at definition time)
         (evaled-params (%eval-defaults params env))
         (is-generator (%ast-contains-yield-p body))
         (func (clython.runtime:make-py-function
                :name name
                :params evaled-params
                :body body
                :env env
                :generator is-generator
                :docstring docstring
                :cl-fn (lambda (&rest args)
                         ;; This closure makes py-call work for user-defined functions
                         ;; (needed for decorators, first-class function passing via py-call)
                         (%call-user-function-from-cl-fn
                          evaled-params body env args is-generator)))))
    ;; Apply decorators (in reverse order)
    (let ((decorated func))
      (dolist (dec-node (reverse (clython.ast:function-def-node-decorator-list node)))
        (let ((dec-fn (eval-node dec-node env)))
          (setf decorated (clython.runtime:py-call dec-fn decorated))))
      (clython.scope:env-set name decorated env)))
  clython.runtime:+py-none+)

(defun %eval-defaults (params env)
  "Evaluate default argument values and return a new py-arguments with evaluated defaults."
  (when (null params) (return-from %eval-defaults nil))
  (let ((defaults (clython.ast:arguments-defaults params))
        (kw-defaults (clython.ast:arguments-kw-defaults params)))
    (make-instance 'clython.ast:py-arguments
                   :posonlyargs (clython.ast:arguments-posonlyargs params)
                   :args (clython.ast:arguments-args params)
                   :vararg (clython.ast:arguments-vararg params)
                   :kwonlyargs (clython.ast:arguments-kwonlyargs params)
                   :kw-defaults (mapcar (lambda (d) (when d (eval-node d env))) kw-defaults)
                   :kwarg (clython.ast:arguments-kwarg params)
                   :defaults (mapcar (lambda (d) (eval-node d env)) defaults))))

;;; ─── Async function definition ──────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:async-function-def-node) env)
  (let* ((name (clython.ast:async-function-def-node-name node))
         (params (clython.ast:async-function-def-node-args node))
         (body (%sort-body (clython.ast:async-function-def-node-body node)))
         (evaled-params (%eval-defaults params env))
         (func (clython.runtime:make-py-function
                :name name
                :params evaled-params
                :body body
                :env env
                :async-p t
                :cl-fn (lambda (&rest args)
                         (%call-user-function-from-cl-fn
                          evaled-params body env args nil t)))))
    ;; Apply decorators (in reverse order)
    (let ((decorated func))
      (dolist (dec-node (reverse (clython.ast:async-function-def-node-decorator-list node)))
        (let ((dec-fn (eval-node dec-node env)))
          (setf decorated (clython.runtime:py-call dec-fn decorated))))
      (clython.scope:env-set name decorated env)))
  clython.runtime:+py-none+)

;;; ─── Await expression ──────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:await-node) env)
  (let ((awaitable (eval-node (clython.ast:await-node-value node) env)))
    (cond
      ;; Awaiting a coroutine — run it to completion
      ((typep awaitable 'clython.runtime:py-coroutine)
       (clython.runtime:py-coroutine-run awaitable))
      ;; Awaiting something with __await__ — call it and exhaust the iterator
      ;; For simplicity, treat non-coroutine awaitables as already-resolved values
      (t awaitable))))

;;; ─── Async for ─────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:async-for-node) env)
  ;; In our synchronous interpreter, async for behaves like regular for.
  ;; Call __aiter__ / __anext__ and await any coroutines returned.
  (let* ((iter-val (eval-node (clython.ast:async-for-node-iter node) env))
         (target-node (clython.ast:async-for-node-target node))
         (body (clython.ast:async-for-node-body node))
         (orelse (clython.ast:async-for-node-orelse node))
         ;; Call __aiter__ via py-getattr (handles class hierarchy + bound method)
         (aiter-method (handler-case (clython.runtime:py-getattr iter-val "__aiter__")
                         (error () nil)))
         (iterator (if aiter-method
                       (let ((result (clython.runtime:py-call aiter-method)))
                         (if (typep result 'clython.runtime:py-coroutine)
                             (clython.runtime:py-coroutine-run result)
                             result))
                       (clython.runtime:py-iter iter-val)))
         (broke nil))
    (block for-loop
      (loop
        (let ((anext-method (handler-case (clython.runtime:py-getattr iterator "__anext__")
                              (error () nil))))
          (unless anext-method (return-from for-loop))
          (let ((next-val
                  (handler-case
                      ;; Call __anext__, await if it returns a coroutine
                      (let ((result (clython.runtime:py-call anext-method)))
                        (if (typep result 'clython.runtime:py-coroutine)
                            (clython.runtime:py-coroutine-run result)
                            result))
                    ;; StopIteration / StopAsyncIteration ends the loop
                    (clython.runtime:stop-iteration () (return-from for-loop))
                    (clython.runtime:py-runtime-error (e)
                      (if (or (string= (clython.runtime:py-runtime-error-class-name e) "StopIteration")
                              (string= (clython.runtime:py-runtime-error-class-name e) "StopAsyncIteration"))
                          (return-from for-loop)
                          (error e)))
                    (py-exception (e)
                      (let ((v (py-exception-value e)))
                        (if (and (typep v 'clython.runtime:py-exception-object)
                                 (or (string= (clython.runtime:py-exception-class-name v) "StopIteration")
                                     (string= (clython.runtime:py-exception-class-name v) "StopAsyncIteration")))
                            (return-from for-loop)
                            (error e)))))))
            (%assign-target target-node next-val env)
            (handler-case
                (dolist (stmt body)
                  (eval-node stmt env))
              (py-break () (setf broke t) (return-from for-loop))
              (py-continue () nil))))))
    ;; else clause runs if loop completed without break
    (unless broke
      (dolist (stmt orelse)
        (eval-node stmt env)))
    clython.runtime:+py-none+))

;;; ─── With statement ────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:with-node) env)
  (let ((items (clython.ast:with-node-items node))
        (body  (clython.ast:with-node-body node)))
    (%eval-with-items items body env)))

(defun %eval-with-items (items body env)
  "Evaluate with items recursively (for multiple context managers in one with)."
  (if (null items)
      ;; All context managers entered — execute body
      (progn
        (dolist (stmt body)
          (eval-node stmt env))
        clython.runtime:+py-none+)
      (let* ((item (first items))
             (ctx-expr (clython.ast:with-item-context-expr item))
             (opt-var  (clython.ast:with-item-optional-vars item))
             (ctx-mgr  (eval-node ctx-expr env))
             ;; Call __enter__
             (enter-method (clython.runtime:py-getattr ctx-mgr "__enter__"))
             (enter-val    (clython.runtime:py-call enter-method)))
        ;; Bind the result if 'as' variable present
        (when opt-var
          (%assign-target opt-var enter-val env))
        ;; Execute body, then call __exit__
        (let ((exc-info nil)
              (result nil))
          (handler-case
              (setf result (%eval-with-items (rest items) body env))
            ;; Catch Python exceptions
            (py-exception (e)
              (setf exc-info e))
            (clython.runtime:py-runtime-error (e)
              (setf exc-info e))
            ;; Catch return signals — need to still call __exit__
            (py-return-value (ret)
              (setf exc-info ret)))
          ;; Call __exit__
          (let* ((exit-method (clython.runtime:py-getattr ctx-mgr "__exit__"))
                 (exit-result
                   (cond
                     ;; Python exception
                     ((typep exc-info 'py-exception)
                      (let ((exc-val (py-exception-value exc-info)))
                        (clython.runtime:py-call
                         exit-method
                         ;; exc_type: the type/class
                         (if (typep exc-val 'clython.runtime:py-exception-object)
                             (clython.runtime:make-py-type
                              :name (clython.runtime:py-exception-class-name exc-val))
                             clython.runtime:+py-none+)
                         ;; exc_val: the exception instance
                         (if (typep exc-val 'clython.runtime:py-exception-object)
                             exc-val
                             clython.runtime:+py-none+)
                         ;; exc_tb: traceback (not implemented)
                         clython.runtime:+py-none+)))
                     ;; Runtime error
                     ((typep exc-info 'clython.runtime:py-runtime-error)
                      (clython.runtime:py-call exit-method
                                               clython.runtime:+py-true+
                                               clython.runtime:+py-none+
                                               clython.runtime:+py-none+))
                     ;; Return signal or no exception
                     (t
                      (clython.runtime:py-call exit-method
                                               clython.runtime:+py-none+
                                               clython.runtime:+py-none+
                                               clython.runtime:+py-none+)))))
            ;; Handle exception suppression
            (cond
              ;; Return signal — re-signal after __exit__
              ((typep exc-info 'py-return-value)
               (signal exc-info))
              ;; Exception — suppress if __exit__ returned truthy
              ((and exc-info (clython.runtime:py-bool-val exit-result))
               ;; Exception suppressed
               nil)
              ;; Exception — not suppressed, re-raise
              (exc-info
               (error exc-info))
              ;; No exception
              (t result)))))))

;;; ─── Async with ────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:async-with-node) env)
  ;; In our synchronous interpreter, async with behaves like regular with.
  ;; __aenter__ and __aexit__ return coroutines which we await immediately.
  (let ((items (clython.ast:async-with-node-items node))
        (body (clython.ast:async-with-node-body node)))
    (%eval-async-with-items items body env)))

(defun %eval-async-with-items (items body env)
  "Evaluate async with items recursively (for nested context managers)."
  (if (null items)
      ;; All context managers entered, execute body
      (handler-case
          (progn
            (dolist (stmt body)
              (eval-node stmt env))
            clython.runtime:+py-none+)
        (py-return-value (ret)
          (signal ret)
          clython.runtime:+py-none+))
      (let* ((item (first items))
             (ctx-expr (clython.ast:with-item-context-expr item))
             (opt-var  (clython.ast:with-item-optional-vars item))
             (ctx-mgr (eval-node ctx-expr env))
             ;; Call __aenter__, await if coroutine (py-getattr returns bound method)
             (enter-method (clython.runtime:py-getattr ctx-mgr "__aenter__"))
             (enter-result (clython.runtime:py-call enter-method))
             (enter-val (if (typep enter-result 'clython.runtime:py-coroutine)
                            (clython.runtime:py-coroutine-run enter-result)
                            enter-result)))
        ;; Bind the result if 'as' variable present
        (when opt-var
          (%assign-target opt-var enter-val env))
        ;; Execute remaining items + body, then call __aexit__
        (let ((exc nil))
          (handler-case
              (%eval-async-with-items (rest items) body env)
            (error (e) (setf exc e)))
          ;; Call __aexit__ (py-getattr returns bound method, so pass exc args only)
          (let* ((exit-method (clython.runtime:py-getattr ctx-mgr "__aexit__"))
                 (exit-result (clython.runtime:py-call exit-method
                                                       clython.runtime:+py-none+
                                                       clython.runtime:+py-none+
                                                       clython.runtime:+py-none+))
                 (exit-val (if (typep exit-result 'clython.runtime:py-coroutine)
                               (clython.runtime:py-coroutine-run exit-result)
                               exit-result)))
            (when (and exc (not (clython.runtime:py-bool-val exit-val)))
              (error exc))))
        clython.runtime:+py-none+)))

(defun %maybe-register-exception-class (name bases)
  "If any base class is in the exception hierarchy, register NAME as an exception subclass."
  (dolist (base bases)
    (let ((base-name (cond
                       ((typep base 'clython.runtime:py-type)
                        (clython.runtime:py-type-name base))
                       ((typep base 'clython.runtime:py-function)
                        (clython.runtime:py-function-name base))
                       (t nil))))
      (when (and base-name (gethash base-name clython.runtime:*exception-hierarchy*))
        ;; Build MRO: self + base's MRO
        (let ((base-mro (gethash base-name clython.runtime:*exception-hierarchy*)))
          (setf (gethash name clython.runtime:*exception-hierarchy*)
                (cons name base-mro)))
        (return)))))

;;; ─── Class definition ──────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:class-def-node) env)
  (let* ((name (clython.ast:class-def-node-name node))
         (explicit-bases (mapcar (lambda (b) (eval-node b env))
                                (clython.ast:class-def-node-bases node)))
         ;; If no explicit bases, implicitly inherit from object
         (bases (if explicit-bases explicit-bases
                    (let ((obj-type (clython.scope:env-get "object" env)))
                      (if obj-type (list obj-type) nil))))
         (class-env (clython.scope:env-extend env))
         (class-dict (make-hash-table :test #'equal)))
    ;; Execute class body in class scope
    (let ((sorted-body (%sort-body (clython.ast:class-def-node-body node))))
      ;; Extract docstring
      (let ((docstring (%extract-docstring sorted-body)))
        (when docstring
          (setf (gethash "__doc__" class-dict) (clython.runtime:make-py-str docstring))))
      (dolist (stmt sorted-body)
        (eval-node stmt class-env)))
    ;; Copy bindings from class scope into class dict
    (maphash (lambda (k v) (setf (gethash k class-dict) v))
             (clython.scope:env-bindings class-env))
    ;; Create the type object
    (let ((cls (clython.runtime:make-py-type :name name :bases bases :tdict class-dict)))
      ;; Inject __class__ into each method's closure for super() support
      (maphash (lambda (k v)
                 (declare (ignore k))
                 (when (typep v 'clython.runtime:py-function)
                   (let ((fn-env (clython.runtime:py-function-env v)))
                     (when fn-env
                       (clython.scope:env-set "__class__" cls fn-env)))))
               class-dict)
      ;; Register in exception hierarchy if any base is an exception class
      (%maybe-register-exception-class name bases)
      ;; Apply decorators (in reverse order)
      (let ((decorated cls))
        (dolist (dec-node (reverse (clython.ast:class-def-node-decorator-list node)))
          (let ((dec-fn (eval-node dec-node env)))
            (setf decorated (clython.runtime:py-call dec-fn decorated))))
        (clython.scope:env-set name decorated env)))
    clython.runtime:+py-none+))

;;; ─── Pass / Break / Continue ────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:pass-node) env)
  (declare (ignore env))
  clython.runtime:+py-none+)

(defmethod eval-node ((node clython.ast:break-node) env)
  (declare (ignore env))
  (signal 'py-break)
  clython.runtime:+py-none+)

(defmethod eval-node ((node clython.ast:continue-node) env)
  (declare (ignore env))
  (signal 'py-continue)
  clython.runtime:+py-none+)

;;; ─── Raise ──────────────────────────────────────────────────────────────────

(defun %is-exception-class-p (obj)
  "Check if OBJ is a py-type or py-function that represents an exception class."
  (cond
    ((typep obj 'clython.runtime:py-type)
     (let ((name (clython.runtime:py-type-name obj)))
       (gethash name clython.runtime:*exception-hierarchy*)))
    ((typep obj 'clython.runtime:py-function)
     (let ((name (clython.runtime:py-function-name obj)))
       (gethash name clython.runtime:*exception-hierarchy*)))
    (t nil)))

(defun %py-object-to-exception (obj)
  "Convert a py-object whose class is in the exception hierarchy to a py-exception-object."
  (let* ((cls (clython.runtime:py-object-class obj))
         (class-name (when (typep cls 'clython.runtime:py-type)
                       (clython.runtime:py-type-name cls))))
    (if (and class-name (gethash class-name clython.runtime:*exception-hierarchy*))
        ;; Build a py-exception-object with the user object's attributes
        (let ((exc-obj (clython.runtime:make-py-exception-object class-name)))
          ;; Copy instance dict for attribute access
          (let ((src-dict (clython.runtime:py-object-dict obj))
                (dst-dict (clython.runtime:py-object-dict exc-obj)))
            (when (and src-dict dst-dict)
              (maphash (lambda (k v) (setf (gethash k dst-dict) v))
                       src-dict)))
          exc-obj)
        obj)))

(defmethod eval-node ((node clython.ast:raise-node) env)
  (if (clython.ast:raise-node-exc node)
      (let ((exc (eval-node (clython.ast:raise-node-exc node) env)))
        ;; If exc is a py-type/py-function (exception class), call it with no args
        (when (and (or (typep exc 'clython.runtime:py-function)
                       (typep exc 'clython.runtime:py-type))
                   (not (typep exc 'clython.runtime:py-exception-object)))
          (setf exc (clython.runtime:py-call exc)))
        ;; If exc is a py-object from a user-defined exception class, convert it
        (when (and (typep exc 'clython.runtime:py-object)
                   (not (typep exc 'clython.runtime:py-exception-object)))
          (setf exc (%py-object-to-exception exc)))
        (error 'py-exception :value exc))
      ;; bare raise — re-raise current exception if available
      (let ((current *current-exception*))
        (if current
            (error current)
            (error 'py-exception
                   :value (clython.runtime:make-py-exception-object "RuntimeError"))))))

;;; ─── Try / Except ──────────────────────────────────────────────────────────

(defun %exception-matches-single-type-p (exc-value handler-type)
  "Check if exc-value matches a single handler type (a py-function or py-type)."
  (let ((handler-name (cond
                        ((typep handler-type 'clython.runtime:py-function)
                         (clython.runtime:py-function-name handler-type))
                        ((typep handler-type 'clython.runtime:py-type)
                         (clython.runtime:py-type-name handler-type))
                        (t nil))))
    (when handler-name
      (cond
        ;; exc-value is a py-exception-object — check hierarchy
        ((typep exc-value 'clython.runtime:py-exception-object)
         (clython.runtime:exception-is-subclass-p
          (clython.runtime:py-exception-class-name exc-value)
          handler-name))
        ;; exc-value is a string (legacy) — check if handler name appears
        ((typep exc-value 'clython.runtime:py-str)
         (search handler-name (clython.runtime:py-str-value exc-value)))
        ;; fallback
        (t nil)))))

(defun %exception-matches-handler-p (exc-value handler-type-node env)
  "Check if an exception value matches the type in a handler's except clause.
   HANDLER-TYPE-NODE is the AST node for the exception type (or NIL for bare except).
   Supports both single types and tuples of types: except (TypeError, ValueError)."
  (when (null handler-type-node)
    (return-from %exception-matches-handler-p t))
  (let ((handler-type (eval-node handler-type-node env)))
    (cond
      ;; Tuple of exception types — match any
      ((typep handler-type 'clython.runtime:py-tuple)
       (some (lambda (etype)
               (%exception-matches-single-type-p exc-value etype))
             (coerce (clython.runtime:py-tuple-value handler-type) 'list)))
      ;; Single exception type
      (t (%exception-matches-single-type-p exc-value handler-type)))))

(defun %handle-exception (exc-val handlers node env)
  "Try to match exc-val against handlers. Returns T if handled, NIL otherwise.
   Signals the original error if not handled."
  (let ((handled nil))
    (dolist (handler handlers)
      (unless handled
        ;; Check if the handler type matches the raised exception
        (when (%exception-matches-handler-p
               exc-val
               (clython.ast:exception-handler-type handler)
               env)
          ;; Bind the exception to the handler's variable name (if any)
          (when (clython.ast:exception-handler-name handler)
            (clython.scope:env-set (clython.ast:exception-handler-name handler)
                                   exc-val env))
          (dolist (stmt (%sort-body (clython.ast:exception-handler-body handler)))
            (eval-node stmt env))
          (setf handled t))))
    handled))

(defmethod eval-node ((node clython.ast:try-node) env)
  (let ((has-finally (clython.ast:try-node-finalbody node)))
    (flet ((%try-body ()
             (let ((caught nil))
               (handler-case
                   (progn
                     (dolist (stmt (%sort-body (clython.ast:try-node-body node)))
                       (eval-node stmt env)))
                 (py-exception (e)
                   (setf caught t)
                   (let* ((*current-exception* e)
                          (exc-val (py-exception-value e)))
                     (unless (%handle-exception exc-val (clython.ast:try-node-handlers node) node env)
                       (error e))))
                 (clython.runtime:py-runtime-error (e)
                   (setf caught t)
                   (let* ((exc-val (clython.runtime:make-py-exception-object
                                    (clython.runtime:py-runtime-error-class-name e)
                                    (list (clython.runtime:make-py-str
                                           (clython.runtime:py-runtime-error-message e)))))
                          (wrapper (make-condition 'py-exception :value exc-val))
                          (*current-exception* wrapper))
                     (unless (%handle-exception exc-val (clython.ast:try-node-handlers node) node env)
                       (error e)))))
               ;; else clause (runs if no exception was raised)
               (unless caught
                 (dolist (stmt (%sort-body (clython.ast:try-node-orelse node)))
                   (eval-node stmt env)))
               clython.runtime:+py-none+)))
      (if has-finally
          (unwind-protect
              (%try-body)
            (dolist (stmt (%sort-body (clython.ast:try-node-finalbody node)))
              (eval-node stmt env)))
          (%try-body)))))

;;; ─── Import ─────────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:import-node) env)
  (dolist (alias (clython.ast:import-node-names node))
    (let* ((name (clython.ast:alias-name alias))
           (asname (or (clython.ast:alias-asname alias) name))
           (mod (clython.imports:import-module name)))
      ;; For dotted imports without 'as', bind only the top-level name
      ;; e.g. 'import os.path' binds 'os', not 'os.path'
      (if (and (not (clython.ast:alias-asname alias))
               (position #\. name))
          (let ((top-name (subseq name 0 (position #\. name))))
            (clython.scope:env-set top-name
                                   (clython.imports:import-module top-name)
                                   env))
          (clython.scope:env-set asname mod env))))
  clython.runtime:+py-none+)

(defmethod eval-node ((node clython.ast:import-from-node) env)
  (let* ((module-name (clython.ast:import-from-node-module node))
         (mod (clython.imports:import-module module-name)))
    (dolist (alias (clython.ast:import-from-node-names node))
      (let* ((name (clython.ast:alias-name alias))
             (asname (or (clython.ast:alias-asname alias) name)))
        (if (string= name "*")
            ;; from X import * — copy all non-underscore-prefixed names
            (maphash (lambda (k v)
                       (unless (and (> (length k) 0)
                                    (char= (char k 0) #\_))
                         (clython.scope:env-set k v env)))
                     (clython.runtime:py-module-dict mod))
            ;; from X import Y / from X import Y as Z
            (multiple-value-bind (val found)
                (gethash name (clython.runtime:py-module-dict mod))
              ;; If not found in dict, try importing as a submodule
              (unless found
                (let ((submod-name (format nil "~A.~A" module-name name)))
                  (handler-case
                      (progn
                        (setf val (clython.imports:import-module submod-name))
                        (setf found t))
                    (error () nil))))
              (unless found
                (clython.runtime:py-raise "ImportError" "cannot import name '~A' from '~A'" name module-name))
              (clython.scope:env-set asname val env))))))
  clython.runtime:+py-none+)

;;; ─── Global / Nonlocal ─────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:global-node) env)
  (dolist (name (clython.ast:global-node-names node))
    (clython.scope:env-declare-global name env))
  clython.runtime:+py-none+)

(defmethod eval-node ((node clython.ast:nonlocal-node) env)
  (dolist (name (clython.ast:nonlocal-node-names node))
    (clython.scope:env-declare-nonlocal name env))
  clython.runtime:+py-none+)

;;; ─── Delete ─────────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:delete-node) env)
  (dolist (target (clython.ast:delete-node-targets node))
    (cond
      ((typep target 'clython.ast:name-node)
       (clython.scope:env-del (clython.ast:name-node-id target) env))
      ((typep target 'clython.ast:subscript-node)
       (let ((obj (eval-node (clython.ast:subscript-node-value target) env))
             (key (eval-node (clython.ast:subscript-node-slice target) env)))
         (clython.runtime:py-delitem obj key)))
      ((typep target 'clython.ast:attribute-node)
       (let ((obj (eval-node (clython.ast:attribute-node-value target) env))
             (attr (clython.ast:attribute-node-attr target)))
         (clython.runtime:py-delattr obj attr)))))
  clython.runtime:+py-none+)

;;; ─── Assert ─────────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:assert-node) env)
  (unless (clython.runtime:py-bool-val (eval-node (clython.ast:assert-node-test node) env))
    (let* ((msg-str (if (clython.ast:assert-node-msg node)
                        (clython.runtime:py-str-of
                         (eval-node (clython.ast:assert-node-msg node) env))
                        ""))
           (args (unless (string= msg-str "")
                   (list (clython.runtime:make-py-str msg-str)))))
      (error 'py-exception
             :value (clython.runtime:make-py-exception-object "AssertionError" args))))
  clython.runtime:+py-none+)

;;; ─── F-strings ─────────────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:joined-str-node) env)
  (let ((parts (mapcar (lambda (v) (eval-node v env))
                       (clython.ast:joined-str-node-values node))))
    (clython.runtime:make-py-str
     (apply #'concatenate 'string
            (mapcar #'clython.runtime:py-str-of parts)))))

(defmethod eval-node ((node clython.ast:formatted-value-node) env)
  (let* ((val (eval-node (clython.ast:formatted-value-node-value node) env))
         (conv (clython.ast:formatted-value-node-conversion node))
         (fmt-spec-node (clython.ast:formatted-value-node-format-spec node))
         (converted
           (cond
             ((eql conv 115) (clython.runtime:py-str-of val))   ; !s
             ((eql conv 114) (clython.runtime:py-repr val))     ; !r
             ((eql conv 97)  (clython.runtime:py-repr val))     ; !a
             (t nil)))
         (fmt-spec
           (when fmt-spec-node
             (clython.runtime:py-str-value (eval-node fmt-spec-node env)))))
    (if (and fmt-spec (plusp (length fmt-spec)))
        (clython.runtime:make-py-str (apply-python-format-spec val fmt-spec converted))
        (clython.runtime:make-py-str (or converted (clython.runtime:py-str-of val))))))

(defun apply-python-format-spec (val spec &optional converted-str)
  "Apply a Python format spec string to a value, returning a formatted string."
  (let* ((len (length spec))
         (pos 0)
         (fill-char #\Space)
         (align nil)
         (zero-pad nil)
         (width nil)
         (precision nil)
         (type-char nil))
    ;; Parse fill+align or just align
    (when (and (>= len 2)
               (member (char spec 1) '(#\< #\> #\^ #\=)))
      (setf fill-char (char spec 0)
            align (char spec 1)
            pos 2))
    (when (and (null align) (plusp len)
               (member (char spec 0) '(#\< #\> #\^ #\=)))
      (setf align (char spec 0)
            pos 1))
    ;; Sign
    (when (and (< pos len) (member (char spec pos) '(#\+ #\- #\Space)))
      (incf pos))
    ;; Zero padding
    (when (and (< pos len) (char= (char spec pos) #\0))
      (setf zero-pad t)
      (when (null align) (setf align #\=))
      (when (char= fill-char #\Space) (setf fill-char #\0))
      (incf pos))
    ;; Width
    (let ((start pos))
      (loop while (and (< pos len) (digit-char-p (char spec pos))) do (incf pos))
      (when (> pos start)
        (setf width (parse-integer (subseq spec start pos)))))
    ;; Precision
    (when (and (< pos len) (char= (char spec pos) #\.))
      (incf pos)
      (let ((start pos))
        (loop while (and (< pos len) (digit-char-p (char spec pos))) do (incf pos))
        (when (> pos start)
          (setf precision (parse-integer (subseq spec start pos))))))
    ;; Type character
    (when (< pos len)
      (setf type-char (char spec pos)))
    ;; Format the value
    (let* ((num-val (typecase val
                      (clython.runtime:py-int (clython.runtime:py-int-value val))
                      (clython.runtime:py-float (clython.runtime:py-float-value val))
                      (t nil)))
           (raw
             (cond
               ((and converted-str (null type-char)) converted-str)
               ((and type-char (char= type-char #\d))
                (format nil "~D" (if num-val (truncate num-val) 0)))
               ((and type-char (char= type-char #\x))
                (format nil "~(~X~)" (if num-val (truncate num-val) 0)))
               ((and type-char (char= type-char #\X))
                (format nil "~X" (if num-val (truncate num-val) 0)))
               ((and type-char (char= type-char #\o))
                (format nil "~O" (if num-val (truncate num-val) 0)))
               ((and type-char (char= type-char #\b))
                (format nil "~B" (if num-val (truncate num-val) 0)))
               ((and type-char (char= type-char #\f))
                (let ((p (or precision 6))
                      (n (if num-val (float num-val 1.0d0) 0.0d0)))
                  (format nil "~,vF" p n)))
               ((and type-char (char= type-char #\e))
                (let ((p (or precision 6))
                      (n (if num-val (float num-val 1.0d0) 0.0d0)))
                  (format nil "~,vE" p n)))
               ((and type-char (char= type-char #\s))
                (let ((s (or converted-str (clython.runtime:py-str-of val))))
                  (if precision (subseq s 0 (min precision (length s))) s)))
               (t
                (cond
                  ((and precision num-val)
                   (format nil "~,vF" precision (float num-val 1.0d0)))
                  (converted-str converted-str)
                  (t (clython.runtime:py-str-of val)))))))
      ;; Apply width/alignment
      (if (and width (> width (length raw)))
          (let ((pad-amount (- width (length raw)))
                (effective-align (or align (if num-val #\> #\<))))
            (cond
              ((char= effective-align #\<)
               (concatenate 'string raw (make-string pad-amount :initial-element fill-char)))
              ((char= effective-align #\>)
               (concatenate 'string (make-string pad-amount :initial-element fill-char) raw))
              ((char= effective-align #\^)
               (let ((left (floor pad-amount 2))
                     (right (ceiling pad-amount 2)))
                 (concatenate 'string
                              (make-string left :initial-element fill-char)
                              raw
                              (make-string right :initial-element fill-char))))
              ((char= effective-align #\=)
               (if (and (plusp (length raw))
                        (member (char raw 0) '(#\+ #\- #\Space)))
                   (concatenate 'string
                                (string (char raw 0))
                                (make-string pad-amount :initial-element fill-char)
                                (subseq raw 1))
                   (concatenate 'string (make-string pad-amount :initial-element fill-char) raw)))
              (t raw)))
          raw))))

;;; ─── Type alias (stub) ─────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:type-alias-node) env)
  (declare (ignore env))
  clython.runtime:+py-none+)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Match statement (PEP 634)
;;;; ─────────────────────────────────────────────────────────────────────────

(defun %match-pattern (subject pattern env)
  "Try to match SUBJECT (a py-object) against PATTERN (an AST pattern node).
   Returns T if matched, NIL otherwise. On match, binds captured names in ENV."
  (typecase pattern
    ;; Wildcard or capture: match-as-node with pattern=NIL
    (clython.ast:match-as-node
     (let ((inner (clython.ast:match-as-node-pattern pattern))
           (name  (clython.ast:match-as-node-name pattern)))
       (cond
         ;; Wildcard: pattern=NIL, name=NIL  -> always matches, no binding
         ((and (null inner) (null name)) t)
         ;; Capture: pattern=NIL, name set   -> always matches, bind name
         ((null inner)
          (clython.scope:env-set name subject env)
          t)
         ;; As-pattern: pattern + name -> match inner, then bind
         (t (when (%match-pattern subject inner env)
              (when name (clython.scope:env-set name subject env))
              t)))))

    ;; Literal value comparison
    (clython.ast:match-value-node
     (let ((val (eval-node (clython.ast:match-value-node-value pattern) env)))
       (clython.runtime:py-eq subject val)))

    ;; Singleton: True, False, None
    (clython.ast:match-singleton-node
     (let ((sv (clython.ast:match-singleton-node-value pattern)))
       (cond
         ((eq sv t)    (eq subject clython.runtime:+py-true+))
         ((eq sv nil)  (eq subject clython.runtime:+py-false+))
         ((eq sv :none) (eq subject clython.runtime:+py-none+))
         (t nil))))

    ;; Sequence pattern: (x, y) or [a, b, c]
    (clython.ast:match-sequence-node
     (let ((sub-patterns (clython.ast:match-sequence-node-patterns pattern)))
       ;; Subject must be a tuple or list
       (let ((elems nil))
         (cond
           ((typep subject 'clython.runtime:py-tuple)
            (setf elems (coerce (clython.runtime:py-tuple-value subject) 'list)))
           ((typep subject 'clython.runtime:py-list)
            (setf elems (coerce (clython.runtime:py-list-value subject) 'list)))
           (t (return-from %match-pattern nil)))
         ;; Check for star patterns
         (let ((star-idx nil))
           (loop for i from 0 below (length sub-patterns)
                 when (typep (nth i sub-patterns) 'clython.ast:match-star-node)
                   do (setf star-idx i) (return))
           (if star-idx
               ;; Star pattern present
               (let* ((before-count star-idx)
                      (after-count (- (length sub-patterns) star-idx 1)))
                 (unless (>= (length elems) (+ before-count after-count))
                   (return-from %match-pattern nil))
                 ;; Match before star
                 (loop for i below before-count
                       unless (%match-pattern (nth i elems) (nth i sub-patterns) env)
                         do (return-from %match-pattern nil))
                 ;; Bind star
                 (let* ((star-pat (nth star-idx sub-patterns))
                        (star-name (clython.ast:match-star-node-name star-pat))
                        (star-elems (subseq elems before-count
                                            (- (length elems) after-count))))
                   (when star-name
                     (clython.scope:env-set star-name
                                            (clython.runtime:make-py-list star-elems)
                                            env)))
                 ;; Match after star
                 (loop for i from 1 to after-count
                       for pat = (nth (+ star-idx i) sub-patterns)
                       for elem = (nth (- (length elems) after-count (- i)) elems)
                       unless (%match-pattern elem pat env)
                         do (return-from %match-pattern nil))
                 t)
               ;; No star — exact length match
               (and (= (length elems) (length sub-patterns))
                    (loop for elem in elems
                          for pat in sub-patterns
                          always (%match-pattern elem pat env))))))))

    ;; OR pattern: 1 | 2 | 3
    (clython.ast:match-or-node
     (loop for alt in (clython.ast:match-or-node-patterns pattern)
           thereis (%match-pattern subject alt env)))

    ;; Star pattern (handled inside sequence, but just in case)
    (clython.ast:match-star-node
     ;; Should not be reached outside of sequence context
     nil)

    ;; Mapping pattern: {"key": value}
    (clython.ast:match-mapping-node
     ;; Subject must be a dict
     (when (typep subject 'clython.runtime:py-dict)
       (let ((keys (clython.ast:match-mapping-node-keys pattern))
             (pats (clython.ast:match-mapping-node-patterns pattern))
             (ht   (clython.runtime:py-dict-value subject)))
         (loop for key-node in keys
               for pat in pats
               for key-val = (eval-node key-node env)
               always (multiple-value-bind (val found)
                          (gethash (clython.runtime::dict-hash-key key-val) ht)
                        (and found (%match-pattern val pat env)))))))

    ;; Class pattern (not yet fully supported)
    (clython.ast:match-class-node nil)

    (t nil)))

(defmethod eval-node ((node clython.ast:match-node) env)
  (let ((subject (eval-node (clython.ast:match-node-subject node) env)))
    (dolist (case-obj (clython.ast:match-node-cases node) clython.runtime:+py-none+)
      (let ((pattern (clython.ast:match-case-pattern case-obj))
            (guard   (clython.ast:match-case-guard case-obj))
            (body    (clython.ast:match-case-body case-obj)))
        ;; Try matching — use a fresh scope so failed matches don't leak bindings
        (let ((matched nil))
          ;; We need to test if pattern matches first, then check guard
          (when (%match-pattern subject pattern env)
            (if guard
                (when (clython.runtime:py-bool-val (eval-node guard env))
                  (setf matched t))
                (setf matched t)))
          (when matched
            (let ((result clython.runtime:+py-none+))
              (dolist (stmt body)
                (setf result (eval-node stmt env)))
              (return result))))))))

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Wire up import system callback
;;;; ─────────────────────────────────────────────────────────────────────────

(setf clython.imports:*eval-source-fn*
      (lambda (source env)
        (let* ((tokens (clython.lexer:tokenize source))
               (ast (clython.parser:parse-module tokens)))
          (eval-node ast env))))
