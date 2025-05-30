
        rule DummyExample {
            strings:
                $a = "malicious"
            condition:
                $a
        }