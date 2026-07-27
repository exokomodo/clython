;;;; modules/abc.lisp — abc built-in module (minimal implementation)
;;;;
;;;; Provides:
;;;;   abstractmethod  - decorator that marks a method as abstract
;;;;   ABC             - base class that enables abstract method checking
;;;;   ABCMeta         - metaclass stub (alias to type for compatibility)
;;;;
;;;; Implementation strategy:
;;;;   - @abstractmethod sets __isabstractmethod__ = True on the function
;;;;   - eval-node (class-def-node) detects ABC in bases and calls
;;;;     %compute-abstract-methods to populate __abstractmethods__
;;;;   - py-call (py-type) checks __abstractmethods__ before instantiation

(in-package :clython.imports)

(defun make-abc-module ()
  "Create the abc module."
  (let ((mod (clython.runtime:make-py-module "abc")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "abc"))

      ;;; ── abstractmethod ──────────────────────────────────────────────────

      (setf (gethash "abstractmethod" d)
            (clython.runtime:make-py-function
             :name "abstractmethod"
             :cl-fn (lambda (fn &rest _)
                      (declare (ignore _))
                      (when (typep fn 'clython.runtime:py-function)
                        (clython.runtime:py-setattr
                         fn "__isabstractmethod__"
                         clython.runtime:+py-true+))
                      fn)))

      ;;; ── ABC base class ──────────────────────────────────────────────────

      ;; ABC is a sentinel base class.  Subclasses of ABC automatically get
      ;; __abstractmethods__ computed at class-definition time (handled in
      ;; eval.lisp's class-def-node evaluator via %abc-base-p).
      (let ((abc-type (clython.runtime:make-py-type :name "ABC")))
        ;; Mark it so eval.lisp can detect it
        (setf (gethash "__is_abc__" (clython.runtime:py-type-dict abc-type))
              clython.runtime:+py-true+)
        (setf (gethash "__abstractmethods__"
                       (clython.runtime:py-type-dict abc-type))
              (clython.runtime:make-py-set nil))
        ;; register(subclass) — stores subclass in _abc_registry
        ;; Stored with a closure so it works when called as MyABC.register(C)
        ;; (no auto-bound self, since it's a plain function on a type).
        (setf (gethash "_abc_registry" (clython.runtime:py-type-dict abc-type))
              (clython.runtime:make-py-list nil))
        (let ((captured-cls abc-type))
          (setf (gethash "register" (clython.runtime:py-type-dict abc-type))
                (clython.runtime:make-py-function
                 :name "register"
                 :cl-fn (lambda (subclass &rest _)
                          (declare (ignore _))
                          (let ((reg (gethash "_abc_registry"
                                              (clython.runtime:py-type-dict captured-cls))))
                            (when (typep reg 'clython.runtime:py-list)
                              (vector-push-extend
                               subclass
                               (clython.runtime:py-list-value reg))))
                          subclass))))
        (setf (gethash "ABC" d) abc-type))

      ;;; ── ABCMeta (alias to type for compatibility) ───────────────────────

      (setf (gethash "ABCMeta" d)
            (clython.runtime:make-py-type :name "ABCMeta"))

      ;;; ── get_cache_token (stub) ──────────────────────────────────────────

      (setf (gethash "get_cache_token" d)
            (clython.runtime:make-py-function
             :name "get_cache_token"
             :cl-fn (lambda (&rest _) (declare (ignore _))
                      (clython.runtime:make-py-int 0)))))
    mod))
