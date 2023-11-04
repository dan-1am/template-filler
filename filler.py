# v1.00

#import re
#def eval_template(src, context):
#    return re.sub(r'\{\{(.*?)\}\}', lambda m: str( eval(m[1], context) ), src)


def fill(src, context):
    first,*parts = src.split("{{")
    ans = [first]
    for part in parts:
        cmd,_,text = part.partition("}}")
        value = str( eval(cmd, context) )
        ans.append(value)
        ans.append(text)
    return "".join(ans)


def parse(src, open="{%", close="%}"):
    first,*parts = src.split(open)
    queued = [dict(cmd=None, args=None, text=first, children=[])]
    for part in parts:
        line,_,text = part.partition(close)
        cmd,*args = line.split()
        if cmd.startswith("end"):
            last = queued.pop()
            if last['cmd'] != cmd[3:]:
                raise SyntaxError(f"Template tag {last['cmd']} closed with {cmd}")
            last['after'] = text
            queued[-1]['children'].append(last)
        elif cmd in ["if","for"]:
            queued.append( dict(cmd=cmd, args=args, text=text, children=[]) )
        else:
            raise SyntaxError(f"Unknown template tag {cmd}")
    if len(queued) > 1:
        raise SyntaxError(f"Tag {queued[-1]['cmd']} is not closed")
    return queued[0]


def recurse(tree, context, ans):
    cmd = tree['cmd']
    if cmd == "if":
        test = eval( " ".join(tree['args']) , context )
        if not test:
            return
        ans.append( fill(tree['text'] , context) )
        for c in tree['children']:
            recurse(c, context, ans)
    elif cmd == "for":
        var, word_in, *args = tree['args']
        if word_in != "in":
            raise SyntaxError(f"Invalid {cmd} tag in: {''.join(tree['args'])}")
        sequence = eval( " ".join(args) , context )
        outer = { k: context.get(k, None) for k in ("outer","index") }
        context['outer'] = type('', (), outer)()
        for i,value in enumerate(sequence):
            context[var] = value
            context['index'] = i
            ans.append( fill(tree['text'] , context) )
            for c in tree['children']:
                recurse(c, context, ans)
        context.update(outer)
    else:
        ans.append( fill(tree['text'] , context) )
        for c in tree['children']:
            recurse(c, context, ans)
    ans.append( fill(tree.get('after',""), context) )


def execute(tree, context):
    ans = []
    recurse(tree, context, ans)
    return "".join(ans)


def use(src, context):
    tree = parse(src)
    return execute(tree, context)
