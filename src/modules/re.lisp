;;;; modules/re.lisp — re built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-re-module ()
  "Create a re module backed by cl-ppcre for real regex support."
  (let ((mod (clython.runtime:make-py-module "re")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "re"))
      ;; Flags (matching CPython re module values)
      (dolist (flag-pair '(("IGNORECASE" . 2) ("I" . 2)
                           ("MULTILINE" . 8) ("M" . 8)
                           ("DOTALL" . 16) ("S" . 16)
                           ("VERBOSE" . 64) ("X" . 64)
                           ("ASCII" . 256) ("A" . 256)
                           ("UNICODE" . 32) ("U" . 32)
                           ("LOCALE" . 4) ("L" . 4)
                           ("NOFLAG" . 0)))
        (setf (gethash (car flag-pair) d)
              (clython.runtime:make-py-int (cdr flag-pair))))
      ;; error exception class stub
      (setf (gethash "error" d)
            (clython.runtime:make-py-type :name "error"))

      ;; ── Pattern type ──────────────────────────────────────────────────────
      ;; A pattern object wraps a cl-ppcre scanner and exposes match/search/etc.
      (let* ((pattern-type (clython.runtime:make-py-type :name "Pattern"))
             (pattern-tdict (make-hash-table :test #'equal)))
        (setf (clython.runtime:py-type-dict pattern-type) pattern-tdict)

        ;; Helper: make a Pattern instance from a CL regex string
        (flet ((make-pattern (regex-str)
                 (let ((inst (make-instance 'clython.runtime:py-object
                                            :py-class pattern-type
                                            :py-dict (make-hash-table :test #'equal))))
                   (setf (gethash "__pattern__" (clython.runtime:py-object-dict inst))
                         regex-str)
                   inst))
               ;; Helper: make a Match object (non-None sentinel + group access)
               (make-match (whole-string start end groups)
                 (let* ((match-type (clython.runtime:make-py-type :name "Match"))
                        (inst (make-instance 'clython.runtime:py-object
                                             :py-class match-type
                                             :py-dict (make-hash-table :test #'equal))))
                   (setf (gethash "__whole__"  (clython.runtime:py-object-dict inst)) whole-string
                         (gethash "__start__"  (clython.runtime:py-object-dict inst)) start
                         (gethash "__end__"    (clython.runtime:py-object-dict inst)) end
                         (gethash "__groups__" (clython.runtime:py-object-dict inst)) groups)
                   ;; group(n=0) method
                   (let ((match-tdict (make-hash-table :test #'equal)))
                     (setf (clython.runtime:py-type-dict match-type) match-tdict)
                     (setf (gethash "group" match-tdict)
                           (clython.runtime:make-py-function
                            :name "group"
                            :cl-fn (lambda (&rest margs)
                                     ;; first arg is self (the match obj), optional second is group index
                                     (let* ((self (first margs))
                                            (n-obj (second margs))
                                            (n (if n-obj
                                                   (clython.runtime:py-int-value n-obj)
                                                   0))
                                            (d (clython.runtime:py-object-dict self))
                                            (w (gethash "__whole__"  d))
                                            (s (gethash "__start__"  d))
                                            (e (gethash "__end__"    d))
                                            (g (gethash "__groups__" d)))
                                       (if (= n 0)
                                           (clython.runtime:make-py-str (subseq w s e))
                                           (let ((gi (nth (1- n) g)))
                                             (if gi
                                                 (clython.runtime:make-py-str gi)
                                                 clython.runtime:+py-none+))))))))
                   inst))
               ;; Extract CL string from a py-str arg
               (arg-str (arg)
                 (if (typep arg 'clython.runtime:py-str)
                     (clython.runtime:py-str-value arg)
                     (error "re: expected str, got ~A" (type-of arg)))))

          ;; ── compile(pattern[, flags]) ──────────────────────────────────────
          (setf (gethash "compile" d)
                (clython.runtime:make-py-function
                 :name "compile"
                 :cl-fn (lambda (&rest args)
                          (let ((regex (arg-str (first args))))
                            (make-pattern regex)))))

          ;; ── match(pattern, string[, flags]) ───────────────────────────────
          (setf (gethash "match" d)
                (clython.runtime:make-py-function
                 :name "match"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (string (arg-str (second args)))
                                 ;; match anchors at start — use :start 0 and check pos
                                 (scanner (cl-ppcre:create-scanner (concatenate 'string "^(?:" regex ")"))))
                            (multiple-value-bind (ms me reg-starts reg-ends)
                                (cl-ppcre:scan scanner string)
                              (if ms
                                  (let ((groups
                                         (when reg-starts
                                           (loop for rs across reg-starts
                                                 for re across reg-ends
                                                 collect (if rs (subseq string rs re) nil)))))
                                    (make-match string ms me groups))
                                  clython.runtime:+py-none+))))))

          ;; ── search(pattern, string[, flags]) ──────────────────────────────
          (setf (gethash "search" d)
                (clython.runtime:make-py-function
                 :name "search"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (string (arg-str (second args))))
                            (multiple-value-bind (ms me reg-starts reg-ends)
                                (cl-ppcre:scan regex string)
                              (if ms
                                  (let ((groups
                                         (when reg-starts
                                           (loop for rs across reg-starts
                                                 for re across reg-ends
                                                 collect (if rs (subseq string rs re) nil)))))
                                    (make-match string ms me groups))
                                  clython.runtime:+py-none+))))))

          ;; ── fullmatch(pattern, string[, flags]) ───────────────────────────
          (setf (gethash "fullmatch" d)
                (clython.runtime:make-py-function
                 :name "fullmatch"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (string (arg-str (second args)))
                                 (scanner (cl-ppcre:create-scanner
                                           (concatenate 'string "^(?:" regex ")$"))))
                            (multiple-value-bind (ms me reg-starts reg-ends)
                                (cl-ppcre:scan scanner string)
                              (if ms
                                  (let ((groups
                                         (when reg-starts
                                           (loop for rs across reg-starts
                                                 for re across reg-ends
                                                 collect (if rs (subseq string rs re) nil)))))
                                    (make-match string ms me groups))
                                  clython.runtime:+py-none+))))))

          ;; ── sub(pattern, repl, string[, count, flags]) ────────────────────
          (setf (gethash "sub" d)
                (clython.runtime:make-py-function
                 :name "sub"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (repl   (arg-str (second args)))
                                 (string (arg-str (third args))))
                            (clython.runtime:make-py-str
                             (cl-ppcre:regex-replace-all regex string repl))))))

          ;; ── subn(pattern, repl, string[, count, flags]) ───────────────────
          (setf (gethash "subn" d)
                (clython.runtime:make-py-function
                 :name "subn"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (repl   (arg-str (second args)))
                                 (string (arg-str (third args)))
                                 (count  0)
                                 (result (cl-ppcre:regex-replace-all
                                          regex string
                                          (lambda (m &rest r)
                                            (declare (ignore r))
                                            (incf count)
                                            repl)
                                          :simple-calls t)))
                            (clython.runtime:make-py-tuple
                             (list (clython.runtime:make-py-str result)
                                   (clython.runtime:make-py-int count)))))))

          ;; ── findall(pattern, string[, flags]) ─────────────────────────────
          (setf (gethash "findall" d)
                (clython.runtime:make-py-function
                 :name "findall"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (string (arg-str (second args)))
                                 (matches '()))
                            (cl-ppcre:do-matches (ms me regex string)
                              (push (clython.runtime:make-py-str (subseq string ms me)) matches))
                            (clython.runtime:make-py-list (nreverse matches))))))

          ;; ── finditer(pattern, string[, flags]) ────────────────────────────
          (setf (gethash "finditer" d)
                (clython.runtime:make-py-function
                 :name "finditer"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (string (arg-str (second args)))
                                 (matches '()))
                            (cl-ppcre:do-matches (ms me regex string)
                              (push (make-match string ms me nil) matches))
                            (let ((items (nreverse matches)))
                              (clython.runtime:make-py-iterator
                               (lambda ()
                                 (if items
                                     (prog1 (pop items) )
                                     nil))))))))

          ;; ── split(pattern, string[, maxsplit, flags]) ─────────────────────
          (setf (gethash "split" d)
                (clython.runtime:make-py-function
                 :name "split"
                 :cl-fn (lambda (&rest args)
                          (let* ((regex  (arg-str (first args)))
                                 (string (arg-str (second args)))
                                 (parts  (cl-ppcre:split regex string)))
                            (clython.runtime:make-py-list
                             (mapcar #'clython.runtime:make-py-str parts)))))))))
    mod))

;;;; ─── functools module ──────────────────────────────────────────────────────

