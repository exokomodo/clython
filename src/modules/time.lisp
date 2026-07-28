;;;; modules/time.lisp — time built-in module
;;;;
;;;; Implements a subset of Python's time module using CL primitives.

(in-package :clython.imports)

;;; Unix epoch offset: CL universal-time is seconds since 1900-01-01 00:00:00 UTC
;;; Python time.time() is seconds since 1970-01-01 00:00:00 UTC
;;; Difference: 70 years = 2208988800 seconds
(defconstant +unix-epoch-offset+ 2208988800)

(defun make-time-module ()
  "Create the time built-in module."
  (let ((mod (clython.runtime:make-py-module "time"))
        (d nil))
    (setf d (clython.runtime:py-module-dict mod))

    ;; time.time() → float seconds since Unix epoch (UTC)
    (setf (gethash "time" d)
          (clython.runtime:make-py-function
           :name "time"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-float
                     (coerce (- (get-universal-time) +unix-epoch-offset+)
                             'double-float)))))

    ;; time.monotonic() → float seconds, monotonically increasing
    (setf (gethash "monotonic" d)
          (clython.runtime:make-py-function
           :name "monotonic"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-float
                     (coerce (/ (get-internal-real-time)
                                internal-time-units-per-second)
                             'double-float)))))

    ;; time.perf_counter() → same as monotonic for our purposes
    (setf (gethash "perf_counter" d)
          (clython.runtime:make-py-function
           :name "perf_counter"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-float
                     (coerce (/ (get-internal-real-time)
                                internal-time-units-per-second)
                             'double-float)))))

    ;; time.process_time() → CPU time used by process
    (setf (gethash "process_time" d)
          (clython.runtime:make-py-function
           :name "process_time"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-float
                     (coerce (/ (get-internal-run-time)
                                internal-time-units-per-second)
                             'double-float)))))

    ;; time.sleep(secs) → None
    (setf (gethash "sleep" d)
          (clython.runtime:make-py-function
           :name "sleep"
           :cl-fn (lambda (secs)
                    (let ((s (clython.runtime:py->cl secs)))
                      (sleep (coerce s 'double-float)))
                    clython.runtime:+py-none+)))

    ;; time.time_ns() → integer nanoseconds since Unix epoch (UTC)
    (setf (gethash "time_ns" d)
          (clython.runtime:make-py-function
           :name "time_ns"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-int
                     (* (- (get-universal-time) +unix-epoch-offset+)
                        1000000000)))))

    ;; time.monotonic_ns() → integer nanoseconds, monotonically increasing
    (setf (gethash "monotonic_ns" d)
          (clython.runtime:make-py-function
           :name "monotonic_ns"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-int
                     (round (* (/ (get-internal-real-time)
                                  internal-time-units-per-second)
                               1000000000))))))

    ;; time.localtime() → stub returning None (rarely needed)
    (setf (gethash "localtime" d)
          (clython.runtime:make-py-function
           :name "localtime"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    clython.runtime:+py-none+)))

    ;; time.gmtime() → stub returning None
    (setf (gethash "gmtime" d)
          (clython.runtime:make-py-function
           :name "gmtime"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    clython.runtime:+py-none+)))

    ;; time.strftime(fmt, ...) → stub returning empty string
    (setf (gethash "strftime" d)
          (clython.runtime:make-py-function
           :name "strftime"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    (clython.runtime:make-py-str ""))))

    ;; Constants
    (setf (gethash "timezone" d) (clython.runtime:make-py-int 0))  ; UTC offset in seconds

    (setf (gethash "__name__" d) (clython.runtime:make-py-str "time"))
    mod))
