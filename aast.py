from typing import List
class Expression(object):
    exp_type = "NO_TYPE"
    line_num = None
    def __init__(self, _line_num):
        self.line_num = _line_num
    def s(self):
        ret = str(self.line_num) +  '\n'
        ret += self.exp_type + '\n' # TODO: UNCOMMENT THIS LATER
        return ret
    def __str__(self):
        return self.s()
    def __repr__(self):
        return str(self)

class InternalExpression(Expression):
    ident = "internal"
    def __init__(self, _line_num, _name, _exp_type):
        super().__init__(_line_num)
        self.name = _name
        self.exp_type = _exp_type
    def __str__(self):
        ret = str(self.line_num) + '\n'
        ret += self.exp_type + '\n'
        ret += self.ident +'\n'
        ret += self.name.ident + '\n'
        return ret
    def __repr__(self):
        return str(self)

class Identifier(object):
    line_num = None
    ident= None
    def __init__(self, _line_num, ident):
        self.line_num = _line_num
        self.ident = ident
    def __str__(self):
        ret = str(self.line_num) + '\n'  + self.ident + "\n"
        return ret
    
class Integer(Expression):
    val = None
    ident = "integer"
    def __init__(self, _line_num, int_val):
        Expression.__init__(self, _line_num)
        self.val = int_val
        self.exp_type = "Int"

    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n" + str(self.val) + '\n'
        return ret
        #return "Integer( "+str(self.int_val)+" )"

class String(Expression):
    val = None
    ident = "string"
    def __init__(self, _line_num, str_val):
        Expression.__init__(self, _line_num)
        self.val = str_val
        self.exp_type = "String"

    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n" + self.val + '\n'
        return ret

class TrueExp(Expression):
    ident = "true"
    def __init__(self, _line_num):
        super().__init__(_line_num)
        self.exp_type = "Bool"

    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        return ret

class FalseExp(Expression):
    ident = "false"
    def __init__(self, _line_num):
        super().__init__(_line_num)
        self.exp_type = "Bool"
    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        return ret


class IdentifierExp(Expression):
    ident = None
    #ident = "identifier"
    def __init__(self, _line_num, _ident_name):
        super().__init__(_line_num)
        self.ident = _ident_name
    def __str__(self):
        ret = self.s()
        #ret += self.ident + "\n" 
        ret += "identifier\n"
        ret += str(self.ident)
        return ret
    
class New(Expression):
    ident = None
    # ident = "new"
    def __init__(self, _line_num, _ident):
        super().__init__(_line_num)
        self.ident = _ident
        self.exp_type = _ident.ident

    def __str__(self):
        ret = self.s()
        ret += "new\n"
        #ret += self.ident + "\n" 
        ret += str(self.ident)
        return ret

class Isvoid(Expression):
    ident = None
    #ident = "isvoid"
    def __init__(self, _line_num, _ident):
        super().__init__(_line_num)
        self.ident = _ident
        self.exp_type = _ident.ident

    def __str__(self):
        ret = self.s()
        ret += "isvoid\n"
        #ret += self.ident +"\n" 
        ret += str(self.ident)
        return ret

class Assign(Expression):
    ident = None
    exp = None
    #ident = "assign"
    def __init__(self, _line_num, _ident, _exp):
        super().__init__(_line_num)
        self.ident = _ident
        self.exp = _exp
        self.exp_type = self.exp.exp_type
    
    def __str__(self):
        ret = self.s()
        ret += "assign\n"
        #ret += self.ident + "\n"
        ret += self.ident.line_num + "\n"
        ret += self.ident.ident + "\n"
        ret += str(self.exp)
        return ret

class Dispatch(Expression):
    method_ident = None
    args = None
    def __init__(self, _line_num, _method_ident, _args):
        super().__init__(_line_num) 
        self.method_ident = _method_ident
        self.args = _args

class Dynamic_Dispatch(Dispatch):
    exp = None
    ident = "dynamic_dispatch"
    def __init__(self, _line_num, _exp, _method_ident, _args):
        super().__init__(_line_num,_method_ident, _args) 
        self.exp = _exp
    
    def __str__(self):
        ret = str(self.line_num) + '\n' 
        ret += self.ident + "\n"
        ret += str(self.exp) + str(self.method_ident) + str(len(self.args)) + '\n'
        for arg in self.args:
            ret += str(arg)
        return ret

class Static_Dispatch(Dispatch):
    exp = None
    type_ident = None
    ident = "static_dispatch"

    def __init__(self, _line_num, _exp, _type_ident,  _method_ident, _args):
        super().__init__(_line_num, _method_ident, _args) 
        self.exp = _exp
        self.type_ident = _type_ident
    
    def __str__(self):
        ret = self.s()
        ret += self.ident
        ret += str(self.exp) +str(self.type_ident) + str(self.method_ident) + str(len(self.args)) + '\n'
        for arg in self.args:
            ret += str(arg)
        return ret


class Self_Dispatch(Dispatch):
    ident = "self_dispatch"
    exp_type = "SELF_TYPE"
    def __init__(self, _line_num,  _method_ident, _args):
        super().__init__(_line_num, _method_ident, _args) 
    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        ret += str(self.method_ident) + str(len(self.args)) + '\n'
        for arg in self.args:
            ret += str(arg)
        return ret


class If(Expression):
    predicate = None
    then_body = None
    else_body = None
    ident = "if"
    def __init__(self, _line_num, _predicate, _then_body, _else_body):
        super().__init__(_line_num)
        self.predicate = _predicate
        self.then_body = _then_body
        self.else_body = _else_body
    def __str__(self):
        ret = self.s()
        ret += self.ident + '\n'
        ret += str(self.predicate)
        ret += str(self.then_body)
        ret += str(self.else_body)
        return ret

class While(Expression):
    predicate = None
    body = None
    ident = "while"
    exp_type = "Object"
    def __init__(self, _line_num, _predicate, _body):
        super().__init__(_line_num)
        self.predicate = _predicate
        self.body = _body
    
    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        ret += str(self.predicate)
        ret += str(self.body) 
        return ret

class ExpCase(Expression):
    ident = "case"
    def __init__(self, lineno, exp, caselist):
        super().__init__(lineno)
        self.exp = exp
        self.caselist = caselist

    def __repr__(self):
        ret = self.s() + '\n'
        ret += self.ident + "\n"
        ret += repr(self.exp) + '\n'
        ret += repr(self.caselist) 
        return ret
    
class CaseItem(Expression):
    def __init__(self, identifier_nt, type_nt, exp):
        self.identifier_nt = identifier_nt
        self.type_nt = type_nt
        self.exp = exp
    
    def __repr__(self):
        return repr(self.identifier_nt) + '\n' + repr(self.type_nt)  + '\n' + repr(self.exp)


class Let(Expression):
    ident = "let"
    def __init__(self, lineno, letlist, body):
        super().__init__(lineno)
        self.letlist = letlist
        self.body = body
    def __repr__(self):
        ret = self.s()
        ret += self.ident + '\n'
        ret += repr(self.letlist) +'\n'
        ret =+ repr(self.body)
        return ret

class LetNoinit(Let):
    ident = "let_binding_no_init"
    def __init__(self, lineno, identifier_nt, type_nt):
        self.lineno = lineno
        self.identifier_nt = identifier_nt
        self.type_nt = type_nt
    def __repr__(self):
        ret = self.s()
        ret += self.ident + '\n'
        ret += repr(self.identifier_nt) + '\n'
        ret += repr(self.type_nt)
        return ret

class LetInit(LetNoinit):
    
    def __init__(self, lineno, identifier_nt, type_nt, exp):
        super().__init__(lineno, identifier_nt, type_nt)
        self.exp = exp
    def __repr__(self):
        return self.s() + "let_binding_init" + '\n' + repr(self.identifier_nt) + '\n' + repr(self.type_nt) + '\n' + repr(self.exp)

class Arithmetic(Expression):
    lhs = None
    rhs = None
    ident = "arith"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num)
        self.lhs = _lhs
        self.rhs = _rhs
    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        ret += str(self.lhs)
        ret += str(self.rhs)
        return ret

class Plus(Arithmetic):
    ident = "plus"
    exp_type = "Int"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num, _lhs, _rhs)

    def __str__(self):
        return super().__str__()

class Minus(Arithmetic):
    ident = "minus"
    exp_type = "Int"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num, _lhs, _rhs)

    def __str__(self):
        return super().__str__()


class Times(Arithmetic):
    ident = "times"
    exp_type = "Int"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num, _lhs, _rhs)

    def __str__(self):
        return super().__str__()


class Divide(Arithmetic):
    ident = "divide"
    exp_type = "Int"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num, _lhs, _rhs)

    def __str__(self):
        return super().__str__()

class Compare(Expression):
    lhs = None
    rhs = None
    ident = "cmp"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num)
        self.lhs = _lhs
        self.rhs = _rhs

    def __str__(self):
        ret = self.s()
        ret += self.ident + "\n"
        ret += str(self.lhs)
        ret += str(self.rhs)
        return ret
 
class LessThan(Compare):
    ident = "lt"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num, _lhs, _rhs)

    def __str__(self):
        return super().__str__()

class LessThanEqual(Compare):
    ident = "le"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num, _lhs, _rhs)

    def __str__(self):
        return super().__str__()

    # def __str__(self):
    #     ret = self.s()
    #     ret += "le\n"
    #     ret += str(self.lhs)
    #     ret += str(self.rhs)
    #     return ret

class Equal(Compare):
    ident = "eq"
    def __init__(self, _line_num, _lhs, _rhs):
        super().__init__(_line_num, _lhs, _rhs)
    
    def __str__(self):
        return super().__str__()



class Not(Expression):
    ident = None
    exp_type = "Bool"
    def __init__(self, _line_num, _ident):
        super().__init__(_line_num)
        self.ident = _ident
        # self.exp_type = _ident.ident

    def __str__(self):
        ret = self.s()
        ret += "not\n"
        ret += str(self.ident.ident)
        return ret

class Negate(Expression):
    ident = None
    def __init__(self, _line_num, _ident):
        super().__init__(_line_num)
        self.ident = _ident
        self.exp_type = _ident.ident

    def __str__(self):
        ret = self.s()
        ret += "new\n" + str(self.ident)
        return ret

class Formal(object):
    formal_name = None
    formal_type = None

    def __init__(self, _formal_name, _formal_type):
        self.formal_name = _formal_name
        self.formal_type = _formal_type
    
    def __str__(self):
        ret = str(self.formal_name) + '\n'
        ret += str(self.formal_type) + '\n'
        return ret
    def __repr__(self):
        return str(self)

class Attribute(object):
    attr_name = None
    attr_type = None
    initialization = None
    exp = None

    def __init__(self, _attr_name, _attr_type, _initialization, _exp):
        self.attr_name = _attr_name
        self.attr_type = _attr_type
        self.initialization = _initialization
        self.exp = _exp
    
    def __str__(self):
        ret = ""
        if self.initialization:
            ret += "attribute_init\n"
        else:
            ret += "attribute_no_init\n"
        
        ret += str(self.attr_name)
        ret += str(self.attr_type)
        if self.initialization:
            ret += str(self.exp)
        return ret
    def __repr__(self):
        return str(self)

class Method(object):
    method_name = ""
    formals: List[Formal]= []
    method_type = ""
    body_exp = None
    source = None

    def __init__(self, _method_name, _formals, _method_type, _body_exp, source = None):
        self.method_name = _method_name
        self.formals = _formals
        self.method_type = _method_type
        self.body_exp = _body_exp
        self.source = self.source

    def __str__(self):
        ret = "method\n"
        ret += str(self.method_name)
        ret += str(len(self.formals)) + "\n"
        for formal in self.formals:
            ret += str(formal)
        ret += str(self.method_type)
        ret += str(self.body_exp)
        return ret
    
    def __repr__(self):
        return str(self)


class Class(object):
    name_iden: Identifier = None
    inherits_iden = None
    attributes = []
    methods: List[Method] = []
    features = []

    def __init__(self, _name_iden, _inherits_iden, _attributes,_methods, _features):
        self.name_iden = _name_iden
        self.inherits_iden = _inherits_iden
        self.attributes = _attributes
        self.methods = _methods
        self.features = _features
    def __str__(self):
        ret = str(self.name_iden)
        if(self.inherits_iden):
            ret += "inherits\n"
            ret += str(self.inherits_iden) 
        # ret += str(self.attributes)
        # ret += str(self.methods)
        ret += str(len(self.features)) + '\n'
        for feature in self.features:
            ret += str(feature)
        return ret

    def __repr__(self):
        return str(self)
class Block(Expression):
    exp_list = []
    ident = "block"
    def __init__(self, _line_num, _exp_list):
        super().__init__(_line_num)
        self.exp_list = _exp_list
    def __str__(self):
        ret = self.s()
        ret += "block\n"
        ret += str(len(self.exp_list)) + '\n'
        for exp in self.exp_list:
            ret += str(exp)
        return ret
