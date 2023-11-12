""" Template filling with context

Standard usage:

import filler

text = filler.use(template, context)


Preparse template for repeated use:

tree = filler.parse(template)
for context in contexts:
    result.append( filler.execute(tree, context)


Simplest usage (variable/expression substitution):

text = filler.fill(template, context)


If you need variable/expression substitution only,
without control commands, you don't need this module:

import re

def eval_template(template, context):
    return re.sub(r'\{\{(.*?)\}\}',
        lambda m: str( eval(m[1], context) ), template)


Template example:

<html><head><title>{{title}}</title></head>
<body><h1>{{title}}</h1>
{% for planet in planets %}
  <p>{{index+1}}. {{planet}}</p>
  {% if not planets[planet] %}<p>no satellites</p>{% endif %}
  {% for satellite in planets[planet]%}
    <p>{{outer.index+1}}.{{index+1}}. {{satellite}}</p>
  {% endfor %}
{% endfor %}
</body></html>
"""

__version__ = "1.05"
__all__ = ["fill", "parse", "execute", "use"]


def fill(template, context):
    """Basic templating. Fill vars and expressions."""
    first,*parts = template.split("{{")
    ans = [first]
    for part in parts:
        cmd,_,text = part.partition("}}")
        value = str( eval(cmd, context) )
        ans.append(value)
        ans.append(text)
    return "".join(ans)



commands = {}


def command(f):
    """Decorator. Add tag command to registry."""
    tag = f.__name__.removeprefix("cmd_")
    commands[tag] = f
    return f


@command
def cmd_pass(tree, context, ans):
    """Pass (do nothing) tag command."""
    ans.append( fill(tree['text'] , context) )
    for c in tree['children']:
        recurse(c, context, ans)


@command
def cmd_if(tree, context, ans):
    test = eval( " ".join(tree['args']) , context )
    if test:
        cmd_pass(tree, context, ans)
    else:
        branch = tree.get('else', None)
        if branch:
            recurse(branch, context, ans)


commands['elif'] = cmd_if
commands['else'] = cmd_pass


@command
def cmd_for(tree, context, ans):
    var, word_in, *args = tree['args']
    if word_in != "in":
        raise SyntaxError(f"Invalid {tree.cmd} tag in: {''.join(tree['args'])}")
    sequence = eval( " ".join(args) , context )
    outer = { k: context.get(k, None) for k in ("outer","index") }
    context['outer'] = type('', (), outer)()
    for i,value in enumerate(sequence):
        context[var] = value
        context['index'] = i
        cmd_pass(tree, context, ans)
    context.update(outer)


def parse(template, open="{%", close="%}"):
    """Parse template to a tree."""
    first,*parts = template.split(open)
    queued = [dict(cmd="pass", args=None, text=first, children=[])]
    for part in parts:
        line,_,text = part.partition(close)
        cmd,*args = line.split()
        if cmd.startswith("end"):
            last = queued.pop()
            if last["cmd"] in ("elif","else"):
                last = queued.pop()
            last["after"] = text
            if last["cmd"] != cmd[3:]:
                raise SyntaxError(f'Template tag {last["cmd"]} closed with {cmd}')
            queued[-1]["children"].append(last)
        elif cmd in (commands):
            parsed = dict(cmd=cmd, args=args, text=text, children=[])
            if cmd in ("elif","else"):
                queued[-1]["else"] = parsed
                if queued[-1]["cmd"] == "elif":  # drop previous elif tags
                    queued.pop()
                if queued[-1]["cmd"] != "if":
                    raise SyntaxError(f"Tag {cmd} without if in: {line}")
            queued.append(parsed)
        else:
            raise SyntaxError(f"Unknown template tag {cmd}")
    if len(queued) > 1:
        raise SyntaxError(f'Tag {queued[-1]["cmd"]} is not closed')
    return queued[0]


def recurse(tree, context, ans):
    """Traverse template tree and collect executed pieces"""
    cmd = tree["cmd"]
    commands[cmd](tree, context, ans)
    ans.append( fill(tree.get("after",""), context) )


def execute(tree, context):
    """Execute parsed template tree."""
    ans = []
    recurse(tree, context, ans)
    return "".join(ans)


def use(template, context):
    """Parse and execute template."""
    tree = parse(template)
    return execute(tree, context)
