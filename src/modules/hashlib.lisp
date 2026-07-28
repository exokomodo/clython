;;;; modules/hashlib.lisp — hashlib built-in module
;;;;
;;;; Implements MD5, SHA1, SHA224, SHA256, SHA384, SHA512 via sb-md5 and openssl.

(in-package :clython.imports)

;;; ─── Internal helpers ─────────────────────────────────────────────────────

(defun %bytes-to-hex (vec)
  "Convert an octet vector to a lowercase hex string."
  (let ((result (make-string (* 2 (length vec)))))
    (loop for b across vec
          for i from 0 by 2
          do (let ((hex (format nil "~2,'0x" b)))
               (setf (char result i)       (char hex 0))
               (setf (char result (1+ i))  (char hex 1))))
    result))

(defun %openssl-hash (algo bytes)
  "Hash BYTES (octet vector) using 'openssl dgst -ALGO -hex'.
   Returns lowercase hex string."
  (let* ((bv (if (vectorp bytes)
                 bytes
                 (coerce bytes '(vector (unsigned-byte 8)))))
         (proc (sb-ext:run-program "/usr/bin/openssl"
                                   (list "dgst"
                                         (concatenate 'string "-" algo)
                                         "-hex")
                                   :input :stream
                                   :output :stream
                                   :error nil
                                   :wait nil))
         (in  (sb-ext:process-input  proc))
         (out (sb-ext:process-output proc)))
    (write-sequence bv in)
    (finish-output in)
    (close in)
    (sb-ext:process-wait proc)
    (let ((line (read-line out nil "")))
      ;; openssl outputs: "SHA2-256(stdin)= abcdef..." or "(stdin)= abcdef..."
      (let ((eq-pos (position #\= line)))
        (if eq-pos
            (string-downcase (string-trim " " (subseq line (1+ eq-pos))))
            "")))))

(defun %make-hash-obj (name hex-str)
  "Build a hash-object py-object with hexdigest(), digest(), update(), name."
  (let ((ht (make-hash-table :test #'equal)))
    ;; .hexdigest()
    (let ((h hex-str))
      (setf (gethash "hexdigest" ht)
            (clython.runtime:make-py-function
             :name "hexdigest"
             :cl-fn (lambda (&rest args)
                      (declare (ignore args))
                      (clython.runtime:make-py-str h)))))
    ;; .digest() — convert hex to bytes
    (let ((h hex-str))
      (setf (gethash "digest" ht)
            (clython.runtime:make-py-function
             :name "digest"
             :cl-fn (lambda (&rest args)
                      (declare (ignore args))
                      (let* ((n   (/ (length h) 2))
                             (arr (make-array n :element-type '(unsigned-byte 8))))
                        (loop for i below n
                              do (setf (aref arr i)
                                       (parse-integer h
                                                      :start (* i 2)
                                                      :end   (+ (* i 2) 2)
                                                      :radix 16)))
                        (clython.runtime:make-py-bytes arr))))))
    ;; .name
    (setf (gethash "name" ht) (clython.runtime:make-py-str name))
    ;; .update() — no-op stub (eager hashing)
    (setf (gethash "update" ht)
          (clython.runtime:make-py-function
           :name "update"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    clython.runtime:+py-none+)))
    ;; .copy() — returns a new identical object
    (let ((n name) (h hex-str))
      (setf (gethash "copy" ht)
            (clython.runtime:make-py-function
             :name "copy"
             :cl-fn (lambda (&rest args)
                      (declare (ignore args))
                      (%make-hash-obj n h)))))
    ;; Assemble py-object
    (let ((obj (make-instance 'clython.runtime:py-object)))
      (setf (clython.runtime:py-object-dict obj) ht)
      obj)))

(defun %get-bytes-data (py-arg)
  "Extract an octet vector from a py-bytes or py-str argument.
   Returns (vector (unsigned-byte 8))."
  (cond
    ((typep py-arg 'clython.runtime:py-bytes)
     (clython.runtime:py-bytes-value py-arg))
    ((typep py-arg 'clython.runtime:py-str)
     (let* ((s   (clython.runtime:py-str-value py-arg))
            (arr (make-array (length s) :element-type '(unsigned-byte 8))))
       (loop for c across s for i from 0
             do (setf (aref arr i) (char-code c)))
       arr))
    ((eq py-arg clython.runtime:+py-none+)
     (make-array 0 :element-type '(unsigned-byte 8)))
    (t
     (make-array 0 :element-type '(unsigned-byte 8)))))

(defun %md5-hex (bytes)
  "Compute MD5 of BYTES, returning lowercase hex string."
  (%openssl-hash "md5" bytes))

(defun %make-hash-constructor (algo-name hash-fn)
  "Return a py-function that constructs a hash object for ALGO-NAME using HASH-FN."
  (clython.runtime:make-py-function
   :name algo-name
   :cl-fn (lambda (&rest args)
            (let* ((data  (if args (first args) clython.runtime:+py-none+))
                   (bytes (%get-bytes-data data))
                   (hex   (funcall hash-fn bytes)))
              (%make-hash-obj algo-name hex)))))

;;; ─── new() factory ────────────────────────────────────────────────────────

(defun %make-new-fn ()
  "hashlib.new(name, data=b'') → hash object."
  (clython.runtime:make-py-function
   :name "new"
   :cl-fn (lambda (&rest args)
            (let* ((name-arg (first args))
                   (data-arg (if (cdr args) (second args) clython.runtime:+py-none+))
                   (name     (clython.runtime:py-str-value name-arg))
                   (bytes    (%get-bytes-data data-arg))
                   (hex      (cond
                               ((string= name "md5")    (%md5-hex bytes))
                               ((string= name "sha1")   (%openssl-hash "sha1"   bytes))
                               ((string= name "sha224") (%openssl-hash "sha224" bytes))
                               ((string= name "sha256") (%openssl-hash "sha256" bytes))
                               ((string= name "sha384") (%openssl-hash "sha384" bytes))
                               ((string= name "sha512") (%openssl-hash "sha512" bytes))
                               (t (clython.runtime:py-raise
                                   "ValueError" "unsupported hash type ~A" name)))))
              (%make-hash-obj name hex)))))

;;; ─── Module constructor ───────────────────────────────────────────────────

(defun make-hashlib-module ()
  "Create the hashlib built-in module."
  (let ((mod (clython.runtime:make-py-module "hashlib"))
        (d   nil))
    (setf d (clython.runtime:py-module-dict mod))

    (setf (gethash "md5"    d) (%make-hash-constructor "md5"
                                  (lambda (b) (%md5-hex b))))
    (setf (gethash "sha1"   d) (%make-hash-constructor "sha1"
                                  (lambda (b) (%openssl-hash "sha1"   b))))
    (setf (gethash "sha224" d) (%make-hash-constructor "sha224"
                                  (lambda (b) (%openssl-hash "sha224" b))))
    (setf (gethash "sha256" d) (%make-hash-constructor "sha256"
                                  (lambda (b) (%openssl-hash "sha256" b))))
    (setf (gethash "sha384" d) (%make-hash-constructor "sha384"
                                  (lambda (b) (%openssl-hash "sha384" b))))
    (setf (gethash "sha512" d) (%make-hash-constructor "sha512"
                                  (lambda (b) (%openssl-hash "sha512" b))))

    (setf (gethash "new" d) (%make-new-fn))

    ;; algorithms_available / algorithms_guaranteed
    (let ((algos (clython.runtime:make-py-set
                  (mapcar #'clython.runtime:make-py-str
                          '("md5" "sha1" "sha224" "sha256" "sha384" "sha512")))))
      (setf (gethash "algorithms_available" d) algos)
      (setf (gethash "algorithms_guaranteed" d) algos))

    (setf (gethash "__name__" d) (clython.runtime:make-py-str "hashlib"))
    mod))
