import aast as AAST
from heapq import heappop, heappush
import copy
def def_iden(type):
    return AAST.Identifier(0, type)
object_methods = [
    AAST.Method(def_iden("abort"), [], def_iden("Object"), AAST.InternalExpression(0, def_iden("Object.abort"), "Object")),
    AAST.Method(def_iden("copy"), [], def_iden("SELF_TYPE"), AAST.InternalExpression(0, def_iden("Object.copy"), "SELF_TYPE")),
    AAST.Method(def_iden("type_name"), [], def_iden("String"), AAST.InternalExpression(0, def_iden("Object.type_name"), "String")),
    ]

io_methods = [
    AAST.Method(def_iden("in_int"), [], def_iden("Int"), AAST.InternalExpression(0, def_iden("IO.in_int"), "Int")),
    AAST.Method(def_iden("in_string"), [], def_iden("String"), AAST.InternalExpression(0, def_iden("IO.in_string"), "String")),
    AAST.Method(def_iden("out_int"), [AAST.Formal(def_iden("x"), def_iden("Int"))], def_iden("SELF_TYPE"), AAST.InternalExpression(0, def_iden("IO.out_int"), "SELF_TYPE")),
    AAST.Method(def_iden("out_string"), [AAST.Formal(def_iden("x"), def_iden("String"))], def_iden("SELF_TYPE"), AAST.InternalExpression(0, def_iden("IO.out_string"), "SELF_TYPE")),
]
string_methods = [
    AAST.Method(def_iden("concat"), [AAST.Formal(def_iden("s"), def_iden("String"))], def_iden("String"), AAST.InternalExpression(0, def_iden("String.concat"), "String")),  
    AAST.Method(def_iden("length"), [], def_iden("Int"), AAST.InternalExpression(0, def_iden("String.length"), "Int")),
    AAST.Method(def_iden("substr"), [AAST.Formal(def_iden("i"), def_iden("Int")), AAST.Formal(def_iden("l"), def_iden("Int"))], def_iden("String"), AAST.InternalExpression(0, def_iden("String.substr"), "String")),  
]


bool_class = AAST.Class(def_iden("Bool"), def_iden("Object"), [], [], [])
io_class = AAST.Class(def_iden("IO"), def_iden("Object"), [], io_methods, io_methods)
int_class = AAST.Class(def_iden("Int"), def_iden("Object"), [], [], [])
object_class = AAST.Class(def_iden("Object"), None, [], object_methods, object_methods)
string_class = AAST.Class(def_iden("String"), def_iden("Object"), [], string_methods, string_methods)
base_classes = [bool_class, io_class, int_class, object_class, string_class]
# Used for special cases
self_type_class = AAST.Class(def_iden("SELF_TYPE"), None, [], [], [])

def class_map(user_classes):  
    cmap = "class_map\n"
    class_list = base_classes + user_classes
    class_names = set(map(name, class_list))

    class_dict ={cls.name_iden.ident : cls for cls in class_list}
    init_check(user_classes, class_list, class_names)
    dict_copy = copy.deepcopy(class_dict)
    
    method_check(class_list, class_names, class_dict, dict_copy)
    
    class_list.sort(key = name)
    cmap += str(len(class_list)) + '\n'

    for cl in class_list:
        cmap += (cl.name_iden.ident) + '\n'
        
        if(cl.inherits_iden): # get parent attributes
            inherited_atr = get_parent_attributes(cl, class_dict)
            cmap += str(len(inherited_atr)) + '\n'
            past_attr = set()
            for attr in inherited_atr:
                if attr.attr_name.ident == "self":
                    print("ERROR: " + attr.attr_name.line_num + ": Type-Check: class " + cl.name_iden.ident + "has an attribute named self")
                    exit()
                if attr.attr_name.ident in past_attr:
                    print("ERROR: " + attr.attr_name.line_num + ": Type-Check: class " + cl.name_iden.ident + " redefines " + attr.attr_name.ident)
                    exit()
                past_attr.add(attr.attr_name.ident)
                cmap += format_attr(attr)
            dict_copy[cl.name_iden.ident].attributes = list(set(inherited_atr))
        elif(len(cl.attributes) > 0):
            cmap += str(len(cl.attributes))+'\n'

            for attr in cl.attributes:
                if attr.attr_name.ident == "self":
                    print("ERROR: " + attr.attr_name.line_num + ": Type-Check: class " + cl.name_iden.ident + "has an attribute named self")
                cmap += format_attr(attr)
        else:
            cmap += "0\n"
    return (cmap, class_dict, class_list, dict_copy)

def name(cl):
    return str(cl.name_iden.ident)


def format_attr(attr):
    fmted = ""
    if attr.initialization:
        fmted += "initializer\n"
    else:
        fmted += "no_initializer\n"
    fmted += str(attr.attr_name.ident) + '\n'
    fmted += str(attr.attr_type.ident) + '\n'
    if(attr.initialization):
        fmted += str(attr.exp) 
    return fmted


def get_parent_attributes(cls, class_dict):
    if not cls.inherits_iden:
        return cls.attributes
    else: 
        return get_parent_attributes(class_dict[cls.inherits_iden.ident], class_dict) + cls.attributes

def meth_name(method):
    return method.method_name.ident
def get_parent_methods(cls: AAST.Class, class_dict: dict):
    if cls.inherits_iden is None:
        return cls.methods
    else: 
        return get_parent_methods(class_dict[cls.inherits_iden.ident], class_dict) + cls.methods

def topo_sort(list):
    #list = [x.rstrip() for x in list]
    haveDependencies = {i: 0 for i in list}
    unlockedUponCompletion = {i: [] for i in list}
    
    for i in range(0, len(list), 2):
        haveDependencies[list[i]] += 1
        
        unlockedUponCompletion[list[i + 1]].append(list[i])
    
    priority_queue = []
    for task, numberOfDependencies in haveDependencies.items():
       if(numberOfDependencies == 0):
          heappush(priority_queue, task)

    sorted = []

    while len(priority_queue) != 0:
        completed = heappop(priority_queue)
        sorted.append(completed)
        for task in unlockedUponCompletion[completed]:
           haveDependencies[task] -= 1
           if(haveDependencies[task] == 0):
            heappush(priority_queue, task)

    for i in haveDependencies.values():
       if i != 0:
          return ["cycle"]
    return sorted


# Check for errors in classes, mainly concerning inheritance
def init_check(user_classes, class_list, class_names):
    
    for cls in user_classes:
        if cls.inherits_iden and cls.inherits_iden.ident in ["Bool", "Int", "String", "SELF_TYPE"]:
            print("ERROR: " + str(cls.name_iden.line_num) + ": Type-Check: class " + str(cls.name_iden.ident) + " inherits from " + str(cls.inherits_iden.ident))
            exit()
        if cls.name_iden.ident == "SELF_TYPE":
            print("ERROR: " + str(cls.name_iden.line_num) + ": " +  "Type-Check: Class redefined: " + cls.name_iden.ident)
            exit()


    for i, cls in enumerate(class_list):
        for j, target_cls in enumerate(class_list):
            if i != j and cls.name_iden.ident == target_cls.name_iden.ident:
                print("ERROR: " + str(max(int(cls.name_iden.line_num), int(target_cls.name_iden.line_num))) + ": " +  "Type-Check: Class redefined: " + cls.name_iden.ident)
                exit()

    if "Main" not in class_names:
        print("ERROR: 0: Type-Check: class Main not found")
        exit()
    
    for cl in class_list:
        if cl.inherits_iden and not cl.inherits_iden.ident in class_names:
            print("ERROR: " + cls.inherits_iden.line_num + " : Type-Check: Class inherits from unknown class: " + cls.inherits_iden.ident)
            exit()

    inheritance = []
    for cl in class_list:
        if cl.inherits_iden:
            inheritance.append(cl.name_iden.ident)
            inheritance.append(cl.inherits_iden.ident)

    if topo_sort(inheritance) == ["cycle"]:
        print("ERROR: 0: Type-Check: inheritance cycle: ")

# Check for illegal formals
def method_check(user_classes, class_names, class_dict, dict_copy):
    type_names = class_names.copy()
    class_names.add("SELF_TYPE")


    for cls in user_classes:
        for method in cls.methods:
            seen_formals = set()
            for formal in method.formals:
                if formal.formal_name.ident in seen_formals:
                    fmt_err(formal.formal_name.line_num, cls.name_iden.ident, " has method " + method.method_name.ident
                            + " with duplicate formal parameter named " + formal.formal_name.ident)
                    exit()
                elif formal.formal_name.ident == "self":
                    print("ERROR: " + formal.formal_name.line_num + ": Type-Check: class " 
                          + cls.name_iden.ident + " has method " + method.method_name.ident
                            + " with formal parameter named " + formal.formal_name.ident)
                    exit()
                elif not formal.formal_type.ident in type_names:
                    print("ERROR: " + str(formal.formal_name.line_num) + ": Type-Check: class " 
                          + cls.name_iden.ident + " has method " + method.method_name.ident
                            + " with formal parameter of unknown type " + formal.formal_type.ident)
                    exit()
                seen_formals.add(formal.formal_name.ident)
            if cls.name_iden.ident == "Main" and method.method_name.ident == "main" and len(method.formals) > 0:
                print("ERROR: 0: Type-Check: class Main method main with 0 parameters not found")
                exit()
            if not method.method_type.ident in class_names:
                fmt_err(method.method_type.line_num, cls.name_iden.ident,   " has method " + method.method_name.ident + " with unknown return type " + method.method_type.ident)
                exit()
        
        # By default, all user_defined classes inherit from Objects
        if not cls.inherits_iden and cls is not object_class:
            cls.inherits_iden = def_iden("Object")
        if cls.inherits_iden:
            parent_methods = get_parent_methods(class_dict[cls.inherits_iden.ident], class_dict)
            parent_map = {i.method_name.ident : i for i in parent_methods}
            for method in cls.methods:
                if method.method_name.ident in parent_map.keys():

                    # handle built-in methods
                    parent_method = parent_map[method.method_name.ident]
                    #check_builtin(cls, method, parent_method, cls.inherits_iden.ident)
                    if len(parent_method.formals) != len(method.formals):
                        fmt_err(method.method_type.line_num, cls.name_iden.ident, " redefines method " + method.method_name.ident + " and changes number of formals")
                        exit()
                    for i in range(len(method.formals)):
                        if parent_method.formals[i].formal_type.ident != method.formals[i].formal_type.ident:
                            fmt_err(method.method_type.line_num, cls.name_iden.ident, " redefines method " + method.method_name.ident + " and changes type of formal " + parent_method.formals[i].formal_name.ident)
                            exit()
                    if parent_method.method_type.ident != method.method_type.ident:
                        fmt_err(method.method_type.line_num, cls.name_iden.ident, " redefines method " + method.method_name.ident + " and changes return type (from " + parent_method.method_type.ident + " to " + method.method_type.ident + ")")

            dict_copy[cls.name_iden.ident].methods = list(set(dict_copy[cls.name_iden.ident].methods + parent_methods))

def fmt_err(lineno, class_name, custom_message):
    print("ERROR: " + lineno + ": Type-Check: class " + class_name + custom_message)


# def check_builtin(cls, method, parent_method, parent_type):
#     if parent_type == "IO" and parent_method in io_methods:
#         fmt_err(method.method_type.line_num, cls.name_iden.ident, " redefines method " + method.method_name.ident)
#         exit()
#     if parent_type == "Object" and parent_method in object_methods and parent_method.name_iden.ident != "abort":
#         fmt_err(method.method_type.line_num, cls.name_iden.ident, " redefines method " + method.method_name.ident)
#         exit()
