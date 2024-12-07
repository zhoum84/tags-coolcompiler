import aast as AAST
from typing import Dict
import class_map as CMAP
user_classes = []

# base_classes = ["Bool", "IO", "Int", "Object", "String"]

#bool_methods = AAST.Method("abort", [], default_ident("Object"), AAST.Expression(0))

# full_dict is a class_map with all 
def impl_map(stack, cdict: Dict[str, AAST.Class], class_list, full_dict):
    # class_list should be sorted already
    impl_map = "implementation_map\n" + str(len(class_list)) + '\n'

    symbol_table = (create_symbol_table(full_dict))
    for (key, cls) in sorted(cdict.items()):
        impl_map += key + '\n'
        all_methods = (CMAP.get_parent_methods(cls, cdict))
        impl_map += str(len(all_methods)) +'\n'
        for method in all_methods:#cls.methods
            impl_map += method.method_name.ident + '\n'
            impl_map += str(len(method.formals)) +'\n'
            for formal in method.formals:
                impl_map += formal.formal_name.ident + '\n'
            impl_map += get_parent(cls, method.method_name.ident, full_dict) + '\n' # parent
            # if isinstance(method.body, AAST.InternalExpression):
            # # impl_map += str(method.body_exp.line_num) +'\n'
            # # impl_map += str(method.method_type.ident) + '\n'
            #     impl_map += str(method.body_exp)
            # else:

            add_formals(symbol_table, cls, method.formals)

            if isinstance(method.body_exp, AAST.InternalExpression):
                impl_map += str(method.body_exp.line_num) + '\n' # line+num
                impl_map += tc(method.body_exp, full_dict) + '\n' # type
                impl_map += str(method.body_exp.ident) + '\n' # identifier
                impl_map += str(method.body_exp.name.ident) + '\n'
            elif hasattr(method.body_exp, "val"):
                impl_map += str(method.body_exp.line_num) + '\n' # line+num
                impl_map += tc(method.body_exp, full_dict) + '\n' # type
                impl_map += str(method.body_exp.ident) + '\n' # identifier
                impl_map += str(method.body_exp.val) + '\n'
            else:
                method.body_exp.exp_type = tc(method.body_exp, symbol_table[cls.name_iden.ident])
                #impl_map += tc(method.body_exp, full_dict) + '\n'
                impl_map += str(method.body_exp)
            #impl_map += str(method.body_exp.)
            #impl_map += str(method.body_exp)
            remove_formals(symbol_table, cls, method.formals)


    return impl_map

def get_parent(cls, method_name, cdict):
    if cls.inherits_iden is None:
        return cls.name_iden.ident
    else:
        parent = cdict[cls.inherits_iden.ident]
        for method in parent.methods:
            # Check if method is inherited from parent
            # If it is, must check parent's inheritance 
            if method.method_name.ident == method_name:

                return get_parent(parent, method_name, cdict)
            # else:
            #     return cls.inherits_iden.ident
            # If it isn't, just return the original class name
        return cls.name_iden.ident


# Each symbol is in a class
# Symbols are part of a class
# (symbol, class) is the input
# Each class has its own symbol table

def create_symbol_table(class_map: dict[str, AAST.Class]):

    base_symbol_table = {cls_name : {} for cls_name in class_map.keys()}
    for cls_name, cls in class_map.items():
        for method in cls.methods:
            base_symbol_table[cls_name][method.method_name.ident] = method
        for attr in cls.attributes:
            base_symbol_table[cls_name][attr.attr_name.ident] = attr

    return base_symbol_table

def add_formals(symbol_table, cls: AAST.Class, formals: list[AAST.Formal]):
    for formal in formals:
        #print(type(symbol_table[cls.name_iden.ident]))
        #print(formal.formal_name.ident)
        symbol_table[cls.name_iden.ident][formal.formal_name.ident] = formal

def remove_formals(symbol_table, cls, formals: list[AAST.Formal]):
    for formal in formals:
        symbol_table[cls.name_iden.ident].pop(formal.formal_name.ident, None)
        #pass
def tc( astnode, symbol_table = {}):
    if isinstance(astnode, AAST.Let):
        # push new environment
        if astnode.ident in symbol_table:
            symbol_table[astnode.ident].push( (astnode.ident, astnode.typ) )
        else:
            symbol_table[astnode.ident] = [ (astnode.ident, astnode.typ) ]

        t1 = tc( astnode.exp, symbol_table )

        symbol_table[astnode.ident].pop()
    
        astnode.exp_type = t1

        return t1

    elif isinstance(astnode, AAST.String):
        return "String"

    elif isinstance(astnode, AAST.Integer):
        return "Int"
    elif isinstance(astnode, AAST.TrueExp):
        return "Bool"
    elif isinstance(astnode, AAST.FalseExp):
        return "Bool"
    elif isinstance(astnode, AAST.IdentifierExp):
        if not astnode.ident.ident in symbol_table:
            print("ERROR: " + astnode.ident.line_num + ": Unbound identifier " + astnode.ident.ident)
            exit()
        print(type(symbol_table[astnode.ident.ident]))
        return symbol_table[astnode.ident.ident].attr_type.ident

    elif isinstance(astnode, AAST.Identifier):
        if not astnode.ident_name in symbol_table:
            raise Exception ("ERROR: Unbound identifier " + astnode.ident_name)
        else:
            return symbol_table[astnode.ident_name][-1][1]
    elif isinstance(astnode, AAST.Arithmetic):
        t1 = tc(astnode.lhs, symbol_table)
        t2 = tc(astnode.rhs, symbol_table)
        
        if (t1 == "Int" and t2 == "Int"):
            astnode.lhs.exp_type = t1
            astnode.rhs.exp_type = t2
            astnode.exp_type = "Int"
            return "Int"
        else:
            raise Exception ("ERROR: Adding " + t1 + " to " + t2 + "\n")
    elif isinstance(astnode, AAST.Compare):
        t1 = tc(astnode.lhs, symbol_table)
        t2 = tc(astnode.rhs, symbol_table)
        # Ints, Strings, and Bools must match
        if (t1, t2 in ["Int", "String", "Bool"]) and t1 != t2:
            print("ERROR: Comparing " + t1 + " to " + t2)
            exit()
        else:
            astnode.lhs.exp_type = t1
            astnode.rhs.exp_type = t2
            astnode.exp_type = "Bool"
            return "Bool"
         #   raise Exception ("ERROR: Adding " + t1 + " to " + t2 + "\n")
    elif isinstance(astnode, AAST.Method):
        return astnode.method_type.ident
    elif isinstance(astnode, AAST.InternalExpression):
        return astnode.exp_type
    elif isinstance(astnode, AAST.Self_Dispatch):
        if astnode.method_ident.ident in symbol_table:
            return (symbol_table[astnode.method_ident.ident].method_type.ident)
        else:
            print("ERROR: " + str(astnode.line_num) + ": Method not found")
            exit()
        return astnode.method_ident.ident
    elif isinstance(astnode, AAST.Block):
        for exp in astnode.exp_list:
            exp.exp_type = tc(exp, symbol_table)
        astnode.exp_type = astnode.exp_list[-1].exp_type # derive block type
        if(astnode.exp_type == "NO_TYPE"):
            print(astnode)
        return astnode.exp_type
    elif isinstance(astnode, AAST.If):
        pred = tc(astnode.predicate, symbol_table)
        then_body = tc(astnode.then_body , symbol_table)
        else_body = tc(astnode.else_body, symbol_table)
        return astnode.then_body.exp_type
    elif isinstance(astnode, AAST.While):
        pred = tc(astnode.predicate, symbol_table)
        if pred != "Bool":
            print("ERROR: Pred should be bool")
            exit()
        body = tc(astnode.body, symbol_table)
        #astnode.exp_type = body
        return astnode.exp_type
    elif isinstance(astnode, AAST.Assign):
        astnode.exp.exp_type = tc(astnode.exp, symbol_table)
        return astnode.exp_type
    else:
        print(type(astnode))
        raise Exception ("ERROR: Unknown Expression type!")
            
