class ModelTestHelper:
    def assert_record_cls(self, record_cls, meta_cls):
        self.assertTrue(record_cls)
        self.assertEqual(meta_cls, record_cls.__metaclass__)
        r = record_cls()
        self.assertEqual(meta_cls, r.meta())
