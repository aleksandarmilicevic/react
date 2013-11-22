import react
from react.api.metamodel import ReactObjMClass
from react import meta
from react import db

class ModelTestHelper:
    def assert_rec_cls(self, rec_cls, meta_cls, *fld_names, **fields):
        # check if __metaclass__ is set
        self.assertTrue(rec_cls)
        self.assertEqual(ReactObjMClass, rec_cls.__metaclass__)

        # check if rec_cls is registered with react.meta
        self.assertIsInstance(react.meta.find(rec_cls.kind(), rec_cls.__name__), meta_cls)

        # check if created obj is registered with react.db
        r = rec_cls()
        self.assertEqual(rec_cls.meta(), r.meta(), "class  and instance meta() different")
        self.assertEqual(r, react.db.find(rec_cls.kind(), r.id()))

        # check if appropriate meta class is assigned to both r and rec_cls
        meta = r.meta()
        self.assertIsInstance(meta, meta_cls,
                              "%s is not an instance of %s" % (rec_cls.meta(), meta_cls))
        self.assertEqual(rec_cls, meta.obj_type())
        self.assertEqual(rec_cls.__name__, meta.name())

        # check fields
        if len(fld_names) > 0: self.assertEqual(len(fld_names), len(meta.fields())) 
        for fname in fld_names:
            self.assertTrue(fname in meta.fields())

        if len(fields) > 0: self.assertEqual(len(fields), len(meta.fields())) 
        for fname in fields:
            self.assertTrue(fname in meta.fields())
            self.assertEqual(str(fields[fname]), str(meta.fields()[fname]))

        # check_all, check_alias_obj
        self.check_all(rec_cls)
        self.check_alias_obj(rec_cls)

    def assert_record_cls(self, *args, **kwargs): self.assert_rec_cls(*args, **kwargs)

    def assert_obj_field_vals(self, cls, **fld_vals):
        obj = cls()
        for fname, fvalue in fld_vals.iteritems():
            self.assertEqual(fvalue, getattr(obj, fname).unwrap())

    def check_all(self, cls):
        pre = cls.all()
        obj = cls()
        post = pre + [obj]
        self.assertEqual(set(post), set(cls.all()))
    
    def check_alias_obj(self, cls):
        obj = cls()
        pre = cls.all()
        a = cls.alias_obj(obj.id())
        self.assertEqual(obj.id(), a.id())
        self.assertNotEqual(id(obj), id(a))
        self.assertEqual(pre, cls.all())
                
