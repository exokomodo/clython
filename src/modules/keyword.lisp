;;;; modules/keyword.lisp — keyword built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

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

