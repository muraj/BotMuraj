from plugin_lib import trigger
import ast
import operator as op
import math
import cmath
import re

try:
  import pint
  ureg = pint.UnitRegistry()
  ureg.default_format = 'P'
except ImportError:
  ureg = None

def safe_pow(a,b):
  va, vb = a, b
  if isinstance(a, complex) or isinstance(b, complex):
    va, vb = (a**2).real, (b**2).real # sqr norm
  if va < 1000000 and vb < 1000000:
    return op.pow(a, b)
  else:
    raise OverflowError()

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Mod: op.mod,
             ast.Div: op.truediv, ast.FloorDiv: op.floordiv, ast.Pow: safe_pow,
             ast.BitXor: op.xor, ast.BitOr: op.__or__, ast.BitAnd: op.__and__,
             ast.LShift: op.lshift, ast.RShift: op.rshift,
             ast.Not: op.not_, ast.USub: op.neg, ast.UAdd: op.pos, ast.Invert: op.inv,
             ast.Eq: op.eq, ast.NotEq: op.ne, ast.Lt: op.lt, ast.LtE: op.le, ast.Gt: op.gt, ast.GtE: op.ge }

functions = {}

constants = dict(pi=math.pi, e=math.e, nan=float('nan'), inf=float('inf'))

safe_functions = ['ceil', 'fabs', 'floor', 'trunc', 'exp', 'sqrt', 'log', 'log10',
                  'acos', 'asin', 'atan', 'cos', 'sin', 'tan',
                  'acosh', 'asinh', 'atanh', 'cosh', 'sinh', 'tanh',
                  'erf', 'erfc', 'gamma', 'lgamma',
                  'degrees', 'radians']

for f in safe_functions:
  if hasattr(cmath, f):
    def func(*args):
      for a in args:
        if isinstance(a, complex):
          return getattr(cmath, f)(*args)
        else:
          return getattr(math, f)(*args)
  else:
    func = getattr(math, f)
  functions[f] = func

functions['fact'] = lambda x: functions['gamma'](x+1)

def eval_(node):
  global functions, constants
  if isinstance(node, ast.Num):
    return node.n
  elif isinstance(node, ast.Name):
    return constants.get(node.id, None) or ureg(node.id)
  elif isinstance(node, ast.BinOp):
    return operators[type(node.op)](eval_(node.left), eval_(node.right))
  elif isinstance(node, ast.UnaryOp):
    return operators[type(node.op)](eval_(node.operand))
  elif isinstance(node, ast.Call):
    args = [ eval_(arg) for arg in node.args ]
    return functions[node.func.id](*args)
  elif isinstance(node, ast.Compare):
    a = eval_(node.left)
    vals = [ eval_(val) for val in node.comparators ]
    for i, op in enumerate(node.ops):
      if not operators[type(op)](a, vals[i]):
        return False
      a = vals[i]
    return True
  else:
    raise TypeError(node)

@trigger('PRIVMSG', priority=1000)
def eval_trigger(bot, user, channel, msg):
  if not user.startswith(channel):
    if not msg.startswith(bot.nickname):
      return True
  if msg.startswith(bot.nickname):
    msg = re.sub(bot.nickname + '\\S+', '', msg).strip()
  try:
    msg, _, endunit = msg.partition(' to ')
    endunit = endunit.strip()
    res = eval_(ast.parse(msg, mode='eval').body)
    if endunit: res = res.to(endunit)
  except Exception as e:
    bot.log.msg(str(e))
    return True
  user,_,_ = user.partition('!')
  bot.msg(channel, "%s: %s" % (user, unicode(res).encode('utf8')))
