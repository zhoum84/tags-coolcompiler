import sys
import init as INIT
import aast as AAST
import utils as UT
import registers as REG
import copy
# Global Variables
# Data structures that store all information required

# Class --> Attributes
class_map = {}

# Class --> Methods
implementation_map = {}

# static strings --> string labels
constant_labels={}

# Child --> Parent map
parent_map = {}

# Parent --> Child map
child_map = {}

# Annotated Abstract Syntax Tree
ast = []

# Class Name --> Class Tag
class_tags = {}

# Current class that is compiling 
current_class = ""

self_reg = REG.R(0)
acc_reg = REG.R(1)
tmp_reg = REG.R(2)
reg_three = REG.R(3)

# offset constants for object layout
classtag_offset = 0
size_offset = 1
vtable_offset = 2
metadata_size = 3
e1_contents_offset = 4
e2_contents_offset = 5 

# primitive offsets
int_contents_offset = 3
bool_contents_offset = int_contents_offset
string_contents_offset = int_contents_offset

branch_count = 0

asm = ""

def assign_tags(classes):
    tags = {}
    cpy = []
    
    for cls in (classes):
        if cls not in ["Int", "Bool", "String", "Object"]:
            cpy.append(cls)
    for i, cls in enumerate(cpy):
        tags[cls] = i + 10
    tags["Int"] = 1
    tags["Bool"] = 0
    tags["String"] = 3
    tags["Object"] = 9
    print(tags)
    return tags

def cgen(exp, st):
    global asm
    global branch_count
    if isinstance(exp, AAST.Variable):
        if hasattr(st[exp.name], "offset") and st[exp.name].offset!= None:
            asm += (f"\t\tld {acc_reg} <- {st[exp.name]} ;;attribute offset for {exp.name}") + "\n"
        else:   
            asm += (f"\t\tmov {acc_reg} <- {st[exp.name]} ;;{exp.name}") + "\n"
        return acc_reg
    elif isinstance(exp, AAST.Int):
        cgen(AAST.New(exp.lineno, 'Int'), st)

        asm += (f"\t\tli {tmp_reg} <- {exp.value}") + "\n"
        asm += (f"\t\tst {acc_reg}[{int_contents_offset}] <- {tmp_reg}") + "\n"
        return acc_reg
    elif isinstance(exp, AAST.String):
        cgen(AAST.New(exp.lineno, 'String'), st)
        asm += (f"\t\tla {tmp_reg} <- {constant_labels[exp.value]}") + "\n"
        asm += (f"\t\tst {acc_reg}[{string_contents_offset}] <- {tmp_reg}") + "\n"
        return acc_reg
    elif isinstance(exp, AAST.TrueExp):
        cgen(AAST.New(exp.lineno, 'Bool'), st)
        asm += (f"\t\tli {tmp_reg} <- {1}") + "\n"
        asm += (f"\t\tst {acc_reg}[{bool_contents_offset}] <- {tmp_reg}") + "\n"
        return acc_reg
    elif isinstance(exp, AAST.FalseExp):
        cgen(AAST.New(exp.lineno, 'Bool'), st)
        asm += (f"\t\tli {tmp_reg} <- {0}") + "\n"
        asm += (f"\t\tst {acc_reg}[{bool_contents_offset}] <- {tmp_reg}") + "\n"
        return acc_reg

    elif isinstance(exp, AAST.New):
        asm += ("\t\tpush fp") + "\n"
        asm += (f"\t\tpush {self_reg}") + "\n"
        if exp.new_type == "SELF_TYPE":
            asm += f'\t\tld {tmp_reg} <- {self_reg}[{vtable_offset}];;get SELF_TYPE object\n'
            asm += f'\t\tld {tmp_reg} <- {tmp_reg}[1]\n' # constructor offset
        else:
            asm += (f"\t\tla {tmp_reg} <- {exp.new_type}..new") + "\n"
        asm += (f"\t\tcall {tmp_reg}") + "\n"
        asm += (f"\t\tpop {self_reg}") + "\n"
        asm += ("\t\tpop fp") + "\n"

        return acc_reg
    elif isinstance(exp, AAST.Let):
        # make a deep copy of st for use solely in the let scope 
        st_copy = copy.deepcopy(st)
        for i, e in enumerate(exp.letlist):
            new_type = current_class if e.type == "SELF_TYPE" else e.type
            if new_type in ["String", "Int", "Bool"]:
                loc = cgen(AAST.New(exp.lineno, new_type), st_copy)
            else:
                asm += f'\t\tli {acc_reg} <- 0\n'
                loc = acc_reg
            # Find unused memory to store new variable
            offset = 0
            while f'fp[{-1 * (i + offset)}]' in [str(x) for x in st_copy.values()]:
                offset += 1
            if isinstance(e, AAST.LetInit):
                loc = cgen(e.exp, st_copy)
                asm += "\t\t;;init\n"
                class_map[current_class].append(AAST.Attribute(e.identifier_nt, e.type, e.exp))
            else:
                class_map[current_class].append(AAST.Attribute(e.identifier_nt, e.type))
            # Only add new binding to st_copy after initialization,
            st_copy[e.identifier_nt] = REG.FP(-1 * (i + offset))

            asm += f"\t\tst {st_copy[e.identifier_nt]} <- {loc}\n"
            asm += f'\t\t;;let\n'

        cgen(exp.body, st_copy)

        for _ in range(len(exp.letlist)):
            class_map[current_class].pop()

        return acc_reg
    elif isinstance(exp, AAST.Dynamic_Dispatch):
        asm += "\t\t;;dyn_dis\n"
        method_offset = -1
        asm += (f"\t\tpush {self_reg}") + "\n"

        asm += ("\t\tpush fp") + "\n"
        ro_type = current_class if exp.ro.anno_type == "SELF_TYPE" else exp.ro.anno_type

        for i, method in enumerate(implementation_map[ro_type]):
            if method.method_name == exp.method:
                method_offset = i + 2 # account for Constructor method
                break
        # push parameters onto stack
        for i, formal in enumerate((exp.formals)):
            f_loc = cgen(formal, st)
            asm += (f"\t\tpush {f_loc}") + ";;formal \n"
        
        if len(exp.formals) > 1:
            asm += f'\t\tli {reg_three} <- {len(exp.formals)}\n'
            asm += f'\t\talloc {reg_three} {reg_three};;formal space\n'
            for i in range(len(exp.formals)):
                asm += (f"\t\tpop {tmp_reg}\n")
                asm += f"\t\tst {reg_three}[{i}] <- {tmp_reg}\n"

            for i in (range(len(exp.formals))):
                asm += (f"\t\tld {tmp_reg} <- {reg_three}[{i}]\n")
                asm += f"\t\tpush {tmp_reg}\n"
        


        #generate code to evaluate the receiver object
        ro_loc = cgen(exp.ro, st)

        if isinstance(exp, AAST.Static_Dispatch):
            branch_count += 1
            asm += f'\t\tbnz {ro_loc} l{branch_count}\n'
            asm += f'\t\tla {acc_reg} <- {constant_labels[f"ERROR: {exp.lineno}: Exception: static dispatch on void"]}\n'
            asm += f'\t\tsyscall IO.out_string\n'
            asm += f'\t\tsyscall exit\n'
            asm += f'l{branch_count}:\n'
        elif hasattr(exp.ro, "name") and exp.ro.name != 'self':
            branch_count += 1
            asm += f'\t\tbnz {ro_loc} l{branch_count}\n'
            asm += f'\t\tla {acc_reg} <- {constant_labels[f"ERROR: {exp.lineno}: Exception: dispatch on void"]}\n'
            asm += f'\t\tsyscall IO.out_string\n'
            asm += f'\t\tsyscall exit\n'
            asm += f'l{branch_count}:\n'
        elif not hasattr(exp.ro, "name"):
            branch_count += 1
            asm += f'\t\tbnz {ro_loc} l{branch_count}\n'
            asm += f'\t\tla {acc_reg} <- {constant_labels[f"ERROR: {exp.lineno}: Exception: dispatch on void"]}\n'
            asm += f'\t\tsyscall IO.out_string\n'
            asm += f'\t\tsyscall exit\n'
            asm += f'l{branch_count}:\n'


        asm += f"\t\tpush {ro_loc};;push receiver\n"

        if isinstance(exp, AAST.Static_Dispatch):
            asm += f'\t\tla {tmp_reg} <- {exp.caller_type}..vtable\n'
        else:
            asm += (f"\t\tld {tmp_reg} <- {ro_loc}[{vtable_offset}]") + ";;load vtable\n"
        
        #retrieve method from vtable
        asm += (f"\t\tld {tmp_reg} <- {tmp_reg}[{method_offset}]") + f";;load method {exp.method}\n"
        asm += (f"\t\tcall {tmp_reg}") + "\n"
        asm += ("\t\tpop fp") + "\n"
        asm += (f"\t\tpop {self_reg}") + "\n"
        asm += "\t\t;;dyn_disend\n"
        return acc_reg
    elif isinstance(exp, AAST.Internal):
        if exp.method == "IO.out_int":
            v_loc = cgen(AAST.Variable(exp.lineno, "Int", "x"), st) # out_int formal
        
            asm += (f"\t\tmov {tmp_reg} <- {v_loc}") + "\n"
            asm += (f"\t\tld {tmp_reg} <- {tmp_reg}[{int_contents_offset}]") + "\n"
            # load int into r1 for syscall
            asm += (f"\t\tmov r1 <- {tmp_reg}")+ "\n"

            asm += ("\t\tsyscall IO.out_int") + "\n"
            return acc_reg
        elif exp.method == "IO.out_string":
            v_loc = cgen(AAST.Variable(exp.lineno, "String", "x"), st)
            asm += (f"\t\tld {acc_reg} <- {v_loc}[{string_contents_offset}]") + "\n"
            # load int into r1 for syscall
            asm += ("\t\tsyscall IO.out_string") + "\n"
            asm += (f"\t\tmov {acc_reg} <- {self_reg}\n")
            return acc_reg
        elif exp.method == "IO.in_int":
            v_loc = cgen(AAST.New(exp.lineno, 'Int'), st)
            asm += (f"\t\tmov {tmp_reg} <- {v_loc}") + "\n"
            asm += (f"\t\tsyscall IO.in_int\n")
            asm += (f"\t\tst {tmp_reg}[{int_contents_offset}] <- {acc_reg}\n")
            asm += (f"\t\tmov {acc_reg} <- {tmp_reg}\n")
            return acc_reg
        elif exp.method == "IO.in_string":
            v_loc = cgen(AAST.New(exp.lineno, 'String'),st)
            asm += (f"\t\tmov {tmp_reg} <- {v_loc}") + "\n"
            asm += (f"\t\tsyscall IO.in_string\n")
            asm += (f"\t\tst {tmp_reg}[{string_contents_offset}] <- {acc_reg}\n")
            asm += (f"\t\tmov {acc_reg} <- {tmp_reg}\n")
            return acc_reg
        elif exp.method == "Object.abort":
            abort_label = constant_labels['abort']
            asm += (f"\t\tla {acc_reg} <- {abort_label}\n")
            asm += "\t\tsyscall IO.out_string\n"
            asm += "\t\tsyscall exit\n"
        elif exp.method == "Object.copy":
            asm += f"\t\tld {tmp_reg} <- {self_reg}[{size_offset}];;get size\n"
            asm += f"\t\talloc {acc_reg} {tmp_reg}\n"
            asm += f"\t\tpush {acc_reg}\n"
            branch_count += 1
            asm += f"l{branch_count}:\n"
            asm += f'\t\tbz {tmp_reg} l{branch_count + 1}\n'
            asm += f'\t\tld {reg_three} <- {self_reg}[0]\n'
            asm += f'\t\tst {acc_reg}[0] <- {reg_three}\n'
            asm += f'\t\tli {reg_three} <- 1\n'
            asm += f'\t\tadd {self_reg} <- {self_reg} {reg_three}\n'
            asm += f'\t\tadd {acc_reg} <- {acc_reg} {reg_three}\n'
            asm += f'\t\tli {reg_three} <- 1\n'
            asm += f'\t\tsub {tmp_reg} <- {tmp_reg} {reg_three}\n'
            asm += f"\t\tjmp l{branch_count}\n"

            branch_count += 1
            asm += f"l{branch_count}:\n"
            asm += f"\t\tpop {acc_reg}\n"
        elif exp.method == "Object.type_name":
            v_loc = cgen(AAST.New(exp.lineno, 'String'), st)
            asm += f"\t\tld {tmp_reg} <- {self_reg}[{vtable_offset}]\n"
            asm += f"\t\tld {tmp_reg} <- {tmp_reg}[{0}]\n"
            asm += f"\t\tst {acc_reg}[{string_contents_offset}] <- {tmp_reg}\n"
            return acc_reg
        elif exp.method == "String.concat":
            v_loc = cgen(AAST.New(exp.lineno, 'String'), st)
            asm += f'\t\tmov {reg_three} <- {v_loc}\n'
            asm += f'\t\tld {tmp_reg} <- fp[2]\n' # TODO: Figure this out. Why is it 3?
            asm += f'\t\tld {tmp_reg} <- {tmp_reg}[{string_contents_offset}]\n'
            asm += f'\t\tld {acc_reg} <- {self_reg}[{string_contents_offset}]\n' 
            asm += f'\t\tsyscall String.concat\n'
            asm += f'\t\tst {reg_three}[{string_contents_offset}] <- {acc_reg}\n'
            asm += f'\t\tmov {acc_reg} <- {reg_three}\n'
            return acc_reg
        elif exp.method == "String.substr":
            s_loc = cgen(AAST.New(exp.lineno, 'String'), st)
            asm += f'\t\tmov {reg_three} <- {s_loc}\n'
            asm += f'\t\tld {tmp_reg} <- fp[3]\n' # TODO: Figure this out. Why is it 3?
            asm += f'\t\tld {tmp_reg} <- {tmp_reg}[{string_contents_offset}]\n'
            asm += f'\t\tld {acc_reg} <- fp[2]\n' 
            asm += f'\t\tld {acc_reg} <- {acc_reg}[{string_contents_offset}]\n'
            asm += f'\t\tld {self_reg} <- {self_reg}[{string_contents_offset}]\n' 
            asm += '\t\tsyscall String.substr\n'
            branch_count += 1
            asm += f'\t\tbnz {acc_reg} l{branch_count}\n'
            asm += f'\t\tla {acc_reg} <- {constant_labels["ERROR: 0: Exception: String.substr out of range"]}\n'
            asm += f'\t\tsyscall IO.out_string\n'
            asm += f'\t\tsyscall exit\n'
            asm += f'l{branch_count}:\n'
            asm += f'\t\tst {reg_three}[{string_contents_offset}] <- {acc_reg}\n'
            asm += f'\t\tmov {acc_reg} <- {reg_three}\n'
        elif exp.method == "String.length":
            i_loc = cgen(AAST.New(exp.lineno, 'Int'), st)
            asm += f'\t\tmov {tmp_reg} <- {i_loc}\n'
            asm += f'\t\tld {acc_reg} <- {self_reg}[{string_contents_offset}]\n'
            asm += f'\t\tsyscall String.length\n'
            asm += f'\t\tst {tmp_reg}[{int_contents_offset}] <- {acc_reg}\n'
            asm += f'\t\tmov {acc_reg} <- {tmp_reg}\n'
            return acc_reg
    elif isinstance(exp, AAST.Assign):
        loc = cgen(exp.exp, st)
        asm += f'\t\tmov {reg_three} <- {loc}\n'
        asm += f'\t\tst {st[exp.ident.name]} <- {reg_three};;assign\n'
        return loc
    elif isinstance(exp, AAST.Arithmetic):
        # 3 registers needed
        # first, evaluate the first operand, storing the result in a register
        asm += ";;arith start\n"
        e1_loc = cgen(exp.e1, st)
        asm += (f"\t\tld {tmp_reg} <- {e1_loc}[{int_contents_offset}]") + "\n"#offset where integer constant is stored
        
        # push first operand onto stack
        asm += (f"\t\tpush {tmp_reg}\n")

        e2_loc = cgen(exp.e2, st)

        #store second operand into acc_reg
        #load unboxed integer constant value from Int object into register
        asm += (f"\t\tld {acc_reg} <- {e2_loc}[{int_contents_offset}]") + "\n"
        if isinstance(exp, AAST.Divide):
            branch_count += 1
            asm += f'\t\tbnz {acc_reg} l{branch_count}\n'
            asm += f'\t\tla {acc_reg} <- {constant_labels[f"ERROR: {exp.lineno}: Exception: division by zero"]}\n'
            asm += '\t\tsyscall IO.out_string\n'
            asm += '\t\tsyscall exit\n'
            asm += f'l{branch_count}:\n'
            

        # retrieve first operand from stack
        asm += (f"\t\tpop {tmp_reg}\n")
        # add values together
        oper = 'add'
        if isinstance(exp, AAST.Plus):
            asm += (f"\t\t{oper} {acc_reg} <- {acc_reg} {tmp_reg}") + "\n"
        if isinstance(exp, AAST.Minus):
            oper = 'sub'
            asm += (f"\t\t{oper} {acc_reg} <- {tmp_reg} {acc_reg}") + "\n"

        elif isinstance(exp, AAST.Times):
            oper = 'mul'
            asm += (f"\t\t{oper} {acc_reg} <- {acc_reg} {tmp_reg}") + "\n"
        elif isinstance(exp, AAST.Divide):
            oper = 'div'
            asm += (f"\t\t{oper} {acc_reg} <- {tmp_reg} {acc_reg}") + "\n"

        # push on stack
        asm += (f"\t\tpush {acc_reg}") + "\n"
        # create new Int object
        cgen(AAST.New(exp.lineno, 'Int'), st)

        # retrieve saved value
        asm += (f"\t\tpop {tmp_reg}") + "\n"

        # throw that value into the newly-created int
        asm += (f"\t\tst {acc_reg}[{int_contents_offset}] <- {tmp_reg}") + "\n"
        asm += ";;arith end\n"

        return acc_reg
    elif isinstance(exp, AAST.Compare):
        asm += '\t\tpush fp\n'
        e1 = cgen(exp.e1, st)
        asm += f'\t\tpush {e1}\n'
        e2 = cgen(exp.e2, st)
        asm += f'\t\tpush {e2}\n'
        
        asm += "\t\tpush r0\n"
        if isinstance(exp, AAST.LessThan):
            handler = "lt"
        elif isinstance(exp, AAST.LessThanEqual):
            handler = "le"
        else:
            handler = "eq"
        asm += f'\t\tcall {handler}_handler\n'
        asm += '\t\tpop fp\n'
        return acc_reg

    elif isinstance(exp, AAST.If):
        asm += f'\t\t;;ifstart\n'
        # load result of predicate
        predicate = cgen(exp.predicate, st)
        # retrieve predciate value
        asm += f'\t\tld {acc_reg} <- {predicate}[{bool_contents_offset}];;load predicate\n'
        
        branch_count += 1   
        t = branch_count     
        asm += f'\t\tbnz {acc_reg} l{t}\n'

        branch_count += 1
        f = branch_count
        asm += f'l{f}: ;;false branch\n'
        else_body = cgen(exp.else_body, st)


        branch_count += 1
        end_branch = branch_count
        asm += f'\t\tjmp l{end_branch};;go to if end\n'


        asm += f'l{t}: ;;true branch\n'
        then_body = cgen(exp.then_body, st)
        asm += f'l{end_branch}: ;;if end \n'
        return acc_reg
    elif isinstance(exp, AAST.Not):
        loc = cgen(exp.exp, st)
        asm += f"\t\tld {tmp_reg} <- {loc}[{bool_contents_offset}]\n"
        branch_count += 1
        t_branch = branch_count
        asm += f"\t\tbnz {tmp_reg} l{t_branch}\n"

        branch_count += 1
        e_branch = branch_count

        cgen(AAST.New(exp.lineno, 'Bool'), st)
        asm += f'\t\tli {tmp_reg} <- 1\n'
        asm += f'\t\tst {acc_reg}[{bool_contents_offset}] <- {tmp_reg}\n'
        asm += f'\t\tjmp l{e_branch}\n'


        asm += f'l{t_branch}:;; true branch\n'
        cgen(AAST.New(exp.lineno, 'Bool'), st)

        asm += f'l{e_branch}: ;;not end \n'
        return acc_reg
    elif isinstance(exp, AAST.Negate):
        i_loc = cgen(AAST.New(exp.lineno, 'Int'), st)
        asm += f'\t\tli {tmp_reg} <- 0\n'
        asm += f'\t\tst {acc_reg}[{int_contents_offset}] <- {tmp_reg}\n'
        asm += f'\t\tld {acc_reg} <- {i_loc}[{int_contents_offset}]\n'

        # Negate needs an Int initialized to 0 to perform subtraction
        # We need to reserve a location in memory, and ensure it will not be overwritten
        offset = 0
        while f'fp[{offset}]' in [str(x) for x in st.values()]:
            offset -= 1
        st["neg"+ str(offset)] = REG.FP(offset)
        asm += f'\t\tst fp[{offset}] <- {acc_reg}\n'

        # get int to negate
        loc = cgen(exp.exp, st)
        # load int
        asm += f'\t\tld {acc_reg} <- {loc}[{int_contents_offset}]\n'
        # load stored 0
        asm += f'\t\tld {tmp_reg} <- fp[{offset}]\n'
        asm += f'\t\tsub {acc_reg} <- {tmp_reg} {acc_reg}\n'
        asm += f'\t\tst fp[{offset}] <- {acc_reg}\n'
        cgen(AAST.New(exp.lineno, 'Int'), st)
        asm += f'\t\tld {tmp_reg} <- fp[{offset}]\n'
        asm += f'\t\tst {acc_reg}[{int_contents_offset}] <- {tmp_reg}\n'
        del st["neg" + str(offset)]
        return acc_reg
      
    elif isinstance(exp, AAST.Isvoid):
        loc = cgen(exp.exp, st)
        branch_count += 1
        t_branch = branch_count
        asm += f"\t\tbz {loc} l{t_branch}\n"

        branch_count += 1
        asm += f'l{branch_count}:;; false branch\n'
        cgen(AAST.New(exp.lineno, 'Bool'), st)
        branch_count += 1
        e_branch = branch_count
        asm += f'\t\tjmp l{e_branch}\n'

        asm += f'l{t_branch}:;; true branch\n'
        cgen(AAST.New(exp.lineno, 'Bool'), st)
        asm += f'\t\tli {tmp_reg} <- 1\n'
        asm += f'\t\tst {acc_reg}[{bool_contents_offset}] <- {tmp_reg}\n'

        asm += f'l{e_branch}: ;;isvoid end \n'
        return acc_reg

    elif isinstance(exp, AAST.Block):
        for e in exp.exp_list:
            cgen(e, st)
        return acc_reg
    elif isinstance(exp, AAST.While):
        branch_count += 1
        s_branch = branch_count
        asm += f"l{s_branch}: ;;while start\n"

        branch_count += 1
        e_branch = branch_count
        loc = cgen(exp.predicate, st)
        # retrieve pred
        asm += f'\t\tld {acc_reg} <- {loc}[{bool_contents_offset}]\n'
        asm += f'\t\tbz {acc_reg} l{e_branch}\n'
        
        cgen(exp.body, st)
        asm += f'\t\tjmp l{s_branch }\n'
        asm += f'l{e_branch}:\n'
        return acc_reg
    elif isinstance(exp, AAST.ExpCase):
        branch_count += 1
        void_brch = branch_count
        st_copy = copy.deepcopy(st)
        asm += '\t\t;;case expression begins\n'
        v_loc = cgen(exp.exp, st)
        asm += f'\t\tbz {acc_reg} l{void_brch}\n'

        asm += f'\t\tst fp[1] <- {acc_reg}\n'
        asm += f'\t\tld {acc_reg} <- {v_loc}[{classtag_offset}]\n'
        c: AAST.CaseItem
        case_types = set()

        # Create branches for defined cases
        # type -> branch 
        case_branches = {}
        for i, c in enumerate(exp.caselist):
            st_copy[c.identifier_nt.name] = REG.FP(1)
            case_type = c.exp_type.name
            branch_count += 1
            asm += f'\t\tli {tmp_reg} <- {class_tags[case_type]}\n'
            asm += f'\t\tbeq {acc_reg} {tmp_reg} l{branch_count};;{c.exp_type.name}\n'
            
            case_types.add(case_type)
            case_branches[case_type] = f"l{branch_count}"
            b_c = branch_count - len(exp.caselist)
        
        # Then, ensure child classes of each case are accounted for
        for i, c in enumerate(exp.caselist):
            case_type = c.exp_type.name
            
            # while case_type in child_map:
            children = UT.dfs(child_map, case_type)
            for child in children:
                if child not in case_types:
                    # Need to get the nearest ancestor of the class
                    cls = child
                    while cls not in case_branches:
                        cls = parent_map[cls]
                    asm += f'\t\tli {tmp_reg} <- {class_tags[child]}\n'
                    asm += f'\t\tbeq {acc_reg} {tmp_reg} {case_branches[cls]};;{c.exp_type.name}\n'
                    case_types.add(child)
                    case_branches[child] = case_branches[cls]
            #     case_type = child_map[case_type]
            # if case_type not in case_types:
            #     asm += f'\t\tli {tmp_reg} <- {class_tags[case_type]}\n'
            #     asm += f'\t\tbeq {acc_reg} {tmp_reg} l{branch_count};;{c.exp_type.name}\n'


        asm += f';;error case\n'
        err1 = "ERROR: {lineno}: Exception: case without matching branch"
        asm += f'\t\tla {acc_reg} <- {constant_labels[err1.format(lineno = exp.lineno)]}\n'
        asm += f'\t\tsyscall IO.out_string\n'
        asm += f'\t\tsyscall exit\n'

        asm += f'l{void_brch}: ;;void case\n'
        err2 = "ERROR: {lineno}: Exception: case on void"
        asm += f'\t\tla {acc_reg} <- {constant_labels[err2.format(lineno = exp.lineno)]}\n'
        asm += f'\t\tsyscall IO.out_string\n'
        asm += f'\t\tsyscall exit\n'
        branch_count += 1
        end_case = branch_count
        for i, c in enumerate(exp.caselist):
            asm += f'l{end_case - len(exp.caselist) + i}:;;{c.exp_type.name}\n'
            cgen(c.exp, st_copy)
            asm += f"\t\tjmp l{end_case}\n"
        
        asm += f'l{end_case}: ;;end_case\n'
        return acc_reg
    else:
        print(type(exp))

def format_constants(class_names, constants):
    builtin =["abort", "ERROR: 0: Exception:"]
    string_count = len(class_names) + len(builtin)
    constants_str = ""
    constants_str += 'the.empty.string:\t\tconstant ""\n'
    for i, cls in enumerate(class_names):
        constants_str += f'string{i}:\t\tconstant "{cls}"\n'
        constant_labels[cls] = f'string{i}'
    for i, c in enumerate(builtin):
        constants_str += f'string{i + len(class_names)}:\t\tconstant "{c}"\n'
        constant_labels[c] = f'string{i + len(class_names)}'

    for const in constants:
        if type(const) is str:
            constant_labels[const]= f'string{string_count}'
            constants_str += f'string{string_count}:\t\tconstant "{const}"\n'
            string_count += 1

    return constants_str

def __main__():

    if len(sys.argv) < 2: 
        print("Specify .cl-type input file.\n")
        exit()
    with open(sys.argv[1]) as f:
        lines = [l[:-1] for l in f.readlines()] # strip \n
    global class_map
    global implementation_map
    global ast
    global class_tags
    global current_class
    global parent_map
    global child_map
    (class_map, class_names) = INIT.load_class_map(lines)
    (implementation_map, ast, constants) = INIT.load_implementation_map_and_ast(lines)
    (parent_map, child_map) = INIT.load_parent_map(lines)
    
    class_tags = assign_tags(class_names)

    constant_block = format_constants(class_names, constants)
    
    global asm
    for cls in class_names:
        # create label for vtable
        asm += (f"{cls}..vtable:\n")
        # label for constructor
        asm += f"\t\tconstant {constant_labels[cls]}\n"
        asm += (f"\t\tconstant {cls}..new") + "\n"
        # labels for other methods
        if cls in implementation_map:
            for method in implementation_map[cls]:
                asm += (f"\t\tconstant {method.method_label}") + "\n"
        
    # asm +=  constructors
    for cls in class_names:
        current_class = cls
        asm += (f"{cls}..new:") + "\n"
        # calling convention
        asm += ("\t\tmov fp <- sp") + "\n"# move frame poitner to the same as the stack pointer
        
        temps = 1
        for attr in class_map[cls]:
            temps = max(temps, attr.num_temps)
        asm += (f"\t\tli {tmp_reg} <- {temps}\n")
        asm += (f"\t\tsub sp <- sp {tmp_reg}\n")
        
        asm += ("\t\tpush ra")  + "\n" # push ra into stack

        # load size into a register
        # we should know this statically
        # vtable, attributes, class tag, object size
        s = len(class_map[cls]) + metadata_size
        if cls in ["Bool", "String", "Int"]:
            s += 1
        asm += (f"\t\tli {self_reg} <- {s}")+ ";;size\n"

        # ask the OS for space in the heap
        asm += (f"\t\talloc {self_reg} {self_reg}")+ "\n"
        tag = class_tags[cls]

        asm += (f"\t\tli {tmp_reg} <- {tag}\n")
        asm += f"\t\tst {self_reg}[{classtag_offset}] <- {tmp_reg} ;;classtag \n"

        asm += (f"\t\tli {tmp_reg} <- {s}")+ ";;size\n"
        asm += (f"\t\tst {self_reg}[{size_offset}] <- {tmp_reg}\n")
        # store attributes
        # store class tag
        # get vtable pointer into newly-allocated space
        asm += (f"\t\tla {tmp_reg} <- {cls}..vtable") + "\n"
        asm += (f"\t\tst {self_reg}[{vtable_offset}] <- {tmp_reg}") + "\n"

        attr: AAST.Attribute

        st = {'self' : self_reg}
        for i, attr in enumerate(class_map[cls]):
            st[attr.id] = self_reg.off(i + metadata_size)

        # First initialize empty attributes
        for i, attr in enumerate(class_map[cls]):
            # Unused, but might be useful for optimization
            # if attr.type == "unboxed_int":
            #     asm += (f"\t\tli {tmp_reg} <- {attr.init}") + "\n"
            #     asm += (f"\t\tst {self_reg}[{i + metadata_size}] <- {tmp_reg}") + "\n"
            # elif attr.type == "unboxed_bool":
            #     asm += (f"\t\tli {tmp_reg} <- {0 if attr.init == False else 1}") + "\n"
            #     asm += (f"\t\tst {self_reg}[{i + metadata_size}] <- {tmp_reg}") + "\n"
            # else:
                asm += f'\t\t;;initialize attribute {attr.id} ({attr.type})\n'
                if attr.type in ["Bool", "Int", "String"]:
                    asm += ("\t\tpush fp") + "\n"
                    asm += (f"\t\tpush {self_reg}") + "\n"
                    asm += (f"\t\tla {tmp_reg} <- {attr.type}..new") + "\n"
                    asm += (f"\t\tcall {tmp_reg}") + "\n"

                    asm += (f"\t\tpop {self_reg}") + "\n"
                    asm += ("\t\tpop fp") + "\n"
                    asm += (f"\t\tst {self_reg}[{i + metadata_size}] <- {acc_reg}") + "\n"
                # Objects get initialized to 0
                else:
                    asm += f'\t\tli {acc_reg} <- 0\n'
                    asm += f'\t\tst {self_reg}[{i + metadata_size}] <- {acc_reg}\n'
        
        # Then initialize starting values
        for i, attr in enumerate(class_map[cls]):

            if attr.init != None:
                # cgen init expr
                # need location for storing the result of the initialization
                # res should just be acc_reg
                res = cgen(attr.init, st)
                # add two to each attribute for list (vtable is at 1, classtag at 0)
                asm += (f"\t\tst {self_reg}[{i + metadata_size}] <- {res}") + "\n"
            else:
                if attr.type in ["Bool", "Int"]:
                    res = cgen(AAST.New(0, attr.type), st)
                else:
                    asm += f"\t\tli {acc_reg} <- 0\n"
                asm += (f"\t\tst {self_reg}[{i + metadata_size}] <- {acc_reg}") + "\n"


        
        if cls == 'Bool':
            asm += f"\t\tli {acc_reg} <- 0\n"
            asm += f"\t\tst {self_reg}[{bool_contents_offset}] <- {acc_reg}\n"

        elif cls == 'Int':
            asm += f"\t\tli {acc_reg} <- 0 ;;load default value\n"
            asm += f"\t\tst {self_reg}[{int_contents_offset}] <- {acc_reg}\n"
        elif cls == 'String':
            asm += f"\t\tla {acc_reg} <- the.empty.string\n"
            asm += f"\t\tst {self_reg}[{string_contents_offset}] <- {acc_reg}\n"
        asm += (f"\t\tmov {acc_reg} <- {self_reg}") + "\n"
        asm += ("\t\tpop ra") + "\n"
        asm += (f"\t\tli {tmp_reg} <- {temps}\n")
        asm += (f"\t\tadd sp <- sp {tmp_reg}\n")
        asm += ("\t\treturn") + "\n"


    #methods
    method: AAST.MethodImplementation
    for method in ast:
        # make label
        current_class = method.class_name
        asm += (f"{method.method_label}:") + '\n'

        asm += ("\t\tmov fp <- sp") + '\n'
        asm += (f"\t\tpop {self_reg}\n")
        if method.num_temps != 0:
            asm += f"\t\tli {tmp_reg} <- {method.num_temps}\n"
            asm += f"\t\tsub sp <- sp {tmp_reg}\n"
        asm += ("\t\tpush ra") + '\n'
        st = {}
        from_class = class_map[method.class_name]
        # determien which class the method belongs to
        # lookup the attributes in that class
        for i, attribute in enumerate(from_class):
            
            st[attribute.id] = self_reg.off(i + metadata_size)
        
        for i, formal in enumerate(method.formals):
            st[formal] = REG.FP(i + 2) # pushing other stuff on stack first
        st["self"] = self_reg

        cgen(method.exp, st)

        asm += ("\t\tpop ra") + '\n'
        if method.num_temps != 0:
            asm += f"\t\tli {tmp_reg} <- {method.num_temps  + len(method.formals)}\n"
            asm += f"\t\tadd sp <- sp {tmp_reg}\n"

        asm += ("\t\treturn") + '\n'
    asm += constant_block   

    asm += UT.create_cmp(class_tags)
    #start label
    asm += ("start:") + '\n'
    asm += ("\t\tla r2 <- Main..new") + '\n'
    asm += "\t\tpush fp\n"
    asm += ("\t\tcall r2") + '\n'
    asm += ("\t\tpush fp")+ '\n'
    asm += ("\t\tpush r1") + '\n'
    asm += (f"\t\tla {tmp_reg} <- Main.main") + '\n'

    asm += (f"\t\tcall {tmp_reg}") + '\n'
    asm += ("\t\tsyscall exit") + '\n'

    asm_filename = (sys.argv[1])[:-4] + "asm"
    fout = open(asm_filename, 'w')
    fout.write(asm)

if __name__ == '__main__':
    __main__()
