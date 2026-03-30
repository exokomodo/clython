;;;; modules/json.lisp — json built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun %json-to-py (str)
  "Parse a JSON string and return a Python object."
  (let ((pos 0) (len (length str)))
    (labels
        ((%skip-ws ()
           (loop while (and (< pos len)
                            (member (char str pos) '(#\Space #\Tab #\Newline #\Return)))
                 do (incf pos)))
         (%peek ()
           (%skip-ws)
           (when (< pos len) (char str pos)))
         (%advance ()
           (let ((c (char str pos))) (incf pos) c))
         (%expect (c)
           (%skip-ws)
           (unless (and (< pos len) (char= (char str pos) c))
             (clython.runtime:py-raise "ValueError"
               (format nil "JSON parse error: expected ~C at pos ~D" c pos)))
           (incf pos))
         (%parse-string ()
           (%expect #\")
           (let ((buf (make-string-output-stream)))
             (loop
               (when (>= pos len)
                 (clython.runtime:py-raise "ValueError" "JSON: unterminated string"))
               (let ((c (%advance)))
                 (cond ((char= c #\") (return))
                       ((char= c #\\)
                        (let ((esc (%advance)))
                          (case esc
                            (#\n (write-char #\Newline buf))
                            (#\t (write-char #\Tab buf))
                            (#\r (write-char #\Return buf))
                            (#\" (write-char #\" buf))
                            (#\\ (write-char #\\ buf))
                            (#\/ (write-char #\/ buf))
                            (otherwise (write-char esc buf)))))
                       (t (write-char c buf)))))
             (get-output-stream-string buf)))
         (%parse-number ()
           (let ((start pos))
             (when (and (< pos len) (char= (char str pos) #\-)) (incf pos))
             (loop while (and (< pos len) (digit-char-p (char str pos))) do (incf pos))
             (let ((is-float nil))
               (when (and (< pos len) (char= (char str pos) #\.))
                 (setf is-float t) (incf pos)
                 (loop while (and (< pos len) (digit-char-p (char str pos))) do (incf pos)))
               (when (and (< pos len) (member (char str pos) '(#\e #\E)))
                 (setf is-float t) (incf pos)
                 (when (and (< pos len) (member (char str pos) '(#\+ #\-))) (incf pos))
                 (loop while (and (< pos len) (digit-char-p (char str pos))) do (incf pos)))
               (let ((numstr (subseq str start pos)))
                 (if is-float
                     (clython.runtime:make-py-float
                      (coerce (read-from-string numstr) 'double-float))
                     (clython.runtime:make-py-int (parse-integer numstr)))))))
         (%parse-array ()
           (%expect #\[)
           (%skip-ws)
           (if (and (< pos len) (char= (char str pos) #\]))
               (progn (incf pos)
                      (clython.runtime:make-py-list (make-array 0 :adjustable t :fill-pointer 0)))
               (let ((items '()))
                 (push (%parse-value) items)
                 (loop while (progn (%skip-ws) (and (< pos len) (char= (char str pos) #\,)))
                       do (incf pos) (push (%parse-value) items))
                 (%expect #\])
                 (clython.runtime:make-py-list
                  (make-array (length items) :initial-contents (nreverse items))))))
         (%parse-object ()
           (%expect #\{)
           (%skip-ws)
           (let ((d (make-hash-table :test #'equal)))
             (unless (and (< pos len) (char= (char str pos) #\}))
               (loop
                 (let ((key (%parse-string)))
                   (%expect #\:)
                   (setf (gethash key d) (%parse-value)))
                 (%skip-ws)
                 (if (and (< pos len) (char= (char str pos) #\,))
                     (incf pos)
                     (return))))
             (%expect #\})
             (clython.runtime:make-py-dict d)))
         (%parse-value ()
           (%skip-ws)
           (when (>= pos len)
             (clython.runtime:py-raise "ValueError" "JSON: unexpected end of input"))
           (let ((c (char str pos)))
             (cond
               ((char= c #\") (clython.runtime:make-py-str (%parse-string)))
               ((char= c #\{) (%parse-object))
               ((char= c #\[) (%parse-array))
               ((or (digit-char-p c) (char= c #\-)) (%parse-number))
               ((and (<= (+ pos 4) len) (string= (subseq str pos (+ pos 4)) "true"))
                (incf pos 4) clython.runtime:+py-true+)
               ((and (<= (+ pos 5) len) (string= (subseq str pos (+ pos 5)) "false"))
                (incf pos 5) clython.runtime:+py-false+)
               ((and (<= (+ pos 4) len) (string= (subseq str pos (+ pos 4)) "null"))
                (incf pos 4) clython.runtime:+py-none+)
               (t (clython.runtime:py-raise "ValueError"
                    (format nil "JSON: unexpected character ~C at pos ~D" c pos)))))))
      (%parse-value))))


(defun make-json-module ()
  "Create a stub json module with dumps and loads."
  (let ((mod (clython.runtime:make-py-module "json")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "json"))
    ;; json.dumps(obj)
    (setf (gethash "dumps" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "dumps"
           :cl-fn (lambda (obj &rest _kw) (declare (ignore _kw))
                    (clython.runtime:make-py-str (%py-to-json obj)))))
    ;; json.loads(s)
    (setf (gethash "loads" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "loads"
           :cl-fn (lambda (s &rest _kw) (declare (ignore _kw))
                    (%json-to-py (clython.runtime:py-str-value s)))))
    mod))

;;; ─── decimal module ─────────────────────────────────────────────────────────

