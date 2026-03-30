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
                        (clython.runtime:make-py-str result))))))
    mod))

;;;; ─── itertools module ─────────────────────────────────────────────────────

