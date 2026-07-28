;;;; modules/struct.lisp — struct built-in module
;;;;
;;;; Implements pack/unpack/calcsize for a subset of Python's struct format strings.

(in-package :clython.imports)

;;; ─── Format parser ────────────────────────────────────────────────────────

(defun %struct-parse-fmt (fmt)
  "Parse a struct format string into (endian . list-of-(type . count)) pairs.
   Returns (values endian items) where endian is :big, :little, or :native,
   and items is a list of (char . repeat-count) conses."
  (let* ((s (clython.runtime:py-str-value fmt))
         (i 0)
         (n (length s))
         (endian :native)
         items)
    ;; Check byte-order prefix
    (when (> n 0)
      (case (char s 0)
        (#\> (setf endian :big)    (incf i))
        (#\< (setf endian :little) (incf i))
        (#\! (setf endian :big)    (incf i))
        (#\= (setf endian :native) (incf i))
        (#\@ (setf endian :native) (incf i))))
    ;; Parse type codes with optional repeat counts
    (loop while (< i n) do
      (let ((c (char s i)))
        (cond
          ((digit-char-p c)
           ;; Accumulate digit(s)
           (let ((num 0))
             (loop while (and (< i n) (digit-char-p (char s i))) do
               (setf num (+ (* num 10) (digit-char-p (char s i))))
               (incf i))
             ;; Next char is the type
             (when (< i n)
               (push (cons (char s i) num) items)
               (incf i))))
          (t
           (push (cons c 1) items)
           (incf i)))))
    (values endian (nreverse items))))

(defun %struct-item-size (type-char)
  "Return the byte size of a single struct type character."
  (case type-char
    ((#\b #\B #\x #\c #\s #\p) 1)
    ((#\h #\H)                  2)
    ((#\i #\I #\l #\L #\f)     4)
    ((#\q #\Q #\d)              8)
    (t                          0)))

(defun %calcsize-items (items)
  "Sum the byte size of all (type . count) items."
  (loop for (tc . cnt) in items
        sum (* cnt (%struct-item-size tc))))

;;; ─── Packing ──────────────────────────────────────────────────────────────

(defun %write-uint (vec offset value nbytes big-endian-p)
  "Write VALUE as an N-byte unsigned integer into VEC at OFFSET."
  (let ((v (if (minusp value)
               (+ value (ash 1 (* nbytes 8)))
               value)))
    (if big-endian-p
        (loop for b from (1- nbytes) downto 0
              do (setf (aref vec (+ offset b))
                       (ldb (byte 8 (* (- nbytes 1 b) 8)) v)))
        (loop for b from 0 below nbytes
              do (setf (aref vec (+ offset b))
                       (ldb (byte 8 (* b 8)) v))))))

(defun %pack-item (vec offset tc count values-list pos big-p)
  "Pack COUNT values of type TC into VEC at OFFSET. Returns new offset and new pos."
  (let ((sz (%struct-item-size tc)))
    (loop repeat count
          do
          (let ((v (nth pos values-list)))
            (case tc
              (#\x ; padding
               (setf (aref vec offset) 0))
              ((#\b #\B) ; signed/unsigned byte
               (let ((n (clython.runtime:py->cl v)))
                 (setf (aref vec offset)
                       (ldb (byte 8 0) n))))
              ((#\h #\H) ; signed/unsigned short
               (let ((n (clython.runtime:py->cl v)))
                 (%write-uint vec offset n 2 big-p)))
              ((#\i #\I #\l #\L) ; signed/unsigned int/long
               (let ((n (clython.runtime:py->cl v)))
                 (%write-uint vec offset n 4 big-p)))
              ((#\q #\Q) ; signed/unsigned long long
               (let ((n (clython.runtime:py->cl v)))
                 (%write-uint vec offset n 8 big-p)))
              (#\f ; float (4 bytes) — approximate via double
               (let* ((n (coerce (clython.runtime:py->cl v) 'single-float))
                      (bits #+sbcl (sb-kernel:single-float-bits n)
                            #-sbcl 0))
                 (%write-uint vec offset bits 4 big-p)))
              (#\d ; double (8 bytes)
               (let* ((n (coerce (clython.runtime:py->cl v) 'double-float))
                      (bits #+sbcl (sb-kernel:double-float-bits n)
                            #-sbcl 0))
                 (%write-uint vec offset bits 8 big-p)))
              ((#\c #\s) ; char/bytes — take first byte
               (let ((bv (cond
                           ((typep v 'clython.runtime:py-bytes)
                            (clython.runtime:py-bytes-value v))
                           ((typep v 'clython.runtime:py-str)
                            (let* ((s (clython.runtime:py-str-value v))
                                   (a (make-array (length s)
                                                  :element-type '(unsigned-byte 8))))
                              (loop for c across s for i from 0
                                    do (setf (aref a i) (char-code c)))
                              a))
                           (t (vector 0)))))
                 (setf (aref vec offset) (if (> (length bv) 0) (aref bv 0) 0)))))
            (unless (char= tc #\x)
              (incf pos)))
          (incf offset sz))
    (values offset pos)))

(defun %struct-pack (fmt values-list)
  "Pack VALUES-LIST according to FMT, returning an octet vector."
  (multiple-value-bind (endian items) (%struct-parse-fmt fmt)
    (let* ((size (%calcsize-items items))
           (vec  (make-array size :element-type '(unsigned-byte 8) :initial-element 0))
           (big-p (eq endian :big))
           (offset 0)
           (pos    0))
      (dolist (item items)
        (let ((tc (car item))
              (cnt (cdr item)))
          (multiple-value-setq (offset pos)
            (%pack-item vec offset tc cnt values-list pos big-p))))
      vec)))

;;; ─── Unpacking ────────────────────────────────────────────────────────────

(defun %read-uint (vec offset nbytes big-p)
  "Read an N-byte unsigned integer from VEC at OFFSET."
  (if big-p
      (loop for b from 0 below nbytes
            sum (ash (aref vec (+ offset b)) (* 8 (- nbytes 1 b))))
      (loop for b from 0 below nbytes
            sum (ash (aref vec (+ offset b)) (* 8 b)))))

(defun %to-signed (n nbytes)
  "Reinterpret unsigned N as signed for NBYTES-wide integers."
  (let ((max-unsigned (ash 1 (* nbytes 8))))
    (if (>= n (ash max-unsigned -1))
        (- n max-unsigned)
        n)))

(defun %unpack-item (vec offset tc count big-p)
  "Unpack COUNT items of type TC from VEC at OFFSET. Returns (values results new-offset)."
  (let ((sz (%struct-item-size tc))
        results)
    (loop repeat count do
      (let ((val
              (case tc
                (#\x clython.runtime:+py-none+)  ; padding — skip
                (#\B (clython.runtime:make-py-int (%read-uint vec offset 1 big-p)))
                (#\b (clython.runtime:make-py-int (%to-signed (%read-uint vec offset 1 big-p) 1)))
                (#\H (clython.runtime:make-py-int (%read-uint vec offset 2 big-p)))
                (#\h (clython.runtime:make-py-int (%to-signed (%read-uint vec offset 2 big-p) 2)))
                ((#\I #\L) (clython.runtime:make-py-int (%read-uint vec offset 4 big-p)))
                ((#\i #\l) (clython.runtime:make-py-int (%to-signed (%read-uint vec offset 4 big-p) 4)))
                (#\Q (clython.runtime:make-py-int (%read-uint vec offset 8 big-p)))
                (#\q (clython.runtime:make-py-int (%to-signed (%read-uint vec offset 8 big-p) 8)))
                (#\f
                 (let ((bits (%read-uint vec offset 4 big-p)))
                   (clython.runtime:make-py-float
                    (coerce #+sbcl (sb-kernel:make-single-float bits)
                            #-sbcl 0.0
                            'double-float))))
                (#\d
                 (let ((bits (%read-uint vec offset 8 big-p)))
                   (clython.runtime:make-py-float
                    #+sbcl (sb-kernel:make-double-float
                            (ldb (byte 32 32) bits)
                            (ldb (byte 32 0)  bits))
                    #-sbcl 0.0d0)))
                ((#\c #\s)
                 (clython.runtime:make-py-bytes
                  (vector (aref vec offset))))
                (t clython.runtime:+py-none+))))
        (unless (char= tc #\x)
          (push val results)))
      (incf offset sz))
    (values (nreverse results) offset)))

(defun %struct-unpack (fmt buf-bytes)
  "Unpack BUF-BYTES according to FMT, returning a list of py-objects."
  (multiple-value-bind (endian items) (%struct-parse-fmt fmt)
    (let ((big-p  (eq endian :big))
          (offset 0)
          all-results)
      (dolist (item items)
        (let ((tc  (car item))
              (cnt (cdr item)))
          (multiple-value-bind (results new-offset)
              (%unpack-item buf-bytes offset tc cnt big-p)
            (setf all-results (append all-results results))
            (setf offset new-offset))))
      all-results)))

;;; ─── Module constructor ───────────────────────────────────────────────────

(defun make-struct-module ()
  "Create the struct built-in module."
  (let ((mod (clython.runtime:make-py-module "struct"))
        (d   nil))
    (setf d (clython.runtime:py-module-dict mod))

    ;; struct.calcsize(fmt) → int
    (setf (gethash "calcsize" d)
          (clython.runtime:make-py-function
           :name "calcsize"
           :cl-fn (lambda (fmt)
                    (multiple-value-bind (endian items) (%struct-parse-fmt fmt)
                      (declare (ignore endian))
                      (clython.runtime:make-py-int
                       (%calcsize-items items))))))

    ;; struct.pack(fmt, *values) → bytes
    (setf (gethash "pack" d)
          (clython.runtime:make-py-function
           :name "pack"
           :cl-fn (lambda (fmt &rest values)
                    (clython.runtime:make-py-bytes
                     (%struct-pack fmt values)))))

    ;; struct.unpack(fmt, buffer) → tuple
    (setf (gethash "unpack" d)
          (clython.runtime:make-py-function
           :name "unpack"
           :cl-fn (lambda (fmt buf)
                    (let ((bv (cond
                                ((typep buf 'clython.runtime:py-bytes)
                                 (clython.runtime:py-bytes-value buf))
                                ((typep buf 'clython.runtime:py-str)
                                 (let* ((s (clython.runtime:py-str-value buf))
                                        (a (make-array (length s)
                                                       :element-type '(unsigned-byte 8))))
                                   (loop for c across s for i from 0
                                         do (setf (aref a i) (char-code c)))
                                   a))
                                (t (vector)))))
                      (clython.runtime:make-py-tuple
                       (%struct-unpack fmt bv))))))

    ;; struct.pack_into(fmt, buf, offset, *values) — stub
    (setf (gethash "pack_into" d)
          (clython.runtime:make-py-function
           :name "pack_into"
           :cl-fn (lambda (&rest args)
                    (declare (ignore args))
                    clython.runtime:+py-none+)))

    ;; struct.unpack_from(fmt, buf, offset=0) — single-item unpack from offset
    (setf (gethash "unpack_from" d)
          (clython.runtime:make-py-function
           :name "unpack_from"
           :cl-fn (lambda (fmt buf &rest rest)
                    (declare (ignore rest))
                    (let ((bv (if (typep buf 'clython.runtime:py-bytes)
                                  (clython.runtime:py-bytes-value buf)
                                  (vector))))
                      (clython.runtime:make-py-tuple
                       (%struct-unpack fmt bv))))))

    (setf (gethash "__name__" d) (clython.runtime:make-py-str "struct"))
    mod))
