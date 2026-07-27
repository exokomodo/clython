;;;; modules/gc.lisp — gc (garbage collection) built-in module stub
;;;;
;;;; Clython does not use reference counting or a cycle collector.
;;;; gc.collect() is a no-op; gc.isenabled() always returns True.

(in-package :clython.imports)

(defun make-gc-module ()
  "Create a gc module stub."
  (let ((mod (clython.runtime:make-py-module "gc")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "gc"))

      ;; gc.collect([generation]) — trigger SBCL full GC; returns 0
      (setf (gethash "collect" d)
            (clython.runtime:make-py-function
             :name "collect"
             :cl-fn (lambda (&rest _)
                      (declare (ignore _))
                      (sb-ext:gc :full t)
                      (clython.runtime:make-py-int 0))))

      ;; gc.isenabled() — Clython has no GC toggle; always return True
      (setf (gethash "isenabled" d)
            (clython.runtime:make-py-function
             :name "isenabled"
             :cl-fn (lambda (&rest _)
                      (declare (ignore _))
                      clython.runtime:+py-true+)))

      ;; gc.enable() / gc.disable() — no-ops
      (setf (gethash "enable" d)
            (clython.runtime:make-py-function
             :name "enable"
             :cl-fn (lambda (&rest _) (declare (ignore _)) clython.runtime:+py-none+)))
      (setf (gethash "disable" d)
            (clython.runtime:make-py-function
             :name "disable"
             :cl-fn (lambda (&rest _) (declare (ignore _)) clython.runtime:+py-none+)))

      ;; gc.get_objects() — return empty list (no tracked objects)
      (setf (gethash "get_objects" d)
            (clython.runtime:make-py-function
             :name "get_objects"
             :cl-fn (lambda (&rest _)
                      (declare (ignore _))
                      (clython.runtime:make-py-list nil)))))
    mod))
