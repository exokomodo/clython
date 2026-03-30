;;;; imports-pkg.lisp — package and variable declarations for clython.imports
;;;;
;;;; Loaded before src/modules/ so all module files can (in-package :clython.imports).

;;;; imports.lisp — Python import system for Clython
;;;;
;;;; Implements module finding, loading, and caching. Supports:
;;;; - Built-in module stubs (sys, _io, builtins, _thread, _signal)
;;;; - Loading pure-Python stdlib modules from CPython's stdlib
;;;; - Module caching to avoid re-evaluation
;;;; - Circular import guards

(defpackage :clython.imports
  (:use :cl)
  (:export
   #:import-module
   #:*module-registry*
   #:*sys-path*
   #:*builtin-modules*
   #:*eval-source-fn*
   #:initialize-import-system))

(in-package :clython.imports)
