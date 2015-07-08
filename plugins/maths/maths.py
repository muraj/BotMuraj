from plugin_lib import trigger
import ast
import operator as op
import math
import cmath
import re
import string

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

base_repls = {'binary': 2, 'ternary':3, 'quaternary':4, 'quinary':5,
              'senary':6, 'oct':8, 'octal':8, 'decimal':10, 'dec':10, 
              'undecimal':11, 'duodecimal':12, 'tridecimal':13, 'tetradecimal':14,
              'pentadecimal':15, 'hex':16, 'hexadecimal':16, 'vigesimal':20,
              'tetravigesimal':24, 'heptavigesimal':27, 'trigesimal':30,
              'duotrigesimal':32, 'hexatrigesimal':36, 'sexagesimal':60,
              'tetrasexagesimal':64, 'pentoctogesimal':85 }

safe_functions = ['ceil', 'fabs', 'floor', 'trunc', 'exp', 'log', 'log10',
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
functions['sqrt'] = lambda x: functions['pow'](x, 0.5)

def eval_(node):
  global functions, constants
  if isinstance(node, ast.Num):
    return ureg.Quantity(node.n)
  elif isinstance(node, ast.Name):
    if node.id in constants: return ureg.Quantity(constants[node.id])
    return ureg(node.id)
  elif isinstance(node, ast.BinOp):
    return operators[type(node.op)](eval_(node.left), eval_(node.right))
  elif isinstance(node, ast.UnaryOp):
    return operators[type(node.op)](eval_(node.operand))
  elif isinstance(node, ast.Call):
    print node.args
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

def to_base(n, b, d):
  if n == 0: return ''
  nb, r = divmod(n, b)
  return to_base(nb, b, d) + d[r]

def frac_to_base(f, b, d, perc=8, pt='.'):
  if f == 0 or perc == 0: return ''
  n, f = divmod(f,1)
  return to_base(int(n), b, d) + pt + frac_to_base(f*b, b, d, perc-1, '')

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
  endunit = endunit.strip().lower()
  # Replace common name with base number
  if endunit in base_repls:
    endunit = 'base'+str(base_repls[endunit])

  # Convert '1 foot' to '1*foot'
  # since ast can't compile "NUM NAME", only "NUM OP NAME"
  msg = re.sub(r'([^*\/\s])\s+([A-Za-z]+)', r'\1 * \2', msg)
  # Replace keyword 'in' with 'inch'
  msg = re.sub(r'\bin\b', 'inch', msg)

  #try:
  bot.log.msg("Evaluating '%s'" % msg)
  res = eval_(ast.parse(msg, mode='eval').body)
  if endunit.startswith('base'):
    base = int(endunit[4:])
    # enough to go to base 85
    alpha = string.digits + string.letters + '.-:+=^!/*?&<>()[]{}@%$#'
    # Special alphabet bases
    if base == 32: alpha = string.ascii_uppercase + string.digits[2:8]
    elif base == 64: alpha = string.ascii_uppercase + string.ascii_lowercase + string.digits + '+/'
    elif base > 85:
      answer = 'Base too big...'
    answer = '-' if res.magnitude < 0 else ''
    answer += frac_to_base(abs(res.magnitude), base, alpha)
    answer += u''.join([unichr(0x2080 + ord(c) - ord('0')) for c in str(base)]).encode('utf8')
    if len(res.units) != 0:
      answer += ' ' + pint.formatting.format_unit(res.units, 'P').encode('utf8') # Already encoded
  elif endunit: answer = unicode(res.to(endunit)).encode('utf8')
  #except Exception as e:
  #  bot.log.msg(str(e))
  #  return True
  user,_,_ = user.partition('!')
  bot.msg(channel, "%s: %s" % (user, answer))
