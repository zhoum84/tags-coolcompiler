import sys
import pprint
ast_lines = []

class_list = []

def get_line():
    return ast_lines.pop(0)

def read_exp():
    line_number = get_line() # no arithmetic, no need for int casting
    exp_name = get_line()

    if exp_name == 'assign':
        assignee = read_identifier()
        rhs = read_exp()
        return (exp_name, assignee, rhs)
    elif exp_name == 'dynamic_dispatch':
        obj_name = read_exp()
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())
        return (exp_name, obj_name, method_name, args)
    
    elif exp_name == "static_dispatch":
        obj_name = read_exp()
        type_name = read_identifier() # parent
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())
        return (exp_name, obj_name, type_name, method_name, args)
    
    elif exp_name == "self_dispatch":
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())
        return (exp_name,method_name, args)
    elif exp_name == "if":
        predicate = read_exp()
        then_body = read_exp()
        else_body = read_exp()
        return (exp_name, predicate, then_body, else_body)
    
    elif exp_name == "while":
        predicate = read_exp()
        body_exp = read_exp()
        return (exp_name, predicate, body_exp)
    elif exp_name == "block":
        num_exps = int(get_line())
        exps = []
        for i in range(num_args):
            args.append(read_exp())
        return (exp_name, exps)
    elif exp_name == "new":
        return (exp_name, read_identifier())
    elif exp_name == "isvoid":
        return (exp_name, read_exp())
    elif exp_name == "plus":
        return (exp_name, read_exp(), read_exp())

    elif exp_name == "minus":
        return (exp_name, read_exp(), read_exp())
    elif exp_name == "times":
        return (exp_name, read_exp(), read_exp())
    elif exp_name == "divide":
        return (exp_name, read_exp(), read_exp())
    elif exp_name == "lt":
        return (exp_name, read_exp(), read_exp())
    elif exp_name == "le":
        return (exp_name, read_exp(), read_exp())
    elif exp_name == "eq":
        return (exp_name, read_exp(), read_exp())
    elif exp_name == "not":
        return (exp_name, read_exp())
    elif exp_name == "negate":
        return (exp_name, read_exp())
    elif exp_name == "integer":
        return (exp_name, int(get_line()))
    elif exp_name == "string":
        return (exp_name, get_line())
    elif exp_name == "identifier":
        return (exp_name, read_identifier())
    
    elif exp_name == "true":
        return (exp_name)
    elif exp_name == "false":
        return (exp_name)

def read_formal():
    formal_name = read_identifier()
    formal_type = read_identifier()
    return (formal_name, formal_type)

class ASTNode(object):
    pass

class Assign(ASTNode):
    def __init__(self, _assignee, _rhs):
        self.assignee = _assignee
        self.rhs = _rhs
class Add(ASTNode):
    def __init__(self, _lhs, _rhs):
        self.lhs = _lhs
        self.rhs = _rhs


class Class(object):
    #attributes, methods, inherits/
    pass
def read_feature():
    feature_kind = get_line()
    if feature_kind == "attribute_no_init":
        feature_name = read_identifier()
        feature_type = read_identifier()
        return (feature_kind, feature_name, feature_type)
    elif feature_kind == "attribute_init":
        feature_name = read_identifier()
        feature_type = read_identifier()
        feature_init = read_exp()
        return (feature_kind, feature_name, feature_type, feature_init)
    elif feature_kind == "method":
        feature_name = read_identifier()
        formals_list = []
        num_formals = int(get_line())
        for i in range(num_formals):
            formals_list.append(read_formal())
        feature_type = read_identifier()
        feature_body = read_exp()
        return (feature_kind, feature_name, feature_type, formals_list, feature_body)
    

def read_identifier():
    lineno = get_line()
    ident_name = get_line()
    return (lineno, ident_name)

def read_class():
    class_info = read_identifier()
    check_inherits = get_line()
    parent = None
    if check_inherits == "inherits":
        parent = read_identifier()

    num_features = int(get_line())
    features_list = []
    attr_list = []
    method_list = []

    for i in range(num_features):
        features_list.append(read_feature())

    return (class_info, parent, features_list)
def read_ast():
    num_classes = int(get_line())
    for i in range(num_classes):
        class_list.append(read_class())
    return class_list
def main():
    global ast_lines
    if len(sys.argv) < 2: 
        print("Specify .cl-ast input file.\n")
        exit()
    with open(sys.argv[1]) as f:
        ast_lines = [l.rstrip() for l in f.readlines()]

    ast = read_ast()
    pprint.pprint(ast)

if __name__ == '__main__':
    main()