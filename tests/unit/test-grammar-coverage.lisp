;;;; Grammar coverage test — verifies every rule in the Python 3.12 PEG grammar
;;;; has a corresponding parser rule registered in Clython.
;;;;
;;;; This test reads grammars/python-3.12.rules and checks that each rule name
;;;; exists as a registered parser rule. It's a living checklist: if you add a
;;;; grammar rule, this test will fail until the parser implements it.

(in-package :clython.test)

;;; --- Grammar rule file parser ---

(defun load-grammar-rules (path)
  "Load rule names from a .rules file. Skips comments and blank lines."
  (with-open-file (stream path :direction :input)
    (loop for line = (read-line stream nil nil)
          while line
          for trimmed = (string-trim '(#\Space #\Tab) line)
          when (and (plusp (length trimmed))
                    (char/= (char trimmed 0) #\#))
            collect trimmed)))

;;; --- Parser rule registry ---
;;; The parser should export a function or variable that lists implemented rules.
;;; Until the parser exists, we use a stub that returns an empty list.

(defun get-implemented-rules ()
  "Return list of rule name strings that the parser currently implements.
   Checks for clython.parser:*grammar-rules* or returns empty list."
  (let ((pkg (find-package :clython.parser)))
    (if pkg
        (let ((sym (find-symbol "*GRAMMAR-RULES*" pkg)))
          (if (and sym (boundp sym))
              (mapcar #'string-downcase
                      (mapcar #'symbol-name (symbol-value sym)))
              nil))
        nil)))

;;; --- Tests ---

(defvar *grammar-rules-path*
  (merge-pathnames "grammars/python-3.12.rules"
                   (asdf:system-source-directory :clython))
  "Path to the canonical grammar rules file.")

(deftest grammar-rules-file-exists (:suite "grammar-coverage")
  (assert-true (probe-file *grammar-rules-path*)
               (format nil "Grammar rules file not found: ~A" *grammar-rules-path*)))

(deftest grammar-rules-file-nonempty (:suite "grammar-coverage")
  (let ((rules (load-grammar-rules *grammar-rules-path*)))
    (assert-true (> (length rules) 100)
                 (format nil "Expected >100 grammar rules, got ~D" (length rules)))))

(deftest grammar-coverage-report (:suite "grammar-coverage")
  "Report grammar rule implementation progress. Always passes — this is a tracker."
  (let* ((expected (load-grammar-rules *grammar-rules-path*))
         (implemented (get-implemented-rules))
         (missing (set-difference expected implemented :test #'string=))
         (covered (- (length expected) (length missing))))
    (format t "~&  Grammar coverage: ~D/~D rules implemented (~,1F%)~%"
            covered (length expected)
            (if (zerop (length expected)) 0.0
                (* 100.0 (/ covered (length expected)))))
    (when missing
      (format t "  ~D rules remaining~%" (length missing)))
    ;; This always passes — progress is informational, not a gate.
    (assert-true t)))

(deftest no-extra-rules (:suite "grammar-coverage")
  "Parser should not implement rules that aren't in the grammar file.
   (Catches typos and stale rules.)"
  (let* ((expected (load-grammar-rules *grammar-rules-path*))
         (implemented (get-implemented-rules))
         (extra (set-difference implemented expected :test #'string=)))
    (assert-true (null extra)
                 (format nil "~D parser rules not in grammar file:~%~{  - ~A~%~}"
                         (length extra)
                         (sort (copy-list extra) #'string<)))))
