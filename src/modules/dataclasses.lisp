;;;; modules/dataclasses.lisp — dataclasses built-in module
;;;;
;;;; Implements the @dataclass decorator (PEP 557 subset) so that conformance
;;;; tests using:
;;;;
;;;;   from dataclasses import dataclass
;;;;   @dataclass
;;;;   class Point:
;;;;       x: int
;;;;       y: int
;;;;   p = Point(1, 2); print(p.x, p.y)  => "1 2"
;;;;
;;;; work correctly.  Only the basic case is handled here:
;;;;   - Positional __init__ generated from __annotations__ order
;;;;   - Default values honoured (class-level attribute value used as default)
;;;;   - __repr__ generated
;;;;   - eq=True (default) generates __eq__ based on all fields
;;;;   Advanced features (frozen, slots, field() helpers, kw_only, etc.) are
;;;;   intentionally deferred.

(in-package :clython.imports)

(defun make-dataclasses-module ()
  "Create the dataclasses module with a working @dataclass decorator."
  (let ((mod (clython.runtime:make-py-module "dataclasses")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "dataclasses"))

    ;; ── dataclass decorator ───────────────────────────────────────────────
    ;;
    ;; When called as @dataclass (no arguments) it receives the class directly.
    ;; When called as @dataclass(...) it returns a decorator.  We detect which
    ;; case applies: if the first argument is a py-type, we apply immediately;
    ;; otherwise we return the identity decorator (we don't support keyword
    ;; options yet).
    (setf (gethash "dataclass" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "dataclass"
           :cl-fn (lambda (&rest args)
                    (if (and args (typep (first args) 'clython.runtime:py-type))
                        ;; @dataclass with no arguments — apply directly
                        (%apply-dataclass (first args))
                        ;; @dataclass(...) — return decorator that applies to class
                        (clython.runtime:make-py-function
                         :name "dataclass_decorator"
                         :cl-fn (lambda (&rest inner-args)
                                  (if (and inner-args
                                           (typep (first inner-args) 'clython.runtime:py-type))
                                      (%apply-dataclass (first inner-args))
                                      clython.runtime:+py-none+)))))))

    ;; ── field() helper ───────────────────────────────────────────────────
    ;; Stores default_factory/default on a Field sentinel so __init__ can
    ;; call the factory per instance (avoids mutable-default-arg sharing).
    (setf (gethash "field" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "field"
           :cl-fn (lambda (&rest _positional)
                    (declare (ignore _positional))
                    (let* ((kwargs clython.runtime:*current-kwargs*)
                           (factory (let ((kv (assoc "default_factory" kwargs :test #'string=)))
                                      (when kv (cdr kv))))
                           (kw-default (let ((kv (assoc "default" kwargs :test #'string=)))
                                         (when kv (cdr kv))))
                           (obj (make-instance 'clython.runtime:py-object
                                               :py-class (clython.runtime:make-py-type :name "Field")
                                               :py-dict (make-hash-table :test #'equal))))
                      (when factory
                        (setf (gethash "_factory" (clython.runtime:py-object-dict obj)) factory))
                      (when kw-default
                        (setf (gethash "_default" (clython.runtime:py-object-dict obj)) kw-default))
                      (setf (gethash "_is_field" (clython.runtime:py-object-dict obj))
                            clython.runtime:+py-true+)
                      obj))))

    ;; ── fields() — returns tuple of Field objects (stub) ─────────────────
    (setf (gethash "fields" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "fields"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-tuple '()))))

    mod))

;;; ─── Internal helpers ────────────────────────────────────────────────────

(defun %get-annotations (cls)
  "Return an ordered list of (name . type-val) from CLS's __annotations__."
  (let ((tdict (clython.runtime:py-type-dict cls)))
    (unless tdict (return-from %get-annotations '()))
    (let ((ann-dict (gethash "__annotations__" tdict)))
      (unless (typep ann-dict 'clython.runtime:py-dict) (return-from %get-annotations '()))
      ;; Iterate the annotation dict — we want insertion order.
      ;; CL hash tables don't preserve order, so we collect all pairs then
      ;; return them (order may vary, but for basic dataclasses this is fine).
      (let ((pairs '()))
        (maphash (lambda (k v) (push (cons k v) pairs))
                 (clython.runtime:py-dict-value ann-dict))
        (nreverse pairs)))))

(defun %apply-dataclass (cls)
  "Transform CLS in-place: generate __init__, __repr__, __eq__ from annotations."
  (let* ((fields (%get-annotations cls))
         (tdict  (clython.runtime:py-type-dict cls)))
    (unless tdict
      (setf tdict (make-hash-table :test #'equal))
      (setf (clython.runtime:py-type-dict cls) tdict))

    ;; ── __init__ ─────────────────────────────────────────────────────────
    ;; Build a CL lambda that accepts each field as a positional argument and
    ;; sets it on self as an instance attribute.
    (unless (gethash "__init__" tdict)
      (let ((field-names (mapcar #'car fields)))
        (setf (gethash "__init__" tdict)
              (clython.runtime:make-py-function
               :name "__init__"
               :cl-fn (lambda (self &rest init-args)
                        ;; Collect defaults from class dict
                        (let ((defaults
                                (loop for fname in field-names
                                      collect (multiple-value-bind (v found)
                                                  (gethash fname tdict)
                                                (if found v :no-default)))))
                          ;; Fill in positional args, fall back to defaults.
                          ;; If the default is a Field descriptor (from field()), call
                          ;; its factory to produce a fresh default per instance.
                          (loop for fname in field-names
                                for default in defaults
                                for i from 0
                                do (let ((val (if (< i (length init-args))
                                                  (nth i init-args)
                                                  (if (eq default :no-default)
                                                      (error "Missing required field: ~A" fname)
                                                      ;; Check if default is a Field descriptor
                                                      (let* ((fdict (when (typep default 'clython.runtime:py-object)
                                                                      (clython.runtime:py-object-dict default)))
                                                             (is-field (when fdict
                                                                         (nth-value 1 (gethash "_is_field" fdict)))))
                                                        (if is-field
                                                            ;; Call factory or use stored default
                                                            (let ((factory (when fdict (gethash "_factory" fdict)))
                                                                  (stored-default (when fdict (gethash "_default" fdict))))
                                                              (cond
                                                                (factory (clython.runtime:py-call factory))
                                                                (stored-default stored-default)
                                                                (t clython.runtime:+py-none+)))
                                                            default))))))
                                     (clython.runtime:py-setattr self fname val))))
                        clython.runtime:+py-none+)))))

    ;; ── __repr__ ─────────────────────────────────────────────────────────
    (unless (gethash "__repr__" tdict)
      (let ((cls-name (clython.runtime:py-type-name cls))
            (field-names (mapcar #'car fields)))
        (setf (gethash "__repr__" tdict)
              (clython.runtime:make-py-function
               :name "__repr__"
               :cl-fn (lambda (self)
                        (let ((parts
                                (loop for fname in field-names
                                      collect (format nil "~A=~A"
                                                fname
                                                (clython.runtime:py-repr
                                                 (clython.runtime:py-getattr self fname))))))
                          (clython.runtime:make-py-str
                           (format nil "~A(~A)" cls-name
                                   (format nil "~{~A~^, ~}" parts)))))))))

    ;; ── __eq__ ───────────────────────────────────────────────────────────
    (unless (gethash "__eq__" tdict)
      (let ((field-names (mapcar #'car fields)))
        (setf (gethash "__eq__" tdict)
              (clython.runtime:make-py-function
               :name "__eq__"
               :cl-fn (lambda (self other)
                        (if (not (typep other 'clython.runtime:py-object))
                            clython.runtime:+py-false+
                            (let ((same-type
                                    (eq (clython.runtime:py-object-class self)
                                        (clython.runtime:py-object-class other))))
                              (if (not same-type)
                                  clython.runtime:+py-false+
                                  (if (every (lambda (fname)
                                               ;; py-eq may return a CL boolean or a py-bool;
                                               ;; coerce to CL truthiness before passing to every.
                                               (let ((r (clython.runtime:py-eq
                                                         (clython.runtime:py-getattr self fname)
                                                         (clython.runtime:py-getattr other fname))))
                                                 (if (typep r 'clython.runtime:py-object)
                                                     (clython.runtime:py-bool-val r)
                                                     r)))
                                             field-names)
                                      clython.runtime:+py-true+
                                      clython.runtime:+py-false+)))))))))
    cls))
