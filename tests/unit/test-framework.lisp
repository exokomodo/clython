;;;; Minimal test framework for Clython unit tests.
;;;; No external dependencies — just SBCL + ASDF.

(defpackage :clython.test
  (:use :cl)
  (:export #:deftest
           #:assert-true
           #:assert-false
           #:assert-equal
           #:assert-not-nil
           #:assert-condition
           #:run-all-tests
           #:run-suite
           #:*test-registry*
           #:*verbose*))

(in-package :clython.test)

(defvar *test-registry* (make-hash-table :test 'equal)
  "Maps suite-name -> list of (test-name . test-fn).")

(defvar *verbose* t
  "When true, print individual test results.")

(defvar *current-suite* "default"
  "Current test suite name for registration.")

(defvar *pass-count* 0)
(defvar *fail-count* 0)
(defvar *error-count* 0)
(defvar *failures* nil)

(defmacro deftest (name (&key (suite "default")) &body body)
  "Define a test function and register it in a suite."
  (let ((fn-name (intern (format nil "TEST-~A" name))))
    `(progn
       (defun ,fn-name ()
         ,@body)
       (let ((suite-tests (gethash ,suite *test-registry*)))
         (setf (gethash ,suite *test-registry*)
               (append (remove-if (lambda (pair) (string= (car pair) ,(string name)))
                                  suite-tests)
                       (list (cons ,(string name) #',fn-name))))))))

(defun assert-true (value &optional message)
  "Assert that VALUE is truthy."
  (unless value
    (error "Assertion failed: expected truthy value~@[: ~A~]" message)))

(defun assert-false (value &optional message)
  "Assert that VALUE is falsy."
  (when value
    (error "Assertion failed: expected falsy value, got ~S~@[: ~A~]" value message)))

(defun assert-equal (expected actual &optional message)
  "Assert that EXPECTED and ACTUAL are EQUAL."
  (unless (equal expected actual)
    (error "Assertion failed: expected ~S, got ~S~@[: ~A~]" expected actual message)))

(defun assert-not-nil (value &optional message)
  "Assert that VALUE is not NIL."
  (when (null value)
    (error "Assertion failed: expected non-NIL~@[: ~A~]" message)))

(defmacro assert-condition (condition-type &body body)
  "Assert that BODY signals a condition of CONDITION-TYPE."
  `(handler-case
       (progn ,@body
              (error "Assertion failed: expected condition ~A but none was signaled"
                     ',condition-type))
     (,condition-type () t)
     (error (e)
       (error "Assertion failed: expected ~A but got ~A: ~A"
              ',condition-type (type-of e) e))))

(defun run-suite (suite-name)
  "Run all tests in a suite. Returns (values pass-count fail-count error-count)."
  (let ((tests (gethash suite-name *test-registry*))
        (pass 0) (fail 0) (errs 0) (failures nil))
    (unless tests
      (format t "~&No tests found in suite ~S~%" suite-name)
      (return-from run-suite (values 0 0 0)))
    (format t "~&=== Suite: ~A (~D tests) ===~%" suite-name (length tests))
    (dolist (test tests)
      (let ((name (car test))
            (fn (cdr test)))
        (handler-case
            (progn
              (funcall fn)
              (incf pass)
              (when *verbose*
                (format t "  PASS  ~A~%" name)))
          (error (e)
            (incf fail)
            (push (cons name (format nil "~A" e)) failures)
            (when *verbose*
              (format t "  FAIL  ~A: ~A~%" name e))))))
    (format t "~&--- ~A: ~D passed, ~D failed, ~D errors ---~%"
            suite-name pass fail errs)
    (when failures
      (format t "~&Failures:~%")
      (dolist (f (reverse failures))
        (format t "  ~A: ~A~%" (car f) (cdr f))))
    (values pass fail errs)))

(defun run-all-tests ()
  "Run all registered test suites. Exit with code 1 if any failures."
  (let ((total-pass 0) (total-fail 0) (total-err 0))
    (maphash (lambda (suite-name tests)
               (declare (ignore tests))
               (multiple-value-bind (p f e) (run-suite suite-name)
                 (incf total-pass p)
                 (incf total-fail f)
                 (incf total-err e)))
             *test-registry*)
    (format t "~&~%=== TOTAL: ~D passed, ~D failed, ~D errors ===~%"
            total-pass total-fail total-err)
    (if (or (> total-fail 0) (> total-err 0))
        (sb-ext:exit :code 1)
        (sb-ext:exit :code 0))))
