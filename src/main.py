import sys
import aast as AAST

import class_map as CMAP
import impl_map as IMAP

ast_lines = []
class_list = []

def read_identifier():
    lineno = get_line()
    ident_name = get_line()
    return AAST.Identifier(lineno, ident_name)

def read_exp():
    line_number = get_line() # no arithmetic, no need for int casting
    exp_name = get_line()

    if exp_name == 'assign':
        assignee = read_identifier()
        rhs = read_exp()
        return AAST.Assign(line_number, assignee, rhs)
    elif exp_name == 'dynamic_dispatch':
        obj_name = read_exp()
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())
        return AAST.Dynamic_Dispatch(line_number, obj_name, method_name, args)
    
    elif exp_name == "static_dispatch":
        obj_name = read_exp()
        type_name = read_identifier() # parent
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())
        return AAST.Static_Dispatch(line_number, obj_name, type_name, method_name, args)
    
    elif exp_name == "self_dispatch":
        method_name = read_identifier()
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())
        return AAST.Self_Dispatch(line_number,method_name, args)
    elif exp_name == "if":
        predicate = read_exp()
        then_body = read_exp()
        else_body = read_exp()
        return AAST.If(line_number,predicate, then_body, else_body)
    
    elif exp_name == "while":
        predicate = read_exp()
        body_exp = read_exp()
        return AAST.While(line_number, predicate, body_exp)
    elif exp_name == "block":
        num_exps = int(get_line())
        exps = []
        for i in range(num_exps):
            exps.append(read_exp())
        return AAST.Block(line_number, exps)
    elif exp_name == "new":
        return AAST.New(line_number, read_identifier())
    elif exp_name == "isvoid":
        return AAST.Isvoid(line_number, read_exp())
    elif exp_name == "plus":
        return AAST.Plus(line_number, read_exp(), read_exp())

    elif exp_name == "minus":
        return AAST.Minus(line_number, read_exp(), read_exp())
    elif exp_name == "times":
        return AAST.Times(line_number, read_exp(), read_exp())
    elif exp_name == "divide":
        return AAST.Divide(line_number, read_exp(), read_exp())
    elif exp_name == "lt":
        return AAST.LessThan(line_number, read_exp(), read_exp())
    elif exp_name == "le":
        return AAST.LessThanEqual(line_number, read_exp(), read_exp())
    elif exp_name == "eq":
        return AAST.Equal(line_number, read_exp(), read_exp())
    elif exp_name == "not":
        return AAST.Not(line_number, read_exp())
    elif exp_name == "negate":
        return AAST.Negate(line_number, read_exp())
    elif exp_name == "integer":
        return AAST.Integer(line_number, int(get_line()))
    elif exp_name == "string":
        return AAST.String(line_number, get_line())
    elif exp_name == "identifier":
        return AAST.IdentifierExp(line_number, read_identifier())
    elif exp_name == "true":
        return AAST.TrueExp(line_number)
    elif exp_name == "false":
        return AAST.FalseExp(line_number)
    elif exp_name == "let":
        let_num = int(get_line())
        letlist = []
        for i in range(let_num):
            let_type = get_line()
            ident_name = read_identifier()
            type_name = read_identifier()
            if let_type == "let_binding_init":
                let_exp = read_exp()
                let_node = AAST.LetInit(line_number, ident_name, type_name, let_exp)
            else:
                let_node = AAST.LetNoinit(line_number, ident_name, type_name)
            letlist.append(let_node)
        let_body = read_exp() 
        return AAST.Let(line_number, letlist, let_body)
    elif exp_name == "case":
        caselist = []
        exp = read_exp()
        let_num = int(get_line())

        for i in range(let_num):
            ident_name = read_identifier()
            type_name = read_identifier()
            body_exp = read_exp()
            caselist.append(AAST.CaseItem(ident_name, type_name, body_exp))
        return AAST.ExpCase(line_number, exp, caselist)

def get_line():
    return ast_lines.pop(0)

def read_formal():
    formal_name = read_identifier()
    formal_type = read_identifier()
    return AAST.Formal(formal_name, formal_type)

def read_feature():
    feature_kind = get_line()
    if feature_kind == "attribute_no_init":
        feature_name = read_identifier()
        feature_type = read_identifier()
        return AAST.Attribute(feature_name, feature_type, False, None)
    elif feature_kind == "attribute_init":
        feature_name = read_identifier()
        feature_type = read_identifier()
        feature_init = read_exp()
        return AAST.Attribute(feature_name, feature_type, True, feature_init)
    elif feature_kind == "method":
        feature_name = read_identifier()
        formals_list = []
        num_formals = int(get_line())
        for i in range(num_formals):
            formals_list.append(read_formal())
        feature_type = read_identifier()
        feature_body = read_exp()
        return AAST.Method(feature_name, formals_list,  feature_type, feature_body)

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

#_name_iden, _inherits_iden, _attributes,_methods, _features
    for i in range(num_features):
        features_list.append(read_feature())
    for i in features_list:
        if isinstance(i, AAST.Attribute):
            attr_list.append(i)
        else: 
            method_list.append(i)
    return AAST.Class(class_info, parent,attr_list, method_list, features_list)

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

    (cdict_text, cdict, class_list, dict_copy) = CMAP.class_map(ast)
    stack = [cdict]
    impl_map = IMAP.impl_map(stack, cdict, class_list, dict_copy)

    out_file = open(sys.argv[1][:-4] + "-type2", "w")
    # for i in ast:
    #     out_file.write(str(i))
    #out_file.write(cdict_text)
    out_file.write(impl_map)
    out_file.close()

if __name__ == '__main__':
    main()