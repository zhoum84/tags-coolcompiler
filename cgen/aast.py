import main as M

asm = ""

class Node(object):
    def __init__(self, lineno, anno_type):
        self.lineno = lineno
        self.anno_type = anno_type
    
    def s(self):
        return ""
    # def __str__(self):
    #     return self.s()
    def cgen(self):
        pass

class Attribute(Node):
    def __init__(self, _id, _type, _init = None, num_temps=0):
        #super().__init__(lineno, anno_type)
        self.id = _id
        self.type = _type
        self.init = _init
        self.num_temps = 0

class Method(Node):
    def __init__(self, method_name, formals, method_label):
        #super().__init__(lineno, anno_type)
        self.method_name = method_name
        self.formals = formals
        self.method_label = method_label
    
    def s(self):
        s = self.method_name + '\n'
        for f in self.formals:
            s += str(f) + '\n'
        s += self.method_label + '\n'
        return s
    
class MethodImplementation(Method):
    def __init__(self, class_name, method_name, formals, method_label, exp, num_temps=0):
        super().__init__(method_name, formals, method_label)
        self.exp = exp
        self.class_name =class_name
        self.num_temps = num_temps

    def s(self):
        s = super().s()
        s += str(self.exp) + '\n'
        s += self.class_name + '\n'
        return s

class Assign(Node):
    ident = None
    exp = None

    def __init__(self, lineno, anno_type, _ident, _exp):
        super().__init__(lineno, anno_type)
        #super().__init__(_line_num)
        self.ident = _ident
        self.exp = _exp
        #self.exp_type = self.exp.exp_type
    
    def cgen(self, st):
        global asm
        loc = self.exp.exp.cgen(st)
        asm += f'\t\tmov {M.reg_three} <- {loc}\n'
        asm += f'\t\tst {st[self.exp.ident.name]} <- {M.reg_three};;assign\n'
        return loc


    
class Variable(Node):
    def __init__(self, lineno, anno_type, name):
        super().__init__(lineno, anno_type)
        self.name = name
    def s(self):
        return self.name

class Arithmetic(Node):
    type = "Int"
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type)
        self.e1 = e1
        self.e2 = e2

class Plus(Arithmetic):
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type, e1, e2)

    def s(self):
        return str(self.e1) + '+' + str(self.e2)

class Minus(Arithmetic):
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type, e1, e2)

class Times(Arithmetic):
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type, e1, e2)

class Divide(Arithmetic):
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type, e1, e2)


class Internal(Node):
    def __init__(self, lineno, anno_type, method):
        super().__init__(lineno, anno_type)
        self.method = method
    def s(self):
        return str(self.method)
    
class Self_Dispatch(Node):
    def __init__(self, lineno, anno_type, method, formals):
        super().__init__(lineno, anno_type)
        self.method = method
        self.formals = formals

    def s(self):
        s = str(self.method) +'\n'
        for f in self.formals:
            s += str(f) + '\n'
        return s
class Dynamic_Dispatch(Self_Dispatch):
    def __init__(self, lineno, anno_type,ro, method, formals):
        super().__init__(lineno, anno_type, method, formals)
        self.ro = ro # receiver object

class Static_Dispatch(Dynamic_Dispatch):
    def __init__(self, lineno, anno_type, ro, method, formals, caller_type):
        super().__init__(lineno, anno_type, ro, method, formals)
        self.caller_type = caller_type

class New(Node):
    def __init__(self, lineno, anno_type):
        super().__init__(lineno, anno_type)
        self.new_type = anno_type

class Base(Node):
    def __init__(self, lineno, anno_type, value):
        super().__init__(lineno, anno_type)
        self.value = value

class Int(Base):
    value: int
    type = "Int"
    def __init__(self, lineno, anno_type, value):
        super().__init__(lineno, anno_type, value)

class String(Base):
    value: str
    type = "String"
    def __init__(self, lineno, anno_type, value):
        super().__init__(lineno, anno_type, value)

class TrueExp(Base):
    value: bool
    type = "Bool"
    def __init__(self, lineno, anno_type):
        super().__init__(lineno, anno_type, True)

class FalseExp(Base):
    value: bool
    type = "Bool"
    def __init__(self, lineno, anno_type):
        super().__init__(lineno, anno_type, False)

class Compare(Node):
    type = "Bool"
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type)
        self.e1 = e1
        self.e2 = e2

class LessThan(Compare):
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type, e1, e2)
class LessThanEqual(Compare):
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type, e1, e2)

class Equal(Compare):
    def __init__(self, lineno, anno_type, e1, e2):
        super().__init__(lineno, anno_type, e1, e2)

class Unary(Node):
    def __init__(self, lineno, anno_type, exp):
        super().__init__(lineno, anno_type)
        self.exp = exp

class Negate(Unary):
    type = "Int"
    def __init__(self, lineno, anno_type, exp):
        super().__init__(lineno, anno_type, exp)

class Not(Unary):
    type = "Bool"
    def __init__(self, lineno, anno_type, exp):
        super().__init__(lineno, anno_type, exp)
class Isvoid(Unary):
    type = "Bool"
    def __init__(self, lineno, anno_type, exp):
        super().__init__(lineno, anno_type, exp)

class If(Node):
    def __init__(self, lineno, anno_type, predicate, then_body, else_body):
        super().__init__(lineno, anno_type)
        self.predicate = predicate
        self.then_body = then_body
        self.else_body = else_body


class While(Node):
    def __init__(self, lineno, anno_type, _predicate, _body):
        super().__init__(lineno, anno_type)
        self.predicate = _predicate
        self.body = _body
    
    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        ret += str(self.predicate)
        ret += str(self.body) 
        return ret

class ExpCase(Node):
    ident = "case"
    def __init__(self, lineno, anno_type, exp, caselist):
        super().__init__(lineno, anno_type)
        self.exp = exp
        self.caselist = caselist

    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        ret += str(self.exp) 
        ret += str(len(self.caselist)) + '\n'
        for case in self.caselist:
            ret += str(case) 
        return ret
    
class CaseItem(Node):
    def __init__(self, lineno, anno_type, identifier_nt, _type, exp):
        super().__init__(lineno, anno_type)
        self.identifier_nt = identifier_nt
        self.type = _type
        self.exp = exp
        self.exp_type = _type
    
    def __str__(self):
        return str(self.identifier_nt) + str(self.type) + str(self.exp)

class Block(Node):
    def __init__(self, lineno, anno_type, exp_list):
        super().__init__(lineno, anno_type)
        self.exp_list = exp_list

class Let(Node):
    ident = "let"
    letlist = []
    def __init__(self, lineno, anno_type, letlist, body):
        super().__init__(lineno, anno_type)
        self.letlist = letlist
        self.body = body

class LetNoinit(Node):
    ident = "let_binding_no_init"
    def __init__(self, lineno, anno_type, identifier_nt, type):
        super().__init__(lineno, anno_type)
        self.identifier_nt = identifier_nt
        self.type = type
  

class LetInit(LetNoinit):
    def __init__(self, lineno, anno_type, identifier_nt, type, exp):
        super().__init__(lineno, anno_type, identifier_nt, type)
        self.exp = exp
