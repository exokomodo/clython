;;;; modules/string.lisp — string built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-string-module ()
  "Create a string module with ASCII constants and capwords."
  (let ((mod (clython.runtime:make-py-module "string")))
    (let ((d (clython.runtime:py-module-dict mod)))
      (setf (gethash "__name__" d) (clython.runtime:make-py-str "string"))
      (setf (gethash "ascii_lowercase" d)
            (clython.runtime:make-py-str "abcdefghijklmnopqrstuvwxyz"))
      (setf (gethash "ascii_uppercase" d)
            (clython.runtime:make-py-str "ABCDEFGHIJKLMNOPQRSTUVWXYZ"))
      (setf (gethash "ascii_letters" d)
            (clython.runtime:make-py-str "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"))
      (setf (gethash "digits" d)
            (clython.runtime:make-py-str "0123456789"))
      (setf (gethash "hexdigits" d)
            (clython.runtime:make-py-str "0123456789abcdefABCDEF"))
      (setf (gethash "octdigits" d)
            (clython.runtime:make-py-str "01234567"))
      (setf (gethash "punctuation" d)
            (clython.runtime:make-py-str "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"))
      (setf (gethash "whitespace" d)
            (clython.runtime:make-py-str (format nil " ~C~C~C~C~C"
                                                 #\Tab #\Newline #\Return
                                                 (code-char 11) (code-char 12))))
      (setf (gethash "printable" d)
            (clython.runtime:make-py-str
             (with-output-to-string (s)
               (dotimes (i 128)
                 (let ((c (code-char i)))
                   (when (or (alphanumericp c)
                             (member c '(#\Space #\! #\" #\# #\$ #\% #\& #\' #\( #\) #\* #\+
                                        #\, #\- #\. #\/ #\: #\; #\< #\= #\> #\? #\@ #\[ #\\
                                        #\] #\^ #\_ #\` #\{ #\| #\} #\~ #\Tab #\Newline
                                        #\Return (code-char 11) (code-char 12))))
                     (write-char c s)))))))
      ;; capwords(s, sep=None)
      (setf (gethash "capwords" d)
            (clython.runtime:make-py-function
             :name "capwords"
             :cl-fn (lambda (&rest args)
                      (let* ((s (clython.runtime:py-str-value (first args)))
                             (sep (if (and (second args)
                                          (not (eq (second args) clython.runtime:+py-none+)))
                                      (clython.runtime:py-str-value (second args))
                                      nil))
                             (words (if sep
                                        (uiop:split-string s :separator sep)
                                        (uiop:split-string
                                         (string-trim '(#\Space #\Tab #\Newline #\Return) s)
                                         :separator " ")))
                             (result (format nil "~{~A~^ ~}"
                                             (mapcar (lambda (w)
                                                       (if (string= w "") w
                                                           (concatenate 'string
                                                                        (string (char-upcase (char w 0)))
                                                                        (string-downcase (subseq w 1)))))
                                                     words))))
                        (clython.runtime:make-py-str result)))))

      ;; Formatter() — class that exposes a format() method with named-arg support
      (setf (gethash "Formatter" d)
            (clython.runtime:make-py-function
             :name "Formatter"
             :cl-fn (lambda (&rest _args)
                      (declare (ignore _args))
                      (let* ((fmt-type (clython.runtime:make-py-type :name "Formatter"))
                             (obj (make-instance 'clython.runtime:py-object
                                                 :py-class fmt-type
                                                 :py-dict (make-hash-table :test #'equal))))
                        (setf (gethash "format" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-function
                               :name "format"
                               :cl-fn (lambda (&rest call-args)
                                        (let* ((fmt-str (clython.runtime:py-str-value (first call-args)))
                                               (pos-args (rest call-args))
                                               (kwargs clython.runtime:*current-kwargs*)
                                               (buf (make-array 0 :element-type 'character
                                                                :fill-pointer 0 :adjustable t))
                                               (i 0)
                                               (auto-idx 0)
                                               (slen (length fmt-str)))
                                          (loop while (< i slen) do
                                            (let ((c (char fmt-str i)))
                                              (cond
                                                ;; Escaped {{ → {
                                                ((and (char= c #\{) (< (1+ i) slen)
                                                      (char= (char fmt-str (1+ i)) #\{))
                                                 (vector-push-extend #\{ buf)
                                                 (incf i 2))
                                                ;; Escaped }} → }
                                                ((and (char= c #\}) (< (1+ i) slen)
                                                      (char= (char fmt-str (1+ i)) #\}))
                                                 (vector-push-extend #\} buf)
                                                 (incf i 2))
                                                ;; Format field {spec}
                                                ((char= c #\{)
                                                 (let ((close (position #\} fmt-str :start (1+ i))))
                                                   (if close
                                                       (let* ((spec (subseq fmt-str (1+ i) close))
                                                              ;; Strip :format-spec
                                                              (colon (position #\: spec))
                                                              (field (if colon (subseq spec 0 colon) spec))
                                                              (val (cond
                                                                     ;; {} — auto-positional
                                                                     ((string= field "")
                                                                      (prog1 (nth auto-idx pos-args)
                                                                        (incf auto-idx)))
                                                                     ;; {N} — explicit positional
                                                                     ((ignore-errors (parse-integer field))
                                                                      (nth (parse-integer field) pos-args))
                                                                     ;; {name} — keyword arg
                                                                     (t
                                                                      (let ((pair (assoc field kwargs :test #'string=)))
                                                                        (if pair
                                                                            (cdr pair)
                                                                            (clython.runtime:py-raise
                                                                             "KeyError" field)))))))
                                                         (when val
                                                           (loop for ch across (clython.runtime:py-str-of val)
                                                                 do (vector-push-extend ch buf)))
                                                         (setf i (1+ close)))
                                                       (progn (vector-push-extend c buf) (incf i)))))
                                                (t
                                                 (vector-push-extend c buf)
                                                 (incf i)))))
                                          (clython.runtime:make-py-str (coerce buf 'string))))))
                        obj))))

      ;; Template(template) — $-style string substitution
      (setf (gethash "Template" d)
            (clython.runtime:make-py-function
             :name "Template"
             :cl-fn (lambda (&rest tmpl-args)
                      (let* ((tmpl-str (clython.runtime:py-str-value (first tmpl-args)))
                             (tmpl-type (clython.runtime:make-py-type :name "Template"))
                             (obj (make-instance 'clython.runtime:py-object
                                                 :py-class tmpl-type
                                                 :py-dict (make-hash-table :test #'equal))))
                        (setf (gethash "template" (clython.runtime:py-object-dict obj))
                              (clython.runtime:make-py-str tmpl-str))

                        (flet ((do-substitute (kwargs raise-on-missing)
                                 ;; Walk tmpl-str, replace $id or ${id} with kwargs values.
                                 (let ((buf (make-array 0 :element-type 'character
                                                        :fill-pointer 0 :adjustable t))
                                       (i 0)
                                       (slen (length tmpl-str)))
                                   (loop while (< i slen) do
                                     (let ((c (char tmpl-str i)))
                                       (cond
                                         ;; Escaped $$  → single $
                                         ((and (char= c #\$) (< (1+ i) slen)
                                               (char= (char tmpl-str (1+ i)) #\$))
                                          (vector-push-extend #\$ buf)
                                          (incf i 2))
                                         ;; ${identifier}
                                         ((and (char= c #\$) (< (1+ i) slen)
                                               (char= (char tmpl-str (1+ i)) #\{))
                                          (let ((close (position #\} tmpl-str :start (+ i 2))))
                                            (if close
                                                (let* ((key (subseq tmpl-str (+ i 2) close))
                                                       (pair (assoc key kwargs :test #'string=)))
                                                  (if pair
                                                      (loop for ch across (clython.runtime:py-str-of (cdr pair))
                                                            do (vector-push-extend ch buf))
                                                      (if raise-on-missing
                                                          (clython.runtime:py-raise "KeyError" key)
                                                          (progn
                                                            (loop for ch across (subseq tmpl-str i (1+ close))
                                                                  do (vector-push-extend ch buf)))))
                                                  (setf i (1+ close)))
                                                (progn (vector-push-extend c buf) (incf i)))))
                                         ;; $identifier
                                         ((and (char= c #\$) (< (1+ i) slen)
                                               (let ((nc (char tmpl-str (1+ i))))
                                                 (or (alpha-char-p nc) (char= nc #\_))))
                                          ;; Collect identifier chars
                                          (let ((j (1+ i)))
                                            (loop while (and (< j slen)
                                                             (let ((nc (char tmpl-str j)))
                                                               (or (alphanumericp nc) (char= nc #\_))))
                                                  do (incf j))
                                            (let* ((key (subseq tmpl-str (1+ i) j))
                                                   (pair (assoc key kwargs :test #'string=)))
                                              (if pair
                                                  (loop for ch across (clython.runtime:py-str-of (cdr pair))
                                                        do (vector-push-extend ch buf))
                                                  (if raise-on-missing
                                                      (clython.runtime:py-raise "KeyError" key)
                                                      (progn
                                                        (loop for ch across (subseq tmpl-str i j)
                                                              do (vector-push-extend ch buf)))))
                                              (setf i j))))
                                         (t
                                          (vector-push-extend c buf)
                                          (incf i)))))
                                   (clython.runtime:make-py-str (coerce buf 'string)))))

                          (setf (gethash "substitute" (clython.runtime:py-object-dict obj))
                                (clython.runtime:make-py-function
                                 :name "substitute"
                                 :cl-fn (lambda (&rest _sa)
                                          (declare (ignore _sa))
                                          (do-substitute clython.runtime:*current-kwargs* t))))

                          (setf (gethash "safe_substitute" (clython.runtime:py-object-dict obj))
                                (clython.runtime:make-py-function
                                 :name "safe_substitute"
                                 :cl-fn (lambda (&rest _sa)
                                          (declare (ignore _sa))
                                          (do-substitute clython.runtime:*current-kwargs* nil)))))
                        obj)))))
    mod))

;;;; ─── itertools module ─────────────────────────────────────────────────────

