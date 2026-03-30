(defsystem :clython
  :description "A Python interpreter implemented in Common Lisp"
  :version "0.1.0"
  :license "CC0-1.0"
  :depends-on (:cl-ppcre)
  :serial t
  :components ((:module "src"
                :components ((:file "ast")
                             (:file "lexer")
                             (:file "parser")
                             (:file "runtime")
                             (:file "builtins")
                             (:file "exceptions")
                             (:file "scope")
                             (:file "imports-pkg")
                             ;; Built-in module implementations — one file per module.
                             ;; To add a new module: create src/modules/<name>.lisp,
                             ;; define make-<name>-module, then register it in
                             ;; imports.lisp's register-builtin-modules.
                             (:module "modules"
                              :components ((:file "sys")
                                           (:file "builtins_module")
                                           (:file "math")
                                           (:file "asyncio")
                                           (:file "os")
                                           (:file "json")
                                           (:file "decimal")
                                           (:file "fractions")
                                           (:file "collections")
                                           (:file "keyword")
                                           (:file "string")
                                           (:file "itertools")
                                           (:file "re")
                                           (:file "functools")
                                           (:file "io")
                                           (:file "random")))
                             (:file "imports")
                             (:file "eval")
                             (:file "clython")
                             (:file "cli")))))
