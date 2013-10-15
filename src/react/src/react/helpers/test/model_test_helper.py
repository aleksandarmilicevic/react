from react.api.metamodel import ReactObjMClass

class ModelTestHelper:
    def assert_record_cls(self, record_cls, meta_cls, *fld_names, **fields):
        self.assertTrue(record_cls)
        self.assertEqual(ReactObjMClass, record_cls.__metaclass__)
        r = record_cls()
        self.assertEqual(record_cls.meta(), r.meta(), "class and instance meta() different")
        meta = r.meta()
        self.assertTrue(isinstance(meta, meta_cls), 
                        "%s is not an instance of %s" % (record_cls.meta(), meta_cls))
        self.assertEqual(record_cls, meta.obj_type())
        self.assertEqual(record_cls.__name__, meta.name())

        if len(fld_names) > 0: self.assertEqual(len(fld_names), len(meta.fields())) 
        for fname in fld_names:
            self.assertTrue(fname in meta.fields())

        if len(fields) > 0: self.assertEqual(len(fields), len(meta.fields())) 
        for fname in fields:
            self.assertTrue(fname in meta.fields())
            self.assertEqual(str(fields[fname]), str(meta.fields()[fname]))

    def assert_rec_cls(self, *args, **kwargs): self.assert_record_cls(*args, **kwargs)
