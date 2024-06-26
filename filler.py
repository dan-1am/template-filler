""" Create text-based file from template.

Standard usage:

import filler
text = filler.use(template, context)

Preparse template for repeated use:

tree = filler.parse(template)
for context in contexts:
    result.append( filler.execute(tree, context)

Simplest usage (variable/expression substitution only):

text = filler.fill(template, context)

If you need variable/expression substitution only,
without control commands, you can do it without this module:

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

from typing import Callable


__version__ = "1.07"
__all__ = ["fill", "parse", "execute", "use"]


def fill(template: str, context: dict) -> str :
    """Basic templating. Fill vars and expressions."""
    first,*parts = template.split("{{")
    result = [first]
    for part in parts:
        cmd,_,text = part.partition("}}")
        value = str( eval(cmd, context) )
        result.append(value)
        result.append(text)
    return "".join(result)


CommandType = Callable[[dict, dict, list[str]], None]

commands: dict[str, CommandType] = {}


def command(f: CommandType) -> CommandType:
    """Decorator. Add tag command to registry."""
# need python 3.9+
#    tag = f.__name__.removeprefix("cmd_")
    tag = f.__name__
    if tag.startswith("cmd_"):
        tag = tag[4:]
    commands[tag] = f
    return f


@command
def cmd_pass(tree, context, result):
    """Pass (do nothing) tag command."""
    result.append( fill(tree['text'], context) )
    for c in tree['children']:
        recurse(c, context, result)

@command
def cmd_if(tree, context, result):
    test = eval( " ".join(tree['args']) , context )
    if test:
        cmd_pass(tree, context, result)
    else:
        branch = tree.get('else', None)
        if branch:
            recurse(branch, context, result)


commands['elif'] = cmd_if
commands['else'] = cmd_pass


@command
def cmd_for(tree, context, result):
    var, word_in, *args = tree['args']
    if word_in != "in":
        raise SyntaxError(f"Invalid {tree.cmd} tag in: {''.join(tree['args'])}")
    sequence = eval( " ".join(args) , context )
    outer = { k: context.get(k, None) for k in ("outer","index") }
    context['outer'] = type('', (), outer)()
    for i,value in enumerate(sequence):
        context[var] = value
        context['index'] = i
        cmd_pass(tree, context, result)
    context.update(outer)


def closetag(queued: list, cmd: str, text: str) -> None:
    last = queued.pop()
    if last["cmd"] in ("elif","else"):
        last = queued.pop()
    last["after"] = text
    if last["cmd"] != cmd[3:]:
        raise SyntaxError(f'Template tag {last["cmd"]} closed with {cmd}')
    queued[-1]["children"].append(last)


def opentag(queued: list, cmd: str, args: list, text: str) -> None:
    parsed = dict(cmd=cmd, args=args, text=text, children=[])
    if cmd in ("elif","else"):
        queued[-1]["else"] = parsed
        if queued[-1]["cmd"] == "elif":  # drop previous elif tags
            queued.pop()
        if queued[-1]["cmd"] != "if":
            raise SyntaxError(f"Tag {cmd} without if in: {cmd} {' '.join(args)}")
    queued.append(parsed)


def parse(template: str, open="{%", close="%}") -> dict:
    """Parse template to a tree."""
    first,*parts = template.split(open)
    queued: list = [dict(cmd="pass", args=None, text=first, children=[])]
    for part in parts:
        line,_,text = part.partition(close)
        cmd,*args = line.split()
        if cmd.startswith("end"):
            closetag(queued, cmd, text)
        elif cmd in (commands):
            opentag(queued, cmd, args, text)
        else:
            raise SyntaxError(f"Unknown template tag {cmd}")
    if len(queued) > 1:
        raise SyntaxError(f'Tag {queued[-1]["cmd"]} is not closed')
    return queued[0]


def recurse(tree: dict, context: dict, result: list[str]):
    """Traverse template tree and collect executed pieces."""
    cmd = tree["cmd"]
    commands[cmd](tree, context, result)
    result.append( fill(tree.get("after",""), context) )


def execute(tree: dict, context: dict) -> str:
    """Execute parsed template tree."""
    result: list[str] = []
    recurse(tree, context, result)
    return "".join(result)


def use(template: str, context: dict) -> str:
    """Parse and execute template."""
    tree = parse(template)
    return execute(tree, context)
