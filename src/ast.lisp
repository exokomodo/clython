;;;; ast.lisp — Python 3.12 AST node definitions for Clython
;;;;
;;;; All node classes correspond to the Python 3.12 abstract grammar:
;;;; https://docs.python.org/3.12/library/ast.html#abstract-grammar

(defpackage :clython.ast
  (:use :cl)
  (:export
   ;; Base
   #:py-ast-node
   #:node-line
   #:node-col
   #:node-end-line
   #:node-end-col

   ;; Modules
   #:module-node
   #:module-node-body
   #:module-node-type-ignores
   #:interactive-node
   #:interactive-node-body
   #:expression-node
   #:expression-node-body

   ;; Statements
   #:function-def-node
   #:function-def-node-name
   #:function-def-node-args
   #:function-def-node-body
   #:function-def-node-decorator-list
   #:function-def-node-returns
   #:function-def-node-type-comment
   #:function-def-node-type-params

   #:async-function-def-node
   #:async-function-def-node-name
   #:async-function-def-node-args
   #:async-function-def-node-body
   #:async-function-def-node-decorator-list
   #:async-function-def-node-returns
   #:async-function-def-node-type-comment
   #:async-function-def-node-type-params

   #:class-def-node
   #:class-def-node-name
   #:class-def-node-bases
   #:class-def-node-keywords
   #:class-def-node-body
   #:class-def-node-decorator-list
   #:class-def-node-type-params

   #:return-node
   #:return-node-value

   #:delete-node
   #:delete-node-targets

   #:assign-node
   #:assign-node-targets
   #:assign-node-value
   #:assign-node-type-comment

   #:aug-assign-node
   #:aug-assign-node-target
   #:aug-assign-node-op
   #:aug-assign-node-value

   #:ann-assign-node
   #:ann-assign-node-target
   #:ann-assign-node-annotation
   #:ann-assign-node-value
   #:ann-assign-node-simple

   #:for-node
   #:for-node-target
   #:for-node-iter
   #:for-node-body
   #:for-node-orelse
   #:for-node-type-comment

   #:async-for-node
   #:async-for-node-target
   #:async-for-node-iter
   #:async-for-node-body
   #:async-for-node-orelse
   #:async-for-node-type-comment

   #:while-node
   #:while-node-test
   #:while-node-body
   #:while-node-orelse

   #:if-node
   #:if-node-test
   #:if-node-body
   #:if-node-orelse

   #:with-node
   #:with-node-items
   #:with-node-body
   #:with-node-type-comment

   #:async-with-node
   #:async-with-node-items
   #:async-with-node-body
   #:async-with-node-type-comment

   #:match-node
   #:match-node-subject
   #:match-node-cases

   #:raise-node
   #:raise-node-exc
   #:raise-node-cause

   #:try-node
   #:try-node-body
   #:try-node-handlers
   #:try-node-orelse
   #:try-node-finalbody

   #:try-star-node
   #:try-star-node-body
   #:try-star-node-handlers
   #:try-star-node-orelse
   #:try-star-node-finalbody

   #:assert-node
   #:assert-node-test
   #:assert-node-msg

   #:import-node
   #:import-node-names

   #:import-from-node
   #:import-from-node-module
   #:import-from-node-names
   #:import-from-node-level

   #:global-node
   #:global-node-names

   #:nonlocal-node
   #:nonlocal-node-names

   #:expr-stmt-node
   #:expr-stmt-node-value

   #:pass-node
   #:break-node
   #:continue-node

   #:type-alias-node
   #:type-alias-node-name
   #:type-alias-node-type-params
   #:type-alias-node-value

   ;; Expressions
   #:bool-op-node
   #:bool-op-node-op
   #:bool-op-node-values

   #:named-expr-node
   #:named-expr-node-target
   #:named-expr-node-value

   #:bin-op-node
   #:bin-op-node-left
   #:bin-op-node-op
   #:bin-op-node-right

   #:unary-op-node
   #:unary-op-node-op
   #:unary-op-node-operand

   #:lambda-node
   #:lambda-node-args
   #:lambda-node-body

   #:if-exp-node
   #:if-exp-node-test
   #:if-exp-node-body
   #:if-exp-node-orelse

   #:dict-node
   #:dict-node-keys
   #:dict-node-values

   #:set-node
   #:set-node-elts

   #:list-comp-node
   #:list-comp-node-elt
   #:list-comp-node-generators

   #:set-comp-node
   #:set-comp-node-elt
   #:set-comp-node-generators

   #:dict-comp-node
   #:dict-comp-node-key
   #:dict-comp-node-value
   #:dict-comp-node-generators

   #:generator-exp-node
   #:generator-exp-node-elt
   #:generator-exp-node-generators

   #:await-node
   #:await-node-value

   #:yield-node
   #:yield-node-value

   #:yield-from-node
   #:yield-from-node-value

   #:compare-node
   #:compare-node-left
   #:compare-node-ops
   #:compare-node-comparators

   #:call-node
   #:call-node-func
   #:call-node-args
   #:call-node-keywords

   #:formatted-value-node
   #:formatted-value-node-value
   #:formatted-value-node-conversion
   #:formatted-value-node-format-spec

   #:joined-str-node
   #:joined-str-node-values

   #:constant-node
   #:constant-node-value
   #:constant-node-kind

   #:attribute-node
   #:attribute-node-value
   #:attribute-node-attr
   #:attribute-node-ctx

   #:subscript-node
   #:subscript-node-value
   #:subscript-node-slice
   #:subscript-node-ctx

   #:starred-node
   #:starred-node-value
   #:starred-node-ctx

   #:name-node
   #:name-node-id
   #:name-node-ctx

   #:list-node
   #:list-node-elts
   #:list-node-ctx

   #:tuple-node
   #:tuple-node-elts
   #:tuple-node-ctx

   #:slice-node
   #:slice-node-lower
   #:slice-node-upper
   #:slice-node-step

   ;; Auxiliary types
   #:py-comprehension
   #:comprehension-target
   #:comprehension-iter
   #:comprehension-ifs
   #:comprehension-is-async

   #:py-arguments
   #:arguments-posonlyargs
   #:arguments-args
   #:arguments-vararg
   #:arguments-kwonlyargs
   #:arguments-kw-defaults
   #:arguments-kwarg
   #:arguments-defaults

   #:py-arg
   #:arg-arg
   #:arg-annotation
   #:arg-type-comment

   #:py-keyword
   #:keyword-arg
   #:keyword-value

   #:py-alias
   #:alias-name
   #:alias-asname

   #:py-with-item
   #:with-item-context-expr
   #:with-item-optional-vars

   #:py-match-case
   #:match-case-pattern
   #:match-case-guard
   #:match-case-body

   #:py-exception-handler
   #:exception-handler-type
   #:exception-handler-name
   #:exception-handler-body

   ;; Pattern nodes (match statement)
   #:match-value-node
   #:match-value-node-value

   #:match-singleton-node
   #:match-singleton-node-value

   #:match-sequence-node
   #:match-sequence-node-patterns

   #:match-mapping-node
   #:match-mapping-node-keys
   #:match-mapping-node-patterns
   #:match-mapping-node-rest

   #:match-class-node
   #:match-class-node-cls
   #:match-class-node-patterns
   #:match-class-node-kwd-attrs
   #:match-class-node-kwd-patterns

   #:match-star-node
   #:match-star-node-name

   #:match-as-node
   #:match-as-node-pattern
   #:match-as-node-name

   #:match-or-node
   #:match-or-node-patterns

   ;; Type parameter nodes (PEP 695)
   #:type-var-node
   #:type-var-node-name
   #:type-var-node-bound

   #:param-spec-node
   #:param-spec-node-name

   #:type-var-tuple-node
   #:type-var-tuple-node-name

   ;; Operator keywords (boolean ops)
   ;; :and :or (standard CL keywords reused)

   ;; Binary operator keywords
   ;; Exported as keywords — consumers use e.g. :add :sub etc.
   ;; No defexport needed; keywords are self-exporting.

   ;; Expression context keywords: :load :store :del
   ;; Comparison operator keywords: :eq :not-eq :lt :lt-e :gt :gt-e :is :is-not :in :not-in
   ;; Unary operator keywords: :invert :not :u-add :u-sub
   ))

(in-package :clython.ast)

;;; ─── Operator / context symbols ────────────────────────────────────────────
;;;
;;; Rather than defining empty CLOS singleton classes for operators and
;;; expression contexts (as CPython does in C), we use plain keyword symbols.
;;; Consumers pattern-match on these keywords.
;;;
;;; Boolean ops  : :and | :or
;;; Binary ops   : :add | :sub | :mult | :mat-mult | :div | :mod | :pow
;;;                :l-shift | :r-shift | :bit-or | :bit-xor | :bit-and
;;;                :floor-div
;;; Unary ops    : :invert | :not | :u-add | :u-sub
;;; Compare ops  : :eq | :not-eq | :lt | :lt-e | :gt | :gt-e
;;;                :is | :is-not | :in | :not-in
;;; Expr context : :load | :store | :del

;;; ─── Base class ─────────────────────────────────────────────────────────────

(defclass py-ast-node ()
  ((line     :initarg :line     :accessor node-line     :initform nil
             :documentation "1-based line number of the first token.")
   (col      :initarg :col      :accessor node-col      :initform nil
             :documentation "0-based column offset of the first token.")
   (end-line :initarg :end-line :accessor node-end-line :initform nil
             :documentation "1-based line number of the last token.")
   (end-col  :initarg :end-col  :accessor node-end-col  :initform nil
             :documentation "0-based column offset past the last token."))
  (:documentation "Abstract base for all Python AST nodes."))

;;; ─── Module nodes ───────────────────────────────────────────────────────────

(defclass module-node (py-ast-node)
  ((body         :initarg :body         :accessor module-node-body
                 :initform nil
                 :documentation "List of statement nodes.")
   (type-ignores :initarg :type-ignores :accessor module-node-type-ignores
                 :initform nil
                 :documentation "List of type_ignore nodes."))
  (:documentation "Top-level module — root of a .py file."))

(defclass interactive-node (py-ast-node)
  ((body :initarg :body :accessor interactive-node-body
         :initform nil
         :documentation "List of statement nodes (single interactive statement)."))
  (:documentation "Interactive source (REPL input)."))

(defclass expression-node (py-ast-node)
  ((body :initarg :body :accessor expression-node-body
         :initform nil
         :documentation "A single expression node."))
  (:documentation "eval() / expression mode module."))

;;; ─── Statement nodes ────────────────────────────────────────────────────────

(defclass function-def-node (py-ast-node)
  ((name           :initarg :name           :accessor function-def-node-name
                   :initform nil)
   (args           :initarg :args           :accessor function-def-node-args
                   :initform nil)
   (body           :initarg :body           :accessor function-def-node-body
                   :initform nil)
   (decorator-list :initarg :decorator-list :accessor function-def-node-decorator-list
                   :initform nil)
   (returns        :initarg :returns        :accessor function-def-node-returns
                   :initform nil)
   (type-comment   :initarg :type-comment   :accessor function-def-node-type-comment
                   :initform nil)
   (type-params    :initarg :type-params    :accessor function-def-node-type-params
                   :initform nil))
  (:documentation "def <name>(<args>): <body>"))

(defclass async-function-def-node (py-ast-node)
  ((name           :initarg :name           :accessor async-function-def-node-name
                   :initform nil)
   (args           :initarg :args           :accessor async-function-def-node-args
                   :initform nil)
   (body           :initarg :body           :accessor async-function-def-node-body
                   :initform nil)
   (decorator-list :initarg :decorator-list :accessor async-function-def-node-decorator-list
                   :initform nil)
   (returns        :initarg :returns        :accessor async-function-def-node-returns
                   :initform nil)
   (type-comment   :initarg :type-comment   :accessor async-function-def-node-type-comment
                   :initform nil)
   (type-params    :initarg :type-params    :accessor async-function-def-node-type-params
                   :initform nil))
  (:documentation "async def <name>(<args>): <body>"))

(defclass class-def-node (py-ast-node)
  ((name           :initarg :name           :accessor class-def-node-name
                   :initform nil)
   (bases          :initarg :bases          :accessor class-def-node-bases
                   :initform nil)
   (keywords       :initarg :keywords       :accessor class-def-node-keywords
                   :initform nil)
   (body           :initarg :body           :accessor class-def-node-body
                   :initform nil)
   (decorator-list :initarg :decorator-list :accessor class-def-node-decorator-list
                   :initform nil)
   (type-params    :initarg :type-params    :accessor class-def-node-type-params
                   :initform nil))
  (:documentation "class <name>(<bases>): <body>"))

(defclass return-node (py-ast-node)
  ((value :initarg :value :accessor return-node-value :initform nil))
  (:documentation "return [<value>]"))

(defclass delete-node (py-ast-node)
  ((targets :initarg :targets :accessor delete-node-targets :initform nil))
  (:documentation "del <targets>"))

(defclass assign-node (py-ast-node)
  ((targets      :initarg :targets      :accessor assign-node-targets      :initform nil)
   (value        :initarg :value        :accessor assign-node-value        :initform nil)
   (type-comment :initarg :type-comment :accessor assign-node-type-comment :initform nil))
  (:documentation "<targets> = <value>"))

(defclass aug-assign-node (py-ast-node)
  ((target :initarg :target :accessor aug-assign-node-target :initform nil)
   (op     :initarg :op     :accessor aug-assign-node-op     :initform nil)
   (value  :initarg :value  :accessor aug-assign-node-value  :initform nil))
  (:documentation "<target> <op>= <value>  (augmented assignment)"))

(defclass ann-assign-node (py-ast-node)
  ((target     :initarg :target     :accessor ann-assign-node-target     :initform nil)
   (annotation :initarg :annotation :accessor ann-assign-node-annotation :initform nil)
   (value      :initarg :value      :accessor ann-assign-node-value      :initform nil)
   (simple     :initarg :simple     :accessor ann-assign-node-simple     :initform nil))
  (:documentation "<target>: <annotation> [= <value>]"))

(defclass for-node (py-ast-node)
  ((target       :initarg :target       :accessor for-node-target       :initform nil)
   (iter         :initarg :iter         :accessor for-node-iter         :initform nil)
   (body         :initarg :body         :accessor for-node-body         :initform nil)
   (orelse       :initarg :orelse       :accessor for-node-orelse       :initform nil)
   (type-comment :initarg :type-comment :accessor for-node-type-comment :initform nil))
  (:documentation "for <target> in <iter>: <body> [else: <orelse>]"))

(defclass async-for-node (py-ast-node)
  ((target       :initarg :target       :accessor async-for-node-target       :initform nil)
   (iter         :initarg :iter         :accessor async-for-node-iter         :initform nil)
   (body         :initarg :body         :accessor async-for-node-body         :initform nil)
   (orelse       :initarg :orelse       :accessor async-for-node-orelse       :initform nil)
   (type-comment :initarg :type-comment :accessor async-for-node-type-comment :initform nil))
  (:documentation "async for <target> in <iter>: <body> [else: <orelse>]"))

(defclass while-node (py-ast-node)
  ((test   :initarg :test   :accessor while-node-test   :initform nil)
   (body   :initarg :body   :accessor while-node-body   :initform nil)
   (orelse :initarg :orelse :accessor while-node-orelse :initform nil))
  (:documentation "while <test>: <body> [else: <orelse>]"))

(defclass if-node (py-ast-node)
  ((test   :initarg :test   :accessor if-node-test   :initform nil)
   (body   :initarg :body   :accessor if-node-body   :initform nil)
   (orelse :initarg :orelse :accessor if-node-orelse :initform nil))
  (:documentation "if <test>: <body> [elif/else: <orelse>]"))

(defclass with-node (py-ast-node)
  ((items        :initarg :items        :accessor with-node-items        :initform nil)
   (body         :initarg :body         :accessor with-node-body         :initform nil)
   (type-comment :initarg :type-comment :accessor with-node-type-comment :initform nil))
  (:documentation "with <items>: <body>"))

(defclass async-with-node (py-ast-node)
  ((items        :initarg :items        :accessor async-with-node-items        :initform nil)
   (body         :initarg :body         :accessor async-with-node-body         :initform nil)
   (type-comment :initarg :type-comment :accessor async-with-node-type-comment :initform nil))
  (:documentation "async with <items>: <body>"))

(defclass match-node (py-ast-node)
  ((subject :initarg :subject :accessor match-node-subject :initform nil)
   (cases   :initarg :cases   :accessor match-node-cases   :initform nil))
  (:documentation "match <subject>: <cases>"))

(defclass raise-node (py-ast-node)
  ((exc   :initarg :exc   :accessor raise-node-exc   :initform nil)
   (cause :initarg :cause :accessor raise-node-cause :initform nil))
  (:documentation "raise [<exc> [from <cause>]]"))

(defclass try-node (py-ast-node)
  ((body      :initarg :body      :accessor try-node-body      :initform nil)
   (handlers  :initarg :handlers  :accessor try-node-handlers  :initform nil)
   (orelse    :initarg :orelse    :accessor try-node-orelse    :initform nil)
   (finalbody :initarg :finalbody :accessor try-node-finalbody :initform nil))
  (:documentation "try: <body> [except ...: ...] [else: ...] [finally: ...]"))

(defclass try-star-node (py-ast-node)
  ((body      :initarg :body      :accessor try-star-node-body      :initform nil)
   (handlers  :initarg :handlers  :accessor try-star-node-handlers  :initform nil)
   (orelse    :initarg :orelse    :accessor try-star-node-orelse    :initform nil)
   (finalbody :initarg :finalbody :accessor try-star-node-finalbody :initform nil))
  (:documentation "try: <body> except* ...: ... (PEP 654 exception groups)"))

(defclass assert-node (py-ast-node)
  ((test :initarg :test :accessor assert-node-test :initform nil)
   (msg  :initarg :msg  :accessor assert-node-msg  :initform nil))
  (:documentation "assert <test> [, <msg>]"))

(defclass import-node (py-ast-node)
  ((names :initarg :names :accessor import-node-names :initform nil))
  (:documentation "import <names>"))

(defclass import-from-node (py-ast-node)
  ((module :initarg :module :accessor import-from-node-module :initform nil)
   (names  :initarg :names  :accessor import-from-node-names  :initform nil)
   (level  :initarg :level  :accessor import-from-node-level  :initform nil))
  (:documentation "from <module> import <names>"))

(defclass global-node (py-ast-node)
  ((names :initarg :names :accessor global-node-names :initform nil))
  (:documentation "global <names>"))

(defclass nonlocal-node (py-ast-node)
  ((names :initarg :names :accessor nonlocal-node-names :initform nil))
  (:documentation "nonlocal <names>"))

(defclass expr-stmt-node (py-ast-node)
  ((value :initarg :value :accessor expr-stmt-node-value :initform nil))
  (:documentation "An expression used as a statement."))

(defclass pass-node (py-ast-node) ()
  (:documentation "pass"))

(defclass break-node (py-ast-node) ()
  (:documentation "break"))

(defclass continue-node (py-ast-node) ()
  (:documentation "continue"))

(defclass type-alias-node (py-ast-node)
  ((name        :initarg :name        :accessor type-alias-node-name        :initform nil)
   (type-params :initarg :type-params :accessor type-alias-node-type-params :initform nil)
   (value       :initarg :value       :accessor type-alias-node-value       :initform nil))
  (:documentation "type <name>[<type-params>] = <value>  (PEP 695)"))

;;; ─── Expression nodes ───────────────────────────────────────────────────────

(defclass bool-op-node (py-ast-node)
  ((op     :initarg :op     :accessor bool-op-node-op     :initform nil
           :documentation ":and or :or")
   (values :initarg :values :accessor bool-op-node-values :initform nil))
  (:documentation "<values[0]> <op> <values[1]> ..."))

(defclass named-expr-node (py-ast-node)
  ((target :initarg :target :accessor named-expr-node-target :initform nil)
   (value  :initarg :value  :accessor named-expr-node-value  :initform nil))
  (:documentation "<target> := <value>  (walrus operator)"))

(defclass bin-op-node (py-ast-node)
  ((left  :initarg :left  :accessor bin-op-node-left  :initform nil)
   (op    :initarg :op    :accessor bin-op-node-op    :initform nil
          :documentation "Keyword such as :add :sub :mult etc.")
   (right :initarg :right :accessor bin-op-node-right :initform nil))
  (:documentation "<left> <op> <right>"))

(defclass unary-op-node (py-ast-node)
  ((op      :initarg :op      :accessor unary-op-node-op      :initform nil
            :documentation "Keyword: :invert :not :u-add :u-sub")
   (operand :initarg :operand :accessor unary-op-node-operand :initform nil))
  (:documentation "<op> <operand>"))

(defclass lambda-node (py-ast-node)
  ((args :initarg :args :accessor lambda-node-args :initform nil)
   (body :initarg :body :accessor lambda-node-body :initform nil))
  (:documentation "lambda <args>: <body>"))

(defclass if-exp-node (py-ast-node)
  ((test   :initarg :test   :accessor if-exp-node-test   :initform nil)
   (body   :initarg :body   :accessor if-exp-node-body   :initform nil)
   (orelse :initarg :orelse :accessor if-exp-node-orelse :initform nil))
  (:documentation "<body> if <test> else <orelse>"))

(defclass dict-node (py-ast-node)
  ((keys   :initarg :keys   :accessor dict-node-keys   :initform nil
           :documentation "List of key nodes; NIL entry means **unpacking.")
   (values :initarg :values :accessor dict-node-values :initform nil))
  (:documentation "{<keys[0]>: <values[0]>, ...}"))

(defclass set-node (py-ast-node)
  ((elts :initarg :elts :accessor set-node-elts :initform nil))
  (:documentation "{<elts>}"))

(defclass list-comp-node (py-ast-node)
  ((elt        :initarg :elt        :accessor list-comp-node-elt        :initform nil)
   (generators :initarg :generators :accessor list-comp-node-generators :initform nil))
  (:documentation "[<elt> for ... in ...]"))

(defclass set-comp-node (py-ast-node)
  ((elt        :initarg :elt        :accessor set-comp-node-elt        :initform nil)
   (generators :initarg :generators :accessor set-comp-node-generators :initform nil))
  (:documentation "{<elt> for ... in ...}"))

(defclass dict-comp-node (py-ast-node)
  ((key        :initarg :key        :accessor dict-comp-node-key        :initform nil)
   (value      :initarg :value      :accessor dict-comp-node-value      :initform nil)
   (generators :initarg :generators :accessor dict-comp-node-generators :initform nil))
  (:documentation "{<key>: <value> for ... in ...}"))

(defclass generator-exp-node (py-ast-node)
  ((elt        :initarg :elt        :accessor generator-exp-node-elt        :initform nil)
   (generators :initarg :generators :accessor generator-exp-node-generators :initform nil))
  (:documentation "(<elt> for ... in ...)"))

(defclass await-node (py-ast-node)
  ((value :initarg :value :accessor await-node-value :initform nil))
  (:documentation "await <value>"))

(defclass yield-node (py-ast-node)
  ((value :initarg :value :accessor yield-node-value :initform nil))
  (:documentation "yield [<value>]"))

(defclass yield-from-node (py-ast-node)
  ((value :initarg :value :accessor yield-from-node-value :initform nil))
  (:documentation "yield from <value>"))

(defclass compare-node (py-ast-node)
  ((left        :initarg :left        :accessor compare-node-left        :initform nil)
   (ops         :initarg :ops         :accessor compare-node-ops         :initform nil
                :documentation "List of comparison operator keywords.")
   (comparators :initarg :comparators :accessor compare-node-comparators :initform nil))
  (:documentation "<left> <ops[0]> <comparators[0]> ..."))

(defclass call-node (py-ast-node)
  ((func     :initarg :func     :accessor call-node-func     :initform nil)
   (args     :initarg :args     :accessor call-node-args     :initform nil)
   (keywords :initarg :keywords :accessor call-node-keywords :initform nil))
  (:documentation "<func>(<args>, <keywords>)"))

(defclass formatted-value-node (py-ast-node)
  ((value       :initarg :value       :accessor formatted-value-node-value       :initform nil)
   (conversion  :initarg :conversion  :accessor formatted-value-node-conversion  :initform nil
                :documentation "Integer: -1 none, 115 s, 114 r, 97 a")
   (format-spec :initarg :format-spec :accessor formatted-value-node-format-spec :initform nil))
  (:documentation "f-string conversion node: {<value>!<conversion>:<format-spec>}"))

(defclass joined-str-node (py-ast-node)
  ((values :initarg :values :accessor joined-str-node-values :initform nil))
  (:documentation "f-string: concatenated constant/formatted-value nodes."))

(defclass constant-node (py-ast-node)
  ((value :initarg :value :accessor constant-node-value :initform nil
          :documentation "Literal value: number, string, bytes, True, False, None, Ellipsis.")
   (kind  :initarg :kind  :accessor constant-node-kind  :initform nil
          :documentation "Optional string, e.g. \"u\" for u-strings."))
  (:documentation "A literal constant."))

(defclass attribute-node (py-ast-node)
  ((value :initarg :value :accessor attribute-node-value :initform nil)
   (attr  :initarg :attr  :accessor attribute-node-attr  :initform nil
          :documentation "Attribute name as a string.")
   (ctx   :initarg :ctx   :accessor attribute-node-ctx   :initform :load
          :documentation ":load | :store | :del"))
  (:documentation "<value>.<attr>"))

(defclass subscript-node (py-ast-node)
  ((value :initarg :value :accessor subscript-node-value :initform nil)
   (slice :initarg :slice :accessor subscript-node-slice :initform nil)
   (ctx   :initarg :ctx   :accessor subscript-node-ctx   :initform :load
          :documentation ":load | :store | :del"))
  (:documentation "<value>[<slice>]"))

(defclass starred-node (py-ast-node)
  ((value :initarg :value :accessor starred-node-value :initform nil)
   (ctx   :initarg :ctx   :accessor starred-node-ctx   :initform :load
          :documentation ":load | :store | :del"))
  (:documentation "*<value>"))

(defclass name-node (py-ast-node)
  ((id  :initarg :id  :accessor name-node-id  :initform nil
        :documentation "Identifier string.")
   (ctx :initarg :ctx :accessor name-node-ctx :initform :load
        :documentation ":load | :store | :del"))
  (:documentation "A bare name reference."))

(defclass list-node (py-ast-node)
  ((elts :initarg :elts :accessor list-node-elts :initform nil)
   (ctx  :initarg :ctx  :accessor list-node-ctx  :initform :load
         :documentation ":load | :store"))
  (:documentation "[<elts>]"))

(defclass tuple-node (py-ast-node)
  ((elts :initarg :elts :accessor tuple-node-elts :initform nil)
   (ctx  :initarg :ctx  :accessor tuple-node-ctx  :initform :load
         :documentation ":load | :store"))
  (:documentation "(<elts>,)"))

(defclass slice-node (py-ast-node)
  ((lower :initarg :lower :accessor slice-node-lower :initform nil)
   (upper :initarg :upper :accessor slice-node-upper :initform nil)
   (step  :initarg :step  :accessor slice-node-step  :initform nil))
  (:documentation "<lower>:<upper>[:<step>]"))

;;; ─── Auxiliary types ────────────────────────────────────────────────────────

(defclass py-comprehension ()
  ((target   :initarg :target   :accessor comprehension-target   :initform nil)
   (iter     :initarg :iter     :accessor comprehension-iter     :initform nil)
   (ifs      :initarg :ifs      :accessor comprehension-ifs      :initform nil)
   (is-async :initarg :is-async :accessor comprehension-is-async :initform nil))
  (:documentation "A single 'for ... in ... if ...' comprehension clause."))

(defclass py-arguments ()
  ((posonlyargs  :initarg :posonlyargs  :accessor arguments-posonlyargs  :initform nil
                 :documentation "Positional-only arguments (before /).")
   (args         :initarg :args         :accessor arguments-args         :initform nil)
   (vararg       :initarg :vararg       :accessor arguments-vararg       :initform nil
                 :documentation "*args argument or NIL.")
   (kwonlyargs   :initarg :kwonlyargs   :accessor arguments-kwonlyargs   :initform nil)
   (kw-defaults  :initarg :kw-defaults  :accessor arguments-kw-defaults  :initform nil)
   (kwarg        :initarg :kwarg        :accessor arguments-kwarg        :initform nil
                 :documentation "**kwargs argument or NIL.")
   (defaults     :initarg :defaults     :accessor arguments-defaults     :initform nil))
  (:documentation "Full argument specification for a function/lambda."))

(defclass py-arg ()
  ((arg          :initarg :arg          :accessor arg-arg          :initform nil
                 :documentation "Argument name string.")
   (annotation   :initarg :annotation   :accessor arg-annotation   :initform nil)
   (type-comment :initarg :type-comment :accessor arg-type-comment :initform nil))
  (:documentation "A single function argument (name + optional annotation)."))

(defclass py-keyword ()
  ((arg   :initarg :arg   :accessor keyword-arg   :initform nil
          :documentation "Keyword name string, or NIL for **unpacking.")
   (value :initarg :value :accessor keyword-value :initform nil))
  (:documentation "A keyword argument in a call: <arg>=<value>."))

(defclass py-alias ()
  ((name   :initarg :name   :accessor alias-name   :initform nil)
   (asname :initarg :asname :accessor alias-asname :initform nil))
  (:documentation "An imported name: <name> [as <asname>]."))

(defclass py-with-item ()
  ((context-expr  :initarg :context-expr  :accessor with-item-context-expr  :initform nil)
   (optional-vars :initarg :optional-vars :accessor with-item-optional-vars :initform nil))
  (:documentation "A single 'with' item: <context-expr> [as <optional-vars>]."))

(defclass py-match-case ()
  ((pattern :initarg :pattern :accessor match-case-pattern :initform nil)
   (guard   :initarg :guard   :accessor match-case-guard   :initform nil)
   (body    :initarg :body    :accessor match-case-body    :initform nil))
  (:documentation "case <pattern> [if <guard>]: <body>"))

(defclass py-exception-handler ()
  ((type :initarg :type :accessor exception-handler-type :initform nil)
   (name :initarg :name :accessor exception-handler-name :initform nil
         :documentation "Bound name string for 'except Exc as name', or NIL.")
   (body :initarg :body :accessor exception-handler-body :initform nil))
  (:documentation "except [<type> [as <name>]]: <body>"))

;;; ─── Pattern nodes (structural pattern matching) ────────────────────────────

(defclass match-value-node (py-ast-node)
  ((value :initarg :value :accessor match-value-node-value :initform nil))
  (:documentation "case <value>  — a dotted name or attribute pattern."))

(defclass match-singleton-node (py-ast-node)
  ((value :initarg :value :accessor match-singleton-node-value :initform nil
          :documentation "T, NIL, or :ellipsis (Python True/False/None)."))
  (:documentation "case True | False | None"))

(defclass match-sequence-node (py-ast-node)
  ((patterns :initarg :patterns :accessor match-sequence-node-patterns :initform nil))
  (:documentation "case [<patterns>]  or  case (<patterns>)"))

(defclass match-mapping-node (py-ast-node)
  ((keys     :initarg :keys     :accessor match-mapping-node-keys     :initform nil)
   (patterns :initarg :patterns :accessor match-mapping-node-patterns :initform nil)
   (rest     :initarg :rest     :accessor match-mapping-node-rest     :initform nil
             :documentation "Name for **rest capture, or NIL."))
  (:documentation "case {<keys[0]>: <patterns[0]>, ..., **<rest>}"))

(defclass match-class-node (py-ast-node)
  ((cls          :initarg :cls          :accessor match-class-node-cls          :initform nil)
   (patterns     :initarg :patterns     :accessor match-class-node-patterns     :initform nil)
   (kwd-attrs    :initarg :kwd-attrs    :accessor match-class-node-kwd-attrs    :initform nil)
   (kwd-patterns :initarg :kwd-patterns :accessor match-class-node-kwd-patterns :initform nil))
  (:documentation "case ClassName(<patterns>, <kwd-attrs>=<kwd-patterns>)"))

(defclass match-star-node (py-ast-node)
  ((name :initarg :name :accessor match-star-node-name :initform nil
         :documentation "Capture name or NIL for bare *."))
  (:documentation "case [*, <name>]  — star pattern inside sequence."))

(defclass match-as-node (py-ast-node)
  ((pattern :initarg :pattern :accessor match-as-node-pattern :initform nil)
   (name    :initarg :name    :accessor match-as-node-name    :initform nil))
  (:documentation "case <pattern> as <name>  or  case _"))

(defclass match-or-node (py-ast-node)
  ((patterns :initarg :patterns :accessor match-or-node-patterns :initform nil))
  (:documentation "case <p1> | <p2> | ..."))

;;; ─── Type parameter nodes (PEP 695) ─────────────────────────────────────────

(defclass type-var-node (py-ast-node)
  ((name  :initarg :name  :accessor type-var-node-name  :initform nil)
   (bound :initarg :bound :accessor type-var-node-bound :initform nil))
  (:documentation "T (TypeVar) in a type parameter list."))

(defclass param-spec-node (py-ast-node)
  ((name :initarg :name :accessor param-spec-node-name :initform nil))
  (:documentation "**P (ParamSpec) in a type parameter list."))

(defclass type-var-tuple-node (py-ast-node)
  ((name :initarg :name :accessor type-var-tuple-node-name :initform nil))
  (:documentation "*Ts (TypeVarTuple) in a type parameter list."))
