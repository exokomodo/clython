(defsystem :clython-tests
  :description "Clython unit tests"
  :depends-on (:clython)
  :serial t
  :components ((:module "tests/unit"
                :components ((:file "test-framework")
                             (:file "test-grammar-coverage")))))
