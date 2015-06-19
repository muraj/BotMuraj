from plugin_lib import trigger
import ast
import operator as op
import math
import cmath
import re

try:
  import pint
  ureg = pint.UnitRegistry(autoconvert_offset_to_baseunit=True)
  ureg.default_format = 'P'
  Quantity = ureg.Quantity
except ImportError:
  ureg, Quantity = None, None

def safe_pow(a,b,z=None):
  va, vb = a, b
  if isinstance(a, complex):
    va = (a**2).real
  elif isinstance(a, Quantity):
    va = a.magnitude

  if isinstance(b, complex):
    vb = (b**2).real
  elif isinstance(b, Quantity):
    vb = b.magnitude

  if va < 1000000 and vb < 1000000:
    return pow(a, b, z)
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
ucode_repls = {u'\u03A0': 'pi', u'\u2107':'e', u'\u221E':'inf' }

safe_functions = ['ceil', 'fabs', 'floor', 'trunc', 'exp', 'sqrt', 'log', 'log10',
                  'acos', 'asin', 'atan', 'cos', 'sin', 'tan',
                  'acosh', 'asinh', 'atanh', 'cosh', 'sinh', 'tanh',
                  'erf', 'erfc', 'gamma', 'lgamma',
                  'degrees', 'radians']

def math_func(f):
  def func(*args):
    for a in args:
      if isinstance(a, complex):
        return getattr(cmath, f)(*args)
      else:
        return getattr(math, f)(*args)
  return func
  

for f in safe_functions:
  functions[f] = math_func(f) if hasattr(cmath, f) else getattr(math, f)

functions['fact'] = lambda x: functions['gamma'](x+1)
functions['pow'] = safe_pow

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
  global ucode_repls
  if not user.startswith(channel):
    if not msg.startswith(bot.nickname):
      return True
  if msg.startswith(bot.nickname):
    msg = re.sub(bot.nickname + '\\S+', '', msg).strip()

  msg = msg.decode('utf8')
  for u,s in ucode_repls.items():
    msg = msg.replace(u,s)
  msg = msg.encode('utf8')

  # Split out the unit conversion op
  msg, _, endunit = msg.partition(' to ')
  endunit = endunit.strip()

  # Convert '1 foot' to '1*foot'
  # since ast can't compile "NUM NAME", only "NUM OP NAME"
  msg = re.sub(r'([^*\/\s])\s+(\w+)', r'\1 * \2', msg)

  try:
    res = eval_(ast.parse(msg, mode='eval').body)
    if endunit: res = res.to(endunit)
  except Exception as e:
    bot.log.msg(str(e))
    return True
  user,_,_ = user.partition('!')
  bot.msg(channel, "%s: %s" % (user, unicode(res).encode('utf8')))
