import sys
import ply.lex as lex
import ply.yacc as yacc

input_filename = sys.argv[1]
#output_filename = input_filename.removesuffix('.cl-lex') + '.cl-ast'
output_filename = input_filename[:-7] + '.cl-ast'
input_lines = []

with open(input_filename) as f:
    # input_lines = [x.rstrip() for x in f.readlines()]
    input_lines = []
    lines = f.readlines()
    #print(lines)
    for i, x in enumerate(lines):
        # handle strings with trailing spaces
        if i > 0 and lines[i - 1] == "string\n":
            input_lines.append(x[:-1])
        else:
            input_lines.append(x.rstrip())


class Lexer(object):
    def token(self):
        #read 2 or 3 lines from input, turn it into a LexToken object
        # fields lineno, value, type, lexpos(=0)
        global input_lines

        if len(input_lines) == 0:
            return None
        line_number = input_lines.pop(0)
        token_type = input_lines.pop(0)
        token_lexeme = ""

        if(token_type in ['type', 'identifier', 'integer', 'string']):
            token_lexeme = input_lines.pop(0)
        return_token = lex.LexToken()
        return_token.lineno = int(line_number)
        return_token.value = token_lexeme
        return_token.type = token_type
        return_token.lexpos = 0
        return return_token

tokens = [
    'class', 
    'type', 
    'lbrace', 'rbrace', 'semi', 'inherits', 'times', 'larrow', 'plus', 'minus', 'divide',
    'identifier', 'colon', 'lparen', 'comma', 'rparen', 'integer', 'dot', 'new', 'string', 'false', 'true',
    'not', 'lt', 'le', 'equals', 'tilde', 'isvoid', 'at', 'if', 'then', 'else', 'fi', 'while', 'loop', 'pool',
    'case', 'of', 'esac', 'rarrow', 'let', 'in'
]

# lowest to highest precedence
# 'left'
# 'right'
# 'non-associative'
precedence = (
    ('right', 'larrow', 'in'),
    ('right', 'not', 'isvoid', 'tilde'),
    ('nonassoc', 'equals', 'lt', 'le'),
    ('left', 'plus', 'minus'),
    ('left', 'times', 'divide'),
    ('left', 'dot')
)

# Base class
class ASTNode(object):
    pass

# Building Blocks (terminals)
# These serve as the foundation for higher nodes in the AST
class ExpBaseValue(ASTNode):
    def __init__(self, lineno, val):
        self.lineno = lineno
        self.val = val

class ExpBool(ExpBaseValue):
    def __init__(self, lineno, val):
        super().__init__(lineno, val)
    def __repr__(self):
        return str(self.lineno) + '\n' + self.val

class ExpInt(ExpBaseValue):
    def __init__(self, lineno, val):
        super().__init__(lineno, val)
    def __repr__(self):
        return str(self.lineno) + '\n' + "integer\n" + str(self.val)

class ExpId(ASTNode):
    def __init__(self, id):
        self.lineno = id.lineno
        self.id = id
    def __repr__(self):
        return str(self.lineno) + '\n' + "identifier\n" + str(self.id)

class ExpString(ExpBaseValue):
    def __init__(self, lineno, val):
        super().__init__(lineno, val)
    def __repr__(self):
        return str(self.lineno) + '\n' + "string\n" + self.val

class TypeNT(ASTNode):
    def __init__(self, lineno, type):
        self.lineno = lineno
        self.type = type
    
    def __repr__(self):
        return str(self.lineno) + '\n' + self.type

class IdentifierNT(ASTNode):
    def __init__(self, lineno, identifier):
        self.lineno = lineno
        self.identifier = identifier
    def __repr__(self):
        return str(self.lineno) + '\n' + self.identifier

# All lists are similar
class List(ASTNode):
    def __init__(self, children):
        self.children = children
    
    def __repr__(self):
        if(isinstance(self.children, list)):
            l = ""
            k = 0
            for i, node in enumerate(self.children):
                l += repr(node)
                if(i != len(self.children) - 1):
                    l += '\n'
                k += 1
                    
            return l
        return repr(self.children)
    
class SizeList(List):
    def __init__(self, children):
        super().__init__(children) 
        self.size = 1 if not isinstance(children, list) else len([child for child in children if child != []])
    def __repr__(self):
        base_repr = super().__repr__()
        if(self.size == 0):
            return str(0)
        return str(self.size) +'\n'  + base_repr 

class LinenoList(List):
    def __init__(self, children, lineno):
        super().__init__(children)
        self.lineno = lineno
    def __repr__(self):
        base_repr = super().__repr__()
        return str(self.lineno) +'\n'  + base_repr 

class ExpUnaryOperator(ASTNode):
    def __init__(self, lineno, exp, token):
        self.lineno = lineno
        self.exp = exp
        self.token = token
    def __repr__(self):
        return str(self.lineno) + '\n' + self.token + '\n' + repr(self.exp)

class ExpOper(ASTNode):
    def __init__(self, lineno, operation, left, right):
        self.lineno = left.lineno
        self.oper = operation
        self.l = left
        self.r = right
    
    def __repr__(self):
        return str(self.lineno) + '\n' + self.oper + '\n' + repr(self.l) + '\n' + repr(self.r)

class Block(ASTNode):
    def __init__(self, lineno, children):
        self.lineno = lineno
        self.children = children
    def __repr__(self):
        return str(self.lineno) + '\n' + 'block' + '\n' + repr(self.children)

class ClassNoInherits(ASTNode):
    def __init__(self, lineno, typename, featurelist):
        self.lineno = lineno
        self.typename = typename
        self.featurelist = featurelist
    def __repr__(self):
        my_string = """{typename}
no_inherits
{featurelist}""".format(typename = self.typename, featurelist = self.featurelist)

        return my_string

class ClassInherits(ClassNoInherits):
    def __init__(self, lineno, typename, inheritsfrom, featurelist):
        super().__init__(lineno, typename, featurelist)
        self.inheritsfrom = inheritsfrom

    def __repr__(self):
        my_string = """{typename}
inherits
{inheritsfrom}
{featurelist}""".format(lineno = self.lineno, typename = self.typename, featurelist = self.featurelist, inheritsfrom = self.inheritsfrom)

        return my_string
    
# Features
class FeatureNoInit(ASTNode):
    def __init__(self, lineno, identifier_nt, type_nt):
        self.lineno = lineno
        self.identifier_nt = identifier_nt
        self.type_nt = type_nt
    
    def __repr__(self):
        return 'attribute_no_init' +'\n' + repr(self.identifier_nt) + '\n' + repr(self.type_nt)

class FeatureInit(FeatureNoInit):
    def __init__(self, lineno, identifier_nt, type_nt, initializedto):
        super().__init__(lineno, identifier_nt, type_nt)
        self.initializedto = initializedto
    
    def __repr__(self):
        return 'attribute_init' +'\n'+ repr(self.identifier_nt) + '\n' + repr(self.type_nt) + '\n' + repr(self.initializedto)

class FeatureMethod(ASTNode):
    def __init__(self, lineno, identifier_nt, formal_list, type_nt, exp):
        self.lineno = lineno
        self.identifier_nt = identifier_nt
        self.formal_list = formal_list
        self.type_nt = type_nt
        self.exp = exp
    def __repr__(self):
        return 'method\n' + repr(self.identifier_nt) + '\n' + repr(self.formal_list) + '\n' + repr(self.type_nt) + '\n' + repr(self.exp)

# Expressions
class ExpDynamic(ASTNode): 
    def __init__(self, lineno, exp, identifier_nt, arg_list,):
        self.lineno = lineno
        self.exp = exp
        self.identifier_nt = identifier_nt
        self.arg_list = arg_list

    def __repr__(self):
        return str(self.lineno) + '\ndynamic_dispatch\n' + repr(self.exp) + '\n'+ repr(self.identifier_nt) + '\n' + repr(self.arg_list) 

class ExpStatic(ASTNode): 
    def __init__(self, lineno, exp, type_nt, identifier_nt, arg_list,):
        self.lineno = lineno
        self.exp = exp
        self.type_nt = type_nt
        self.identifier_nt = identifier_nt
        self.arg_list = arg_list

    def __repr__(self):
        return str(self.lineno) + '\nstatic_dispatch\n' + repr(self.exp) + '\n' + repr(self.type_nt)+  '\n'+ repr(self.identifier_nt) + '\n' + repr(self.arg_list) 

class ExpSelfDispatch(ASTNode): 
    def __init__(self, lineno, identifier_nt, arg_list):
        self.lineno = lineno
        self.identifier_nt = identifier_nt
        self.arg_list = arg_list

    def __repr__(self):
        return str(self.lineno) + '\nself_dispatch'+ '\n'+ repr(self.identifier_nt) + '\n' + repr(self.arg_list) 

class ExpNew(ASTNode):
    def __init__(self, lineno, type_nt):
        self.type_nt = type_nt
        self.lineno = lineno
    def __repr__(self):
        return str(self.lineno) + '\nnew\n' + repr(self.type_nt)

class Formal(ASTNode):
    def __init__(self, lineno, identifier_nt, type_nt):
        self.lineno = lineno
        self.identifier_nt = identifier_nt
        self.type_nt = type_nt
    
    def __repr__(self):
        return repr(self.identifier_nt) + '\n' + repr(self.type_nt)

class ArgExp(ASTNode):
    def __init__(self,arg):
        self.arg = arg

    def __repr__(self):
        return repr(self.arg)

class ExpAssign(ASTNode):
    def __init__(self, lineno, identifier_nt, exp):
        self.identifier_nt = identifier_nt
        self.exp = exp
        self.lineno = lineno

    def __repr__(self):
        return str(self.lineno) + '\n' + "assign" + '\n' + repr(self.identifier_nt) + '\n' + repr(self.exp)

# Control Flow nodes
class ExpIf(ASTNode):
    def __init__(self, lineno, condition, ifbody, elsebody):
        self.lineno = lineno
        self.condition = condition
        self.ifbody = ifbody
        self.elsebody = elsebody
    def __repr__(self):
        return str(self.lineno) + '\nif' + '\n' + repr(self.condition) + '\n' + repr(self.ifbody) + '\n' + repr(self.elsebody)

class ExpWhile(ASTNode):
    def __init__(self, lineno, condition, body):
        self.lineno = lineno
        self.condition = condition
        self.body = body
    def __repr__(self) -> str:
        return str(self.lineno) + '\nwhile\n' + repr(self.condition) + '\n' + repr(self.body)

class ExpCase(ASTNode):
    def __init__(self, lineno, exp, caselist):
        self.lineno = lineno
        self.exp = exp
        self.caselist = caselist
    def __repr__(self):
        return str(self.lineno) + '\ncase\n' + repr(self.exp) + '\n'+ repr(self.caselist) 

class CaseItem(ASTNode):
    def __init__(self, identifier_nt, type_nt, exp):
        self.identifier_nt = identifier_nt
        self.type_nt = type_nt
        self.exp = exp
    
    def __repr__(self):
        return repr(self.identifier_nt) + '\n' + repr(self.type_nt)  + '\n' + repr(self.exp)

# Let Nodes
class ExpLet(ASTNode):
    def __init__(self, lineno, letlist, body):
        self.lineno = lineno
        self.letlist = letlist
        self.body = body
    def __repr__(self):
        return str(self.lineno) + '\n' + "let" + '\n' + repr(self.letlist) + '\n' + repr(self.body) 

class LetNoinit(ASTNode):
    def __init__(self, lineno, identifier_nt, type_nt):
        self.lineno = lineno
        self.identifier_nt = identifier_nt
        self.type_nt = type_nt
    def __repr__(self):
        return "let_binding_no_init" + '\n' + repr(self.identifier_nt) + '\n' + repr(self.type_nt)

class LetInit(LetNoinit):
    def __init__(self, lineno, identifier_nt, type_nt, exp):
        super().__init__(lineno, identifier_nt, type_nt)
        self.exp = exp
    def __repr__(self):
        return "let_binding_init" + '\n' + repr(self.identifier_nt) + '\n' + repr(self.type_nt) + '\n' + repr(self.exp)

def p_program(p):
    'program : classlist'
    p[0] = p[1]

def p_classlist(p):
    '''classlist : classlist_some
                 | classlist_none'''
    p[0] = SizeList(p[1])

def p_classlist_cont(p):
    '''classlist_cont : classlist_some
                      | classlist_none
    '''
    p[0] = p[1]

def p_classlist_some(p):
    'classlist_some : classdef semi classlist_cont'
    p[0] = [ p[1] ] + p[3]

def p_classlist_none(p):
    'classlist_none : '
    p[0] = []

def p_class_noinherits(p):
    'classdef : class type_nt lbrace featurelist rbrace'
    p[0] = ClassNoInherits(p.lineno(1), p[2], p[4])

def p_class_inherits(p):
    'classdef : class type_nt inherits type_nt lbrace featurelist rbrace'
    p[0] = ClassInherits(p.lineno(1), p[2], p[4], p[6])

def p_featurelist(p):
    '''featurelist : featurelist_some
                   | featurelist_none'''
    p[0] = SizeList(p[1])

def p_featurelist_cont(p):
    '''featurelist_cont : featurelist_some
                   '''
    p[0] = p[1]

def p_feature_list_some(p):
    '''featurelist_some : feature semi
       featurelist_some : feature semi featurelist_cont
    '''

    if len(p) == 4:
        p[0] = [ p[1] ] + p[3]
    else:
        p[0] = [p[1]]

def p_feature_list_none(p):
    'featurelist_none : '
    p[0] = []

def p_feature_attribute_noinit(p):
    'feature : identifier_nt colon type_nt'
    p[0] = FeatureNoInit(p.lineno(1), p[1], p[3])

def p_feature_attribute_init(p):
    'feature : identifier_nt colon type_nt larrow exp'
    p[0] = FeatureInit(p.lineno(1), p[1], p[3], p[5])

def p_type(p):
    'type_nt : type'
    p[0] = TypeNT(p.lineno(1), p[1])

def p_identifier(p):
    'identifier_nt : identifier'
    p[0] = IdentifierNT(p.lineno(1), p[1])

def p_feature_method(p):
    'feature : identifier_nt lparen formal_list rparen colon type_nt lbrace exp rbrace'
    p[0] = FeatureMethod(p.lineno(1), p[1], p[3], p[6], p[8])

# For some reason I couldn't consolidate these into one
def p_exp_plus(p):
    'exp : exp plus exp'
    p[0] = ExpOper(p.lineno(1), "plus", p[1], p[3])

def p_exp_minus(p):
    'exp : exp minus exp'
    p[0] = ExpOper(p.lineno(1), "minus", p[1], p[3])

def p_exp_times(p):
    'exp : exp times exp'
    p[0] = ExpOper(p.lineno(1), "times", p[1], p[3])

def p_exp_divide(p):
    'exp : exp divide exp'
    p[0] = ExpOper(p.lineno(1), "divide", p[1], p[3])

def p_exp_lt(p):
    'exp : exp lt exp'
    p[0] = ExpOper(p.lineno(1), "lt", p[1], p[3])

def p_exp_le(p):
    'exp : exp le exp'
    p[0] = ExpOper(p.lineno(1), "le", p[1], p[3])

def p_exp_eq(p):
    'exp : exp equals exp'
    p[0] = ExpOper(p.lineno(1), "eq", p[1], p[3])

def p_exp_string(p):
    'exp : string'
    p[0] = ExpString(p.lineno(1), p[1])

def p_exp_isvoid(p):
    'exp : isvoid exp'
    p[0] = ExpUnaryOperator(p.lineno(1), p[2], 'isvoid')

def p_exp_bool_false(p):
    '''exp : false'''
    p[0] = ExpBool(p.lineno(1), 'false')

def p_exp_bool_true(p):
    '''exp : true'''
    p[0] = ExpBool(p.lineno(1), 'true')
    
def p_exp_not(p):
    'exp : not exp'
    p[0] = ExpUnaryOperator(p.lineno(1), p[2], "not")

def p_exp_negate(p):
    'exp : tilde exp'
    p[0] = ExpUnaryOperator(p.lineno(1), p[2], "negate")

def p_exp_integer(p):
    'exp : integer'
    p[0] = ExpInt(p.lineno(1), p[1])

def p_exp_parens(p):
    'exp : lparen exp rparen'
    p[0] = p[2]

def p_exp_dynamic(p):
    'exp : exp dot identifier_nt lparen arglist rparen'
    p[0] = ExpDynamic(p.lineno(2), p[1], p[3], p[5])

def p_exp_static(p):
    'exp : exp at type_nt dot identifier_nt lparen arglist rparen'
    p[0] = ExpStatic(p.lineno(2), p[1], p[3], p[5], p[7])
def p_exp_self_dispatch(p):
    'exp : identifier_nt lparen arglist rparen'
    p[0] = ExpSelfDispatch(p.lineno(2), p[1], p[3])

def p_exp_assign(p):
    'exp : identifier_nt larrow exp'
    p[0] = ExpAssign((p[1].lineno), p[1], p[3])
def p_exp_new(p):
    'exp : new type_nt'
    p[0] = ExpNew(p.lineno(1), p[2])

def p_exp_ident(p):
    'exp : identifier_nt'
    p[0] = ExpId(p[1])

def p_arglist(p):
    '''arglist : arglist_some
               | arglist_none
    '''
    p[0] = SizeList(p[1])

def p_arglist_some(p):
    '''arglist_some : arg comma arglist_some
                    | arg
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_arg_exp(p):
    'arg : exp'
    p[0] = ArgExp(p[1])

def p_arglist_none(p):
    'arglist_none : '
    p[0] = []

def p_formallist(p):
    '''formal_list : formal_list_some
                   | formal_list_none'''
    p[0] = SizeList(p[1])

def p_formal_list_some(p):
    '''formal_list_some : formal comma formal_list_some
                        | formal
    '''
    if len(p) == 4:
        p[0] = [ p[1] ] + p[3]
    else:
        p[0] = [p[1]]

def p_formal_list_none(p):
    'formal_list_none : '
    p[0] = []

def p_formal(p):
    'formal : identifier_nt colon type_nt'
    p[0] = Formal(p.lineno(1), p[1], p[3])

# Cool doesn't have statements but hey
def p_block(p):
    'exp : lbrace statementlist rbrace'
    p[0] = Block(p.lineno(1), p[2])

def p_statementlist(p):
    '''statementlist : statementlist_some
                     | statementlist_none'''
    p[0] = SizeList(p[1])

def p_statementlist_cont(p):
    '''statementlist_cont : statementlist_some
                          | statementlist_none'''
    p[0] = p[1]

def p_statementlist_some(p):
    '''statementlist_some : exp semi statementlist_cont
                          | exp
    '''
    if len(p) == 4:
        p[0] = [ p[1] ] + p[3]
    else:
        p[0] = [p[1]]

def p_statementlist_none(p):
    'statementlist_none : '
    p[0] = []

# Control Flow

def p_exp_if(p):
    'exp : if exp then exp else exp fi'
    p[0] = ExpIf(p.lineno(1), p[2], p[4], p[6])

def p_exp_while(p):
    'exp : while exp loop exp pool'
    p[0] = ExpWhile(p.lineno(1), p[2], p[4])

def p_exp_case(p):
    'exp : case exp of caselist esac'
    p[0] = ExpCase(p.lineno(1), p[2], p[4])

def p_caselist(p):
    'caselist : caselist_some'
    p[0] = SizeList(p[1])

def p_caselist_some(p):
    'caselist_some : caseitem semi caselist_cont'
    p[0] = [p[1]] + p[3]

def p_castlist_cont(p):
    '''caselist_cont : caselist_some
                     | caselist_none
    '''
    p[0] = p[1]
def p_caselist_none(p):
    'caselist_none : '
    p[0] = []

def p_caseitem(p):
    'caseitem : identifier_nt colon type_nt rarrow exp'
    p[0] = CaseItem(p[1], p[3], p[5])

# Let expressions

def p_exp_let(p):
    'exp : let letlist in exp'
    p[0] = ExpLet(p.lineno(1), p[2], p[4])

def p_letlist(p):
    'letlist : letlist_some'
    p[0] = SizeList(p[1])

def p_letlist_some(p): 
    '''letlist_some : letvar
                    | letvar comma letlist_some'''
    
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_letvar_noinit(p):
    'letvar : identifier_nt colon type_nt'
    p[0] = LetNoinit(p.lineno(1), p[1], p[3])

def p_letvar_init(p):
    'letvar : identifier_nt colon type_nt larrow exp'
    p[0] = LetInit(p.lineno(1), p[1], p[3], p[5])

def p_error(p):
    if p:
        print("ERROR:", p.lineno, ": Parser: parse error near", p.type)
        exit(1)
    else:
        print("ERROR: Syntax error at EOF")

lexer = Lexer()
parser = yacc.yacc()
ast = yacc.parse(lexer = lexer)

ast_filename = (sys.argv[1])[:-4] + "-ast"
fout = open(ast_filename, 'w')
fout.write(repr(ast))
if(repr(ast)[-1] != '\n'):
    fout.write('\n')
fout.close()

