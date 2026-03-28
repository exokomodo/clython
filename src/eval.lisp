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
      ((eq val :ellipsis) clython.runtime:+py-none+)  ; stub
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

(defmethod eval-node ((node clython.ast:list-node) env)
  (let ((items (mapcar (lambda (elt) (eval-node elt env))
                       (clython.ast:list-node-elts node))))
    (clython.runtime:make-py-list items)))

(defmethod eval-node ((node clython.ast:tuple-node) env)
  (let ((items (mapcar (lambda (elt) (eval-node elt env))
                       (clython.ast:tuple-node-elts node))))
    (clython.runtime:make-py-tuple items)))

(defmethod eval-node ((node clython.ast:dict-node) env)
  (let ((d (clython.runtime:make-py-dict)))
    (loop for k-node in (clython.ast:dict-node-keys node)
          for v-node in (clython.ast:dict-node-values node)
          do (let ((k (eval-node k-node env))
                   (v (eval-node v-node env)))
               (clython.runtime:py-setitem d k v)))
    d))

(defmethod eval-node ((node clython.ast:set-node) env)
  (let ((items (mapcar (lambda (elt) (eval-node elt env))
                       (clython.ast:set-node-elts node))))
    (clython.runtime:make-py-set items)))

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
  (let* ((func (eval-node (clython.ast:call-node-func node) env))
         (args (mapcar (lambda (a) (eval-node a env))
                       (clython.ast:call-node-args node)))
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

(defun %call-user-function (func args &optional kwargs)
  "Call a user-defined py-function with the given evaluated arguments."
  (let* ((closure-env (clython.runtime:py-function-env func))
         (call-env (clython.scope:env-extend closure-env))
         (params (clython.runtime:py-function-params func))
         (body (clython.runtime:py-function-body func)))
    ;; Bind positional arguments and keyword arguments
    (%bind-params params args call-env kwargs)
    ;; Execute body, catching return
    (handler-case
        (progn
          (dolist (stmt body)
            (eval-node stmt call-env))
          clython.runtime:+py-none+)
      (py-return-value (ret)
        (py-return-value-val ret)))))

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

(defmethod eval-node ((node clython.ast:lambda-node) env)
  (let ((evaled-params (%eval-defaults (clython.ast:lambda-node-args node) env)))
    (clython.runtime:make-py-function
     :name "<lambda>"
     :params evaled-params
     :body (list (make-instance 'clython.ast:return-node
                                :value (clython.ast:lambda-node-body node)))
     :env env)))

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
  ;; Simplified: collect into a list and return an iterator over it
  (let ((comp-env (clython.scope:env-extend env))
        (results '()))
    (%eval-comprehension-generators
     (clython.ast:generator-exp-node-generators node)
     (lambda ()
       (push (eval-node (clython.ast:generator-exp-node-elt node) comp-env) results))
     comp-env)
    (let ((items (nreverse results))
          (idx 0))
      (clython.runtime:make-py-iterator
       (lambda ()
         (if (< idx (length items))
             (prog1 (nth idx items) (incf idx))
             (error 'clython.runtime:stop-iteration)))))))

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

(defmethod eval-node ((node clython.ast:aug-assign-node) env)
  (let* ((target (clython.ast:aug-assign-node-target node))
         (op (clython.ast:aug-assign-node-op node))
         (rhs (eval-node (clython.ast:aug-assign-node-value node) env))
         (current (eval-node target env))
         (new-val (%binop-dispatch op current rhs)))
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
        (clython.runtime:stop-iteration () nil)))
    ;; else clause (runs if no break)
    (unless broke
      (dolist (stmt (%sort-body (clython.ast:for-node-orelse node)))
        (eval-node stmt env)))
    clython.runtime:+py-none+))

;;; ─── Function definition ──────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:function-def-node) env)
  (let* ((name (clython.ast:function-def-node-name node))
         (params (clython.ast:function-def-node-args node))
         (body (%sort-body (clython.ast:function-def-node-body node)))
         ;; Evaluate default values now (at definition time)
         (evaled-params (%eval-defaults params env))
         (func (clython.runtime:make-py-function
                :name name
                :params evaled-params
                :body body
                :env env)))
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

;;; ─── Class definition ──────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:class-def-node) env)
  (let* ((name (clython.ast:class-def-node-name node))
         (bases (mapcar (lambda (b) (eval-node b env))
                        (clython.ast:class-def-node-bases node)))
         (class-env (clython.scope:env-extend env))
         (class-dict (make-hash-table :test #'equal)))
    ;; Execute class body in class scope
    (dolist (stmt (%sort-body (clython.ast:class-def-node-body node)))
      (eval-node stmt class-env))
    ;; Copy bindings from class scope into class dict
    (maphash (lambda (k v) (setf (gethash k class-dict) v))
             (clython.scope:env-bindings class-env))
    ;; Create the type object
    (let ((cls (clython.runtime:make-py-type :name name :bases bases :tdict class-dict)))
      (clython.scope:env-set name cls env))
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

(defmethod eval-node ((node clython.ast:raise-node) env)
  (if (clython.ast:raise-node-exc node)
      (let ((exc (eval-node (clython.ast:raise-node-exc node) env)))
        ;; If exc is a py-function (exception class), call it with no args
        (when (and (typep exc 'clython.runtime:py-function)
                   (not (typep exc 'clython.runtime:py-exception-object)))
          (setf exc (clython.runtime:py-call exc)))
        (error 'py-exception :value exc))
      ;; bare raise — re-raise current exception if available
      (let ((current *current-exception*))
        (if current
            (error current)
            (error 'py-exception
                   :value (clython.runtime:make-py-exception-object "RuntimeError"))))))

;;; ─── Try / Except ──────────────────────────────────────────────────────────

(defun %exception-matches-handler-p (exc-value handler-type-node env)
  "Check if an exception value matches the type in a handler's except clause.
   HANDLER-TYPE-NODE is the AST node for the exception type (or NIL for bare except)."
  (when (null handler-type-node)
    (return-from %exception-matches-handler-p t))
  (let ((handler-type (eval-node handler-type-node env)))
    ;; handler-type should be a py-function (exception constructor) with a name
    (when (typep handler-type 'clython.runtime:py-function)
      (let ((handler-name (clython.runtime:py-function-name handler-type)))
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
          (t nil))))))

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
        ;; Convert runtime error to a py-exception-object for uniform handling
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
    ;; finally clause (always runs)
    (dolist (stmt (%sort-body (clython.ast:try-node-finalbody node)))
      (eval-node stmt env)))
  clython.runtime:+py-none+)

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
  (let ((val (eval-node (clython.ast:formatted-value-node-value node) env)))
    ;; Simplified: just convert to string (ignoring conversion/format-spec)
    (clython.runtime:make-py-str (clython.runtime:py-str-of val))))

;;; ─── Type alias (stub) ─────────────────────────────────────────────────────

(defmethod eval-node ((node clython.ast:type-alias-node) env)
  (declare (ignore env))
  clython.runtime:+py-none+)

;;;; ─────────────────────────────────────────────────────────────────────────
;;;; Wire up import system callback
;;;; ─────────────────────────────────────────────────────────────────────────

(setf clython.imports:*eval-source-fn*
      (lambda (source env)
        (let* ((tokens (clython.lexer:tokenize source))
               (ast (clython.parser:parse-module tokens)))
          (eval-node ast env))))
