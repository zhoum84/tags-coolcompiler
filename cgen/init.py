import aast as AAST

# Given contents of a .cl-type file, initialize data structures
# required to hold all necessary information
  
type_lines = []
class_map = {}
implementation_map = {}
ast = []

class_names = []
constants = []

def get_line():
    return type_lines.pop(0)

def read_identifier(exp_type):
    lineno = get_line()
    name = get_line()
    return AAST.Variable(lineno, exp_type, name)

def read_exp():
    lineno = get_line()
    exp_type = get_line()
    exp_name = get_line()
    if exp_name == "integer":
        return AAST.Int(lineno, exp_type, int(get_line()))
    elif exp_name == "string":
        str_val = get_line()
        constants.append(str_val)
        return AAST.String(lineno, exp_type, str_val)
    elif exp_name == "true":
        return AAST.TrueExp(lineno, exp_type, )
    elif exp_name == "false":
        return AAST.FalseExp(lineno, exp_type, )
    elif exp_name == "identifier":
        return read_identifier(exp_type)
    elif exp_name == "assign":

        assignee = read_identifier(exp_type)
        rhs = read_exp()
        return AAST.Assign(lineno, exp_type, assignee, rhs)
    elif exp_name == "plus":
        return AAST.Plus(lineno, exp_type, read_exp(), read_exp())
    elif exp_name == "minus":
        return AAST.Minus(lineno, exp_type, read_exp(), read_exp())
    elif exp_name == "times":
        return AAST.Times(lineno, exp_type, read_exp(), read_exp())
    elif exp_name == "divide":
        constants.append(f"ERROR: {lineno}: Exception: division by zero")
        return AAST.Divide(lineno, exp_type, read_exp(), read_exp())
    elif exp_name == "lt":
        return AAST.LessThan(lineno, exp_type, read_exp(), read_exp())
    elif exp_name == "le":
        return AAST.LessThanEqual(lineno, exp_type, read_exp(), read_exp())
    elif exp_name == "eq":
        return AAST.Equal(lineno, exp_type, read_exp(), read_exp())
    elif exp_name == "not":
        return AAST.Not(lineno, exp_type, read_exp())
    elif exp_name == "negate":
        return AAST.Negate(lineno, exp_type, read_exp())
    elif exp_name == "isvoid":
        return AAST.Isvoid(lineno, exp_type, read_exp())
    elif exp_name == "new":
        new_lineno = get_line()
        return AAST.New(new_lineno, get_line())
    elif exp_name == "block":
        num_exps = int(get_line())
        exps = []
        for i in range(num_exps):
            exps.append(read_exp())
        return AAST.Block(lineno, exp_type, exps)
    elif exp_name == "if":
        predicate = read_exp()
        then_body = read_exp()
        else_body = read_exp()
        return AAST.If(lineno, exp_type, predicate, then_body, else_body)
    elif exp_name == "internal":
        name = get_line()
        if name == "String.substr":
            constants.append("ERROR: 0: Exception: String.substr out of range")
        return AAST.Internal(lineno, exp_type, name)
    elif exp_name == "self_dispatch":
        method_name = read_identifier(exp_type)
        num_args = int(get_line())
        args = []
        for i in range(num_args):
            args.append(read_exp())
        return AAST.Dynamic_Dispatch(lineno, exp_type, AAST.Variable(0, "SELF_TYPE", "self"), method_name.name, args)
    elif exp_name == "dynamic_dispatch":
        obj_name = read_exp()
        method_name = read_identifier(exp_type)
        num_args = int(get_line())
        args = []
        constants.append(f"ERROR: {lineno}: Exception: dispatch on void")

        for i in range(num_args):
            args.append(read_exp())
        return AAST.Dynamic_Dispatch(lineno, exp_type, obj_name, method_name.name, args)
    elif exp_name == "static_dispatch":
        obj_name = read_exp()
        type_name = read_identifier(exp_type) # parent
        method_name = read_identifier(exp_type)
        num_args = int(get_line())
        args = []
        constants.append(f"ERROR: {lineno}: Exception: static dispatch on void")
        for i in range(num_args):
            args.append(read_exp())
        return AAST.Static_Dispatch(lineno, exp_type, obj_name, method_name.name, args, type_name.name)
    elif exp_name == "let":
        let_num = int(get_line())
        letlist = []
        for i in range(let_num):
            let_type = get_line()
            ident_name = read_identifier(exp_type).name
            type_name = read_identifier(exp_type).name
            if let_type == "let_binding_init":
                let_exp = read_exp()
                let_node = AAST.LetInit(lineno, exp_type, ident_name, type_name, let_exp)
            else:
                let_node = AAST.LetNoinit(lineno, exp_type, ident_name, type_name)
            letlist.append(let_node)
        let_body = read_exp() 
        return AAST.Let(lineno, exp_type, letlist, let_body)
    elif exp_name == "while":
        predicate = read_exp()
        body_exp = read_exp()
        return AAST.While(lineno, exp_type, predicate, body_exp)
    elif exp_name == "case":
        caselist = []
        exp = read_exp()
        let_num = int(get_line())

        constants.append(f"ERROR: {lineno}: Exception: case without matching branch")
        constants.append(f"ERROR: {lineno}: Exception: case on void")
        for i in range(let_num):
            ident_name = read_identifier(exp_type)
            type_name = read_identifier(exp_type)
            body_exp = read_exp()
            caselist.append(AAST.CaseItem(lineno, exp_type, ident_name, type_name, body_exp))

        return AAST.ExpCase(lineno, exp_type, exp, caselist)


    
def read_class():
    class_attr = []
    class_name = get_line()
    num_attr = get_line()
    for i in range(int(num_attr)):
        init_type = get_line()
        attr_name = get_line()
        attr_type = get_line()
        exp = None
        if init_type == "initializer":
            exp = read_exp()
        class_attr.append(AAST.Attribute(attr_name, attr_type, exp))
        class_attr[-1].num_temps = temps(exp)
    class_names.append(class_name)
    class_map[class_name] = class_attr

def load_class_map(lines):
    global class_map
    global type_lines
    type_lines = lines

    get_line() # should be "class_map"
    num_classes = get_line()
    for cls in range(int(num_classes)):
        read_class()
    return (class_map, class_names)

def load_implementation_map_and_ast(lines):
    global type_lines
    type_lines = lines

    get_line() # should be "implementation_map"
    num_classes = get_line()
    for cls in range(int(num_classes)):
        read_class_methods()
    
    return (implementation_map, ast, list(set(constants)))
    
    

def load_parent_map(lines):
    global type_lines
    type_lines = lines
    get_line() # should say parent_map
    num_classes = int(get_line())
    parent_map = {}
    child_map = {}
    for i in range(num_classes):
        child = get_line()
        parent = get_line()
        parent_map[child] = parent
        if parent in child_map:
            child_map[parent].append(child)
        else:
            child_map[parent] = [child]
        #child_map[parent] = child
    return parent_map, child_map

method_labels = []
def read_class_methods():
    class_methods = []
    class_name = get_line()
    num_methods = get_line()
    for i in range(int(num_methods)):
        formals = []
        method_name = get_line()
        num_formals = get_line()
        for j in range(int(num_formals)):
            formals.append(get_line())
        class_origin = get_line()
        method_body = read_exp()
        method_label = f'{class_origin}.{method_name}'
        if not method_label in method_labels:
            ast.append(AAST.MethodImplementation(class_name, method_name, formals, method_label, method_body))
            method_labels.append(method_label) 
            ast[-1].num_temps = temps(ast[-1])
        class_methods.append(AAST.Method(method_name, formals,method_label))
    implementation_map[class_name] = class_methods


def temps(e):
    if isinstance(e, AAST.MethodImplementation):
        return temps(e.exp)
    elif isinstance(e, AAST.Negate):
        return 1 + temps(e.exp)
    if isinstance(e, AAST.Arithmetic):
        return max(temps(e.e1), 1 + temps(e.e2))
    elif isinstance(e, AAST.Compare):
        return max(temps(e.e1), 1 + temps(e.e2))
    elif isinstance(e, AAST.Internal):
        return 1
    elif isinstance(e, AAST.Block):
        t = []
        for i, exp in enumerate(e.exp_list):
            t.append(temps(exp))
        return max(t)
    elif isinstance(e, AAST.Int):
        return 1
    elif isinstance(e, AAST.TrueExp):
        return 1
    elif isinstance(e, AAST.FalseExp):
        return 1
    elif isinstance(e, AAST.Let):
        t = []
        for i, exp in enumerate(e.letlist):
            t.append(temps(exp) + i)
        t.append(temps(e.body) + len(e.letlist))
        return 1 + max(t)

    elif isinstance(e, AAST.Dynamic_Dispatch):
        return len(e.formals) + 1
    elif isinstance(e, AAST.If):
        return max(temps(e.predicate), temps(e.then_body), temps(e.else_body))
    elif isinstance(e, AAST.ExpCase):
        t = []
        for c in e.caselist:
            t.append(temps(c))
        return max(t) + temps(e.exp)
    elif isinstance(e, AAST.Assign):
        return temps(e.exp)
    elif isinstance(e, AAST.LetInit):
        return temps(e.exp)
    else:
        return 1
