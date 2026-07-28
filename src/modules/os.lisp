;;;; modules/os.lisp — os built-in module
;;;;
;;;; Part of Clython's built-in module registry.
;;;; To add a new module: create a file here, define make-X-module,
;;;; then register it in imports.lisp's register-builtin-modules.

(in-package :clython.imports)

(defun make-os-path-module ()
  "Create a stub os.path module with join."
  (let ((mod (clython.runtime:make-py-module "os.path")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "os.path"))
    ;; os.path.join(*parts)
    (setf (gethash "join" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "join"
           :cl-fn (lambda (&rest parts)
                    (clython.runtime:make-py-str
                     (format nil "~{~A~^/~}"
                             (mapcar #'clython.runtime:py->cl parts))))))
    ;; os.path.exists(path) — checks actual filesystem
    (setf (gethash "exists" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "exists"
           :cl-fn (lambda (p)
                    (clython.runtime:py-bool-from-cl
                     (not (null (probe-file (clython.runtime:py-str-value p))))))))
    ;; os.path.sep — path separator ('/' on Unix, '\\' on Windows)
    (setf (gethash "sep" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str
           (string #+windows #\\ #-windows #\/)))
    ;; os.path.dirname(path)
    (setf (gethash "dirname" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "dirname"
           :cl-fn (lambda (p)
                    (let* ((s (clython.runtime:py-str-value p))
                           (pos (or (position #\/ s :from-end t)
                                   (position #\\ s :from-end t))))
                      (clython.runtime:make-py-str
                       (if pos (subseq s 0 pos) ""))))))
    ;; os.path.basename(path)
    (setf (gethash "basename" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "basename"
           :cl-fn (lambda (p)
                    (let* ((s (clython.runtime:py-str-value p))
                           (pos (or (position #\/ s :from-end t)
                                   (position #\\ s :from-end t))))
                      (clython.runtime:make-py-str
                       (if pos (subseq s (1+ pos)) s))))))
    ;; os.path.splitext(path) → (root, ext)  e.g. ("foo.tar", ".gz")
    (setf (gethash "splitext" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "splitext"
           :cl-fn (lambda (p)
                    (let* ((s (clython.runtime:py-str-value p))
                           ;; find last dot AFTER any slash (base only)
                           (slash-pos (or (position #\/ s :from-end t)
                                         (position #\\ s :from-end t)))
                           (base-start (if slash-pos (1+ slash-pos) 0))
                           (dot-pos (position #\. s :from-end t :start base-start)))
                      (if dot-pos
                          (clython.runtime:make-py-tuple
                           (list (clython.runtime:make-py-str (subseq s 0 dot-pos))
                                 (clython.runtime:make-py-str (subseq s dot-pos))))
                          (clython.runtime:make-py-tuple
                           (list p (clython.runtime:make-py-str ""))))))))
    ;; os.path.isfile(path) — true if path exists and is a regular file (not a dir)
    (setf (gethash "isfile" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "isfile"
           :cl-fn (lambda (p)
                    (let* ((s (clython.runtime:py-str-value p))
                           (pf (probe-file s)))
                      (clython.runtime:py-bool-from-cl
                       (and pf (pathname-name pf) t))))))
    ;; os.path.isdir(path) — true if path exists and is a directory
    (setf (gethash "isdir" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "isdir"
           :cl-fn (lambda (p)
                    (let* ((s (clython.runtime:py-str-value p))
                           ;; Ensure trailing slash so probe-file sees directory
                           (dir-s (if (or (string= s "") (member (char s (1- (length s)))
                                                                  '(#\/ #\\)))
                                      s
                                      (concatenate 'string s "/")))
                           (pf (probe-file dir-s)))
                      (clython.runtime:py-bool-from-cl
                       (and pf (not (pathname-name pf)) t))))))

    ;; os.path.abspath(path) — resolve relative to CWD
    (setf (gethash "abspath" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "abspath"
           :cl-fn (lambda (p)
                    (clython.runtime:make-py-str
                     (namestring
                      (merge-pathnames (clython.runtime:py-str-value p)
                                       *default-pathname-defaults*))))))
    mod))

(defun make-os-module ()
  "Create a stub os module."
  (let ((mod (clython.runtime:make-py-module "os")))
    (setf (gethash "__name__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "os"))
    ;; __file__ — CPython sets this to the .py path; stub with the module name
    (setf (gethash "__file__" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-str "os.py"))
    ;; os.path submodule
    (let ((path-mod (make-os-path-module)))
      (setf (gethash "path" (clython.runtime:py-module-dict mod)) path-mod)
      ;; Also register os.path in the module registry
      (setf (gethash "os.path" *module-registry*) path-mod))
    ;; os.getcwd()
    (setf (gethash "getcwd" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "getcwd"
           :cl-fn (lambda ()
                    (clython.runtime:make-py-str
                     (namestring (uiop:getcwd))))))
    ;; os.sep / os.linesep / os.devnull
    (setf (gethash "sep"     (clython.runtime:py-module-dict mod)) (clython.runtime:make-py-str "/"))
    (setf (gethash "linesep" (clython.runtime:py-module-dict mod)) (clython.runtime:make-py-str (string #\newline)))
    (setf (gethash "devnull" (clython.runtime:py-module-dict mod)) (clython.runtime:make-py-str "/dev/null"))
    ;; os.environ — a dict-like view of the process environment
    (let ((env-dict (clython.runtime:make-py-dict)))
      ;; sb-ext:posix-environ returns "KEY=VAL" strings
      (loop for entry in #+sbcl (sb-ext:posix-environ) #-sbcl '()
            for eq-pos = (position #\= entry)
            when eq-pos
            ;; dict-hash-key converts py-str → CL string; store under CL string directly
            do (setf (gethash (subseq entry 0 eq-pos)
                              (clython.runtime:py-dict-value env-dict))
                     (clython.runtime:make-py-str (subseq entry (1+ eq-pos)))))
      (setf (gethash "environ" (clython.runtime:py-module-dict mod)) env-dict))
    ;; os.getenv(key[, default]) — convenience wrapper
    (setf (gethash "getenv" (clython.runtime:py-module-dict mod))
          (clython.runtime:make-py-function
           :name "getenv"
           :cl-fn (lambda (&rest args)
                    (let* ((key (clython.runtime:py-str-value (first args)))
                           (default (if (>= (length args) 2) (second args) clython.runtime:+py-none+))
                           (val (uiop:getenv key)))
                      (if val (clython.runtime:make-py-str val) default)))))
    mod))

;;; ─── json module ────────────────────────────────────────────────────────────

