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
        src = """{% if a == "alpha" %}ok{% endif %}"""
        text = filler.use(src, context)
        self.assertEqual(text, "ok")
        src = """{% if b == "bad" %}bad{% endif %}"""
        text = filler.use(src, context)
        self.assertEqual(text, "")

    def test_spaces_near_tags(self):
        src = """begin  {% if a == "alpha" %}\n ok  \n{% endif %} end"""
        text = filler.use(src, context)
        self.assertEqual(text, """begin  \n ok  \n end""")

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

context = dict(a="alpha", b="book", d=[5,4,3])
src = """\
line1 {{a}}
1 {% if a == "alpha" %} 2
{% for i in d %}
<h1>head{{i}}</h1>
body{% if i == 4 %} four! {% endif %}
{% for j in range(2) %}{{for_parent['for_counter']}}:{{j}}{% endfor %}
{% endfor %}
{% endif %}
done {{b}}
"""

tree = filler.parse(src, "{%", "%}")
print(tree)
print( filler.execute(tree, context) )


if __name__ == '__main__':
    unittest.main()
