import unittest
import filler


context = dict(a="alpha", b="book", d=[5,4,3])

class TestFiller(unittest.TestCase):

    def test_fill_without_tags(self):
        src = """Some text.\n  Line two."""
        text = filler.fill(src, context)
        self.assertEqual(text, src)

    def test_fill_variables(self):
        src = """begin {{a}} mid {{b}} last {{d[1]}} end"""
        text = filler.fill(src, context)
        self.assertEqual(text, "begin alpha mid book last 4 end")

    def test_fill_expressions(self):
        src = """{{a+"-fx"}} {{len(b)}} {{d[1]*2+1.5}} end"""
        text = filler.fill(src, context)
        self.assertEqual(text, "alpha-fx 4 9.5 end")

    def test_single_if(self):
        src = """a {% if a == "alpha" %}ok{% endif %} b"""
        text = filler.use(src, context)
        self.assertEqual(text, "a ok b")
        src = """a {% if b == "bad" %}bad{% endif %} b"""
        text = filler.use(src, context)
        self.assertEqual(text, "a  b")

    def test_if_else(self):
        src = """a {% if a == "alpha" %}ok{% else %}bad{% endif %} b"""
        text = filler.use(src, context)
        self.assertEqual(text, "a ok b")
        src = """a {% if a == "wrong" %}ok{% else %}bad{% endif %} b"""
        text = filler.use(src, context)
        self.assertEqual(text, "a bad b")

    def test_single_elif(self):
        context = dict(a=1)
        src = """a {% if a == 1 %}1{% elif a == 2 %}2{% endif %} b"""
        text = filler.use(src, context)
        self.assertEqual(text, "a 1 b")
        context['a'] = 2
        text = filler.use(src, context)
        self.assertEqual(text, "a 2 b")

    def test_elif_chain(self):
        context = dict(a=1)
        src = ("""a {% if a == 1 %}1{% elif a == 2 %}2"""
            """{% elif a == 3 %}3{% else %}4{% endif %} b""")
        for n in range(1,5):
            context['a'] = n
            text = filler.use(src, context)
            self.assertEqual(text, f"a {n} b")

    def test_spaces_near_tags(self):
        src = """a  {% if a == "alpha" %}\n ok  \n{% endif %} b"""
        text = filler.use(src, context)
        self.assertEqual(text, """a  \n ok  \n b""")

    def test_single_for(self):
        src = """{% for i in range(3) %}{{i}}+{% endfor %}"""
        text = filler.use(src, context)
        self.assertEqual(text, """0+1+2+""")
        src = """{% for i in d %}{{i}}-{% endfor %}"""
        text = filler.use(src, context)
        self.assertEqual(text, """5-4-3-""")

    def test_nested_fors(self):
        src = ("{% for i in range(2) %}{% for n in d %}"
        "{{i}}. {{n}}; "
        "{% endfor %}{% endfor %}")
        text = filler.use(src, context)
        self.assertEqual(text, "0. 5; 0. 4; 0. 3; 1. 5; 1. 4; 1. 3; ")

    def test_outer_for_index(self):
        src = ("{% for m in ('ab','cd') %}"
        "{% for i in d %}{% for n in range(2) %}"
        "{{outer.outer.index}}{{outer.index}}{{index}}={{m}}{{i}}{{n}} "
        "{% endfor %}{% endfor %}{% endfor %}")
        need = "000=ab50 001=ab51 010=ab40 011=ab41 020=ab30 021=ab31"\
        " 100=cd50 101=cd51 110=cd40 111=cd41 120=cd30 121=cd31 "
        text = filler.use(src, context)
        self.assertEqual(text, need)


if __name__ == '__main__':
    unittest.main()
