(defsystem :clython
  :description "A Python interpreter implemented in Common Lisp"
  :version "0.1.0"
  :license "CC0-1.0"
  :depends-on ()
  :serial t
  :components ((:module "src"
                :components ((:file "ast")
                             (:file "lexer")
                             (:file "parser")
                             (:file "runtime")
                             (:file "builtins")
                             (:file "exceptions")
                             (:file "scope")
                             (:file "imports")
                             (:file "eval")
                             (:file "clython")
                             (:file "cli")))))
