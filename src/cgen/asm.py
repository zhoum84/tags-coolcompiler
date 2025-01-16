import aast as AAST
import registers as REG
import copy
import utils as UT
from constants import * 
from instructions import *
from asm_constant_labels import *
asm = ""
fp = REG.FP_86()
sp = REG.SP_86()
rsi = REG.RSI()
def cgen(exp, st):
    global asm
    global branch_count
    if isinstance(exp, AAST.Variable):
        if hasattr(st[exp.name], "offset") and st[exp.name].offset!= None:
            asm += comment(f"attribute offset for {exp.name}: {st[exp.name]}")
            asm += movq(st[exp.name], acc_reg)
        else:   
            asm += movq(st[exp.name], acc_reg)
        return acc_reg
    elif isinstance(exp, AAST.Int):
        cgen(AAST.New(exp.lineno, 'Int'), st)
        asm += movq(exp.value, tmp_reg)
        asm += movq(tmp_reg, f'{int_contents_offset * 8}({acc_reg})')
        return acc_reg
    elif isinstance(exp, AAST.String):
        cgen(AAST.New(exp.lineno, 'String'), st)
        asm += movq_int(constant_labels[exp.value], tmp_reg)
        asm += movq(tmp_reg, f'{8 * string_contents_offset}({acc_reg})')
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
        asm += pushq(fp)
        asm += pushq(self_reg)
        if exp.new_type == "SELF_TYPE":
            asm += f'\t\tld {tmp_reg} <- {self_reg}[{vtable_offset}];;get SELF_TYPE object\n'
            asm += f'\t\tld {tmp_reg} <- {tmp_reg}[1]\n' # constructor offset
        else:
            asm += movq(f'{exp.new_type}..new', tmp_reg)
        asm += call(f'*{tmp_reg}')
        asm += popq(self_reg)
        asm += popq(fp)

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
        asm += comment("dynamic dispatch start:")
        method_offset = -1
        asm += pushq(self_reg)
        asm += pushq(fp)
        ro_type = current_class if exp.ro.anno_type == "SELF_TYPE" else exp.ro.anno_type

        for i, method in enumerate(implementation_map[ro_type]):
            if method.method_name == exp.method:
                method_offset = i + 2 # account for Constructor method
                break
        # push parameters onto stack
        for i, formal in enumerate((exp.formals)):
            f_loc = cgen(formal, st)
            asm += pushq(f_loc)
        
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

        # if isinstance(exp, AAST.Static_Dispatch):
        #     branch_count += 1
        #     asm += f'\t\tbnz {ro_loc} l{branch_count}\n'
        #     asm += f'\t\tla {acc_reg} <- {constant_labels[f"ERROR: {exp.lineno}: Exception: static dispatch on void"]}\n'
        #     asm += f'\t\tsyscall IO.out_string\n'
        #     asm += f'\t\tsyscall exit\n'
        #     asm += f'l{branch_count}:\n'
        # elif hasattr(exp.ro, "name") and exp.ro.name != 'self':
        #     branch_count += 1
        #     asm += f'\t\tbnz {ro_loc} l{branch_count}\n'
        #     asm += f'\t\tla {acc_reg} <- {constant_labels[f"ERROR: {exp.lineno}: Exception: dispatch on void"]}\n'
        #     asm += f'\t\tsyscall IO.out_string\n'
        #     asm += f'\t\tsyscall exit\n'
        #     asm += f'l{branch_count}:\n'
        # elif not hasattr(exp.ro, "name"):
        #     branch_count += 1
        #     asm += f'\t\tbnz {ro_loc} l{branch_count}\n'
        #     asm += f'\t\tla {acc_reg} <- {constant_labels[f"ERROR: {exp.lineno}: Exception: dispatch on void"]}\n'
        #     asm += f'\t\tsyscall IO.out_string\n'
        #     asm += f'\t\tsyscall exit\n'
        #     asm += f'l{branch_count}:\n'

        asm += pushq(ro_loc)

        if isinstance(exp, AAST.Static_Dispatch):
            asm += movq(f'{exp.caller_type}..vtable', tmp_reg)
        else:
            asm += movq(f'{vtable_offset * 8}({ro_loc})', tmp_reg)
        
        #retrieve method from vtable
        asm += movq(f'{method_offset * 8}({tmp_reg})', tmp_reg)
        asm += call_reg(tmp_reg)
        asm += addq('$8', sp) # Sometimes this is 8, sometimes this is 16, not sure when though.
        asm += popq(fp)
        asm += popq(self_reg)
        return acc_reg
    elif isinstance(exp, AAST.Internal):
        if exp.method == "IO.out_int":
            v_loc = cgen(AAST.Variable(exp.lineno, "Int", "x"), st) # out_int formal
        
            asm += movq(f'{int_contents_offset * 8}({v_loc})', tmp_reg)

            # load int into r1 for syscall
            asm += movq('$percent.d', '%rdi')
            asm += movl('%r13d', '%eax')
            asm += tab_and_endl('cdqe')
            asm += movq('%rax', '%rsi')
            asm += movl_int(0, '%eax')
            asm += call('printf')
            asm += movq(self_reg, acc_reg)
            return acc_reg
        elif exp.method == "IO.out_string":
            v_loc = cgen(AAST.Variable(exp.lineno, "String", "x"), st)
            asm += movq(f"{string_contents_offset * 8}({v_loc})", acc_reg)
            # load int into r1 for syscall
            asm += movq(acc_reg, '%rdi')
            asm += call('cooloutstr')
            asm += movq(self_reg, acc_reg)
            return acc_reg
        elif exp.method == "IO.in_int":
            v_loc = cgen(AAST.New(exp.lineno, 'Int'), st)
            asm += movq(v_loc, tmp_reg)
            asm += movl_int(1, '%esi')
            asm += movl_int(4096, '%edi')
            asm += call('calloc')
            asm += pushq('%rax')
            asm += movq('%rax', '%rdi')
            asm += movq_int(4096, '%rsi')
            asm += movq('stdin(%rip)', '%rdx')
            asm += call('fgets')
            asm += popq('%rdi')
            asm += movl_int(0, '%eax')
            asm += pushq('%rax')
            asm += movq('%rsp', '%rdx')
            asm += movq('$percent.ld', '%rsi')
            asm += call('sscanf')
            asm += popq('%rax')
            asm += movq_int(0, '%rsi')
            asm += cmpq_int(2147483647, '%rax')
            asm += cmovg('%rsi', '%rax')
            asm += cmpq_int(-2147483647, '%rax')
            asm += cmovl('%rsi', '%rax')
            asm += movq('%rax', acc_reg)
            asm += movq(acc_reg, f'{8 * int_contents_offset}({tmp_reg})')
            asm += movq(tmp_reg, acc_reg)
            return acc_reg
        elif exp.method == "IO.in_string":
            v_loc = cgen(AAST.New(exp.lineno, 'String'),st)
            asm += movq(v_loc, tmp_reg)
            asm += call('coolgetstr')
            asm += movq('%rax', acc_reg)
            asm += movq(acc_reg, f'{string_contents_offset * 8}({tmp_reg})')
            asm += movq(tmp_reg, acc_reg)
            return acc_reg
        elif exp.method == "Object.abort":
            abort_label = constant_labels['abort']
            asm += movq(abort_label, acc_reg)
            asm += movq(acc_reg, '%rdi')
            asm += call('cooloutstr')
            asm += movl_int(0, '%edi')
            asm += call('exit')
        elif exp.method == "Object.copy":
            asm += movq(f'{size_offset * 8}({self_reg})', tmp_reg)
            asm += movq_int(8, rsi)
            asm += movq(tmp_reg, '%rdi')
            asm += call('calloc')
            asm += movq('%rax', acc_reg)
            asm += pushq(acc_reg)
            branch_count += 1
            asm += globl(f'l{branch_count}')
            asm += label(f'l{branch_count}')
            asm += cmpq_int(0, tmp_reg)
            asm += je(f'l{branch_count + 1}')
            asm += movq(f'0({self_reg})', reg_three)
            asm += movq(reg_three, f'0({acc_reg})')
            asm += movq_int(8, reg_three)
            asm += addq(reg_three, self_reg)
            asm += addq(reg_three, acc_reg)
            asm += movq_int(1, reg_three)
            asm += subq(reg_three, tmp_reg)
            asm += jmp(f'l{branch_count}')

            branch_count += 1
            asm += globl(f'l{branch_count}')
            asm += label(f'l{branch_count}')
            asm += popq(acc_reg)
        elif exp.method == "Object.type_name":
            v_loc = cgen(AAST.New(exp.lineno, 'String'), st)
            asm += movq(f'{vtable_offset * 8}({self_reg})', tmp_reg)
            asm += movq(f'0({tmp_reg})', tmp_reg)
            asm += movq(tmp_reg, f'{8 * string_contents_offset}({acc_reg})')
            return acc_reg
        elif exp.method == "String.concat":
            v_loc = cgen(AAST.New(exp.lineno, 'String'), st)
            asm += movq(v_loc, reg_three)
            asm += movq(f'{2 * 8}({fp})', tmp_reg)
            asm += movq(f'{string_contents_offset * 8}({tmp_reg})', tmp_reg)
            asm += movq(f'{string_contents_offset * 8}({self_reg})', acc_reg)
            asm += call('coolstrcat')
            asm += movq(acc_reg, f'{string_contents_offset * 8}({reg_three})')
            asm += movq(reg_three, acc_reg)
            return acc_reg
        elif exp.method == "String.substr":
            s_loc = cgen(AAST.New(exp.lineno, 'String'), st)
            asm += movq(s_loc, reg_three)
            asm += movq(f'{3 * 8}({fp})', tmp_reg)
            asm += movq(f'{string_contents_offset * 8}({tmp_reg})', tmp_reg)
            asm += movq(f'{2 * 8}({fp})', acc_reg)
            asm += movq(f'{string_contents_offset * 8}({acc_reg})', acc_reg)
            asm += movq(f'{string_contents_offset * 8}({self_reg})', self_reg)
            asm += movq(self_reg, '%rdi')
            asm += movq(acc_reg, '%rsi')
            asm += movq(tmp_reg, '%rdx')
            asm += call('coolsubstr')
            asm += movq('%rax', acc_reg)
            asm += cmpq_int(0, acc_reg)
            branch_count += 1
            asm += jne(f'l{branch_count}')
            asm += movq_int(constant_labels["ERROR: 0: Exception: String.substr out of range"], acc_reg)
            asm += movq(acc_reg, '%rdi')
            asm += call('cooloutstr')
            asm += movl_int(0, '%edi')
            asm += call('exit')
            asm += globl(f'l{branch_count}')
            asm += label(f'l{branch_count}')
            asm += movq(acc_reg, f'{8 * string_contents_offset}({reg_three})')
            asm += movq(reg_three, acc_reg)
        elif exp.method == "String.length":
            i_loc = cgen(AAST.New(exp.lineno, 'Int'), st)
            asm += movq(i_loc, tmp_reg)
            asm += movq(f'{string_contents_offset * 8}({self_reg})', acc_reg)
            asm += movq(acc_reg, '%rdi')
            asm += movl_int(0, '%eax')
            asm += call('coolstrlen')
            asm += movq('%rax', acc_reg)
            asm += movq(acc_reg, f'{int_contents_offset * 8}({tmp_reg})')
            asm += movq(tmp_reg, acc_reg)
            return acc_reg
    elif isinstance(exp, AAST.Assign):
        loc = cgen(exp.exp, st)
        asm += f'\t\tmov {reg_three} <- {loc}\n'
        asm += f'\t\tst {st[exp.ident.name]} <- {reg_three};;assign\n'
        return loc
    elif isinstance(exp, AAST.Arithmetic):
        # 3 registers needed
        # first, evaluate the first operand, storing the result in a register
        asm += comment("arith start")
        e1_loc = cgen(exp.e1, st)
        asm += movq(f'{int_contents_offset * 8}({e1_loc})', acc_reg)
        
        # push first operand onto stack
        asm += movq(acc_reg, f'0({fp})')
        # asm += (f"\t\tpush {tmp_reg}\n")

        e2_loc = cgen(exp.e2, st)

        #store second operand into acc_reg
        #load unboxed integer constant value from Int object into register
        asm += movq(f'{int_contents_offset * 8}({e2_loc})', acc_reg)
        if isinstance(exp, AAST.Divide):
            branch_count += 1
            asm += cmpq_int(0, acc_reg)
            asm += jne(f'l{branch_count}')
            asm += movq(constant_labels[f"ERROR: {exp.lineno}: Exception: division by zero"], acc_reg)
            asm += call('cooloutstr')
            asm += movl_int(0, '%edi')
            asm += call('exit')
            asm += globl(f'l{branch_count}')
            asm += label(f'l{branch_count}')
            
        asm += movq(f'0({fp})', tmp_reg)

        # retrieve first operand from stack
        # asm += (f"\t\tpop {tmp_reg}\n")
        # add values together
        if isinstance(exp, AAST.Plus):
            asm += addq(tmp_reg, acc_reg)
        if isinstance(exp, AAST.Minus):
            asm += subq(tmp_reg, acc_reg)

        elif isinstance(exp, AAST.Times):
            asm += movq(tmp_reg, '%rax')
            asm += imull(f"{acc_reg}d", '%eax')
            asm += shlq_int(32, '%rax')
            asm += shrq_int(32, '%rax')
            asm += movl('%eax', '%r13d')
        elif isinstance(exp, AAST.Divide):
            asm +=movq_int(0, '%rdx')
            asm += movq(tmp_reg, '%rax')
            asm += cdq()
            asm += idivl('%r13d')
            asm += movq('%rax', acc_reg)

        # push on stack
        asm += movq(acc_reg, f'0({fp})')
        # create new Int object
        cgen(AAST.New(exp.lineno, 'Int'), st)

        # retrieve saved value
        asm += movq(f'0({fp})', tmp_reg)

        # throw that value into the newly-created int
        asm += movq(tmp_reg, f"{8 * int_contents_offset}({acc_reg})")

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


def format_constants_casm(class_names, constants):
    builtin =["abort", "ERROR: 0: Exception:"]
    # string_count = len(class_names) + len(builtin)
    constants_str = ""


    defaults = {
        'the.empty.string' : '',
        'percent.d' : '%ld',
        'percent.ld' : ' %ld'
    }

    for key, value in defaults.items():
        constants_str += globl(key)
        constants_str += label(key)
        for char in value:
            constants_str += f".byte {ord(char)} # '{char}'\n"
        constants_str += '.byte 0\n'
        constants_str += '\n'
        constant_labels[value] = key

    # constants_str += globl('the.empty.string')
    # constants_str += label('the.empty.string')
    # constants_str += ".byte 0\n"
    # constants_str += '\n'


    for i, cls in enumerate(class_names + builtin + constants):
        constants_str += globl(f'string{i}')
        constants_str += f'string{i}:\t\t# "{cls}"\n'
        for char in cls:
            constants_str += f".byte {ord(char)} # '{char}'\n"
        constants_str += '.byte 0\n'
        constants_str += '\n'
        constant_labels[cls] = f'string{i}'
    # for i, c in enumerate(builtin):
    #     constants_str += f'string{i + len(class_names)}:\t\tconstant "{c}"\n'
    #     constant_labels[c] = f'string{i + len(class_names)}'

    # for const in constants:
    #     if type(const) is str:
    #         constant_labels[const]= f'string{string_count}'
    #         constants_str += f'string{string_count}:\t\tconstant "{const}"\n'
    #         string_count += 1

    return constants_str

def create_vtables(class_names):
    global asm
    for cls in class_names:
        # create label for vtable
        asm += globl(f'{cls}..vtable')
        asm += (f"{cls}..vtable:\n")
        # label for constructor
        asm += f"\t\t.quad {constant_labels[cls]}\n"
        asm += (f"\t\t.quad {cls}..new") + "\n"
        # labels for other methods
        if cls in implementation_map:
            for method in implementation_map[cls]:
                asm += (f"\t\t.quad {method.method_label}") + "\n"
        asm += '\n'
def create_constructors(class_names):
    global asm
    global current_class
    global class_map

    for cls in class_names:
        current_class = cls
        asm += globl(f'{cls}..new')
        asm += label(f'{cls}..new')
        # calling convention
        asm += pushq(fp)
        asm += movq(sp, fp)
        
        temps = 1
        for attr in class_map[cls]:
            temps = max(temps, attr.num_temps)
        # A long int is 8 bytes
        asm += f'\t\t## stack room for temporaries: {temps}\n'
        asm += movq(f'${temps * 8}', tmp_reg)
        asm += subq(tmp_reg, sp)
        asm += f'\t\t## return address handling\n'
        asm += movq("$4", self_reg)
        asm += movq("$8", rsi)
        asm += movq(self_reg, "%rdi")
        # ask the OS for space in the heap
        asm += call("calloc")
        asm += movq("%rax", self_reg)
        asm += '\t\t## store class tag, object size and vtable pointer\n'

        # load size into a register
        # we should know this statically
        # vtable, attributes, class tag, object size
        s = len(class_map[cls]) + metadata_size
        if cls in ["Bool", "String", "Int"]:
            s += 1
        tag = class_tags[cls]
        asm += movq(f"${tag}", tmp_reg)
        asm += movq(tmp_reg, f'{classtag_offset}({self_reg})')

        asm += movq(f"${s}", tmp_reg)
        asm += movq(tmp_reg, f'{8 * size_offset}({self_reg})')

        # asm += (f"\t\tli {tmp_reg} <- {tag}\n")
        # asm += f"\t\tst {self_reg}[{classtag_offset}] <- {tmp_reg} ;;classtag \n"

        # asm += (f"\t\tli {tmp_reg} <- {s}")+ ";;size\n"
        # asm += (f"\t\tst {self_reg}[{size_offset}] <- {tmp_reg}\n")
        # get vtable pointer into newly-allocated space
        asm += movq(f"${cls}..vtable", tmp_reg)
        asm += movq(tmp_reg, f'{8 * (vtable_offset)}({self_reg})')
        asm += f'\t\t## initialize attributes\n'
        # asm += (f"\t\tst {self_reg}[{vtable_offset}] <- {tmp_reg}") + "\n"

        attr: AAST.Attribute

        st = {'self' : self_reg}
        for i, attr in enumerate(class_map[cls]):
            st[attr.id] = self_reg.off(i + metadata_size)

        # First initialize empty attributes
        for i, attr in enumerate(class_map[cls]):
                asm += f'\t\t## initialize attribute {attr.id} ({attr.type})\n'
                if attr.type in ["Bool", "Int", "String"]:
                    asm += pushq(fp)
                    asm += pushq(self_reg)
                    asm += movq(f'{attr.type}..new', tmp_reg)
                    asm += call_reg(tmp_reg)

                    asm += popq(self_reg)
                    asm += popq(fp)
                    asm += movq(acc_reg, f"{(i + metadata_size) * 8}({self_reg})")
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
                asm += movq(res, f"{8 * (i + metadata_size)}({self_reg})")
            else:
                if attr.type in ["Bool", "Int"]:
                    res = cgen(AAST.New(0, attr.type), st)
                else:
                    asm += f"\t\tli {acc_reg} <- 0\n"
                asm += movq(acc_reg, f'{8* (i + metadata_size)}({self_reg})')


        
        if cls == 'Bool' or cls == 'Int':
            asm += comment("load default value")
            asm += movq_int(0, acc_reg)
            asm += movq(acc_reg, f'{8 * int_contents_offset}({self_reg})')
        elif cls == 'String':
            asm += movq('the.empty.string', acc_reg)
            asm += movq(acc_reg, f'{string_contents_offset}({self_reg})')
        asm += movq(self_reg, acc_reg)
        asm += comment('return address handling')
        asm += movq(fp, sp)
        asm += popq(fp)
        asm += ret()

def create_methods():
    global asm
    global current_class
    method: AAST.MethodImplementation
    for method in ast:
        # make label
        current_class = method.class_name
        asm += f'.globl {method.method_label}\n'
        asm += (f"{method.method_label}:") + '\n'
        
        asm += pushq(fp)
        asm += movq(sp, fp)
        asm += movq(f'16({fp})', self_reg)
        if method.num_temps != 0:
            asm += movq_int(method.num_temps * 8, tmp_reg)
            asm += subq(tmp_reg, sp)
        asm += comment('return address handling')
        # asm += ("\t\tpush ra") + '\n'
        st = {}
        from_class = class_map[method.class_name]
        # determien which class the method belongs to
        # lookup the attributes in that class
        for i, attribute in enumerate(from_class):
            st[attribute.id] = self_reg.off(i + metadata_size)
        
        for i, formal in enumerate(method.formals):
            st[formal] = REG.FP_86(i + 2) # pushing other stuff on stack first
        st["self"] = self_reg

        cgen(method.exp, st)

        asm += comment('return address handling')
        asm += movq(fp, sp)
        asm += popq(fp)
        # if method.num_temps != 0:
        #     asm += f"\t\tli {tmp_reg} <- {method.num_temps  + len(method.formals)}\n"
        #     asm += f"\t\tadd {sp} <- {sp} {tmp_reg}\n"

        asm += ret()

def create_start_label():
    global asm
    asm += globl('start')
    asm += label('start')
    asm += '\t\t.globl main\n'
    asm += "\t\t.type main, @function\n"
    asm += label('main')
    asm += movq('$Main..new', tmp_reg)
    asm += pushq(fp)
    asm += call_reg(tmp_reg)
    asm += pushq(fp)
    asm += pushq(acc_reg)
    asm += movq('$Main.main', tmp_reg)
    asm += call_reg(tmp_reg)
    asm += movl('$0', "%edi")
    asm += call('exit')

def asm86(class_names, constants, _class_map, _implementation_map, _ast,_parent_map, _child_map, _class_tags):
    global class_map
    global implementation_map
    global ast
    global class_tags
    global current_class
    global parent_map
    global child_map
    global asm
    global self_reg
    global acc_reg
    global tmp_reg
    global reg_three
    self_reg = REG.R_86(12)
    acc_reg = REG.R_86(13)
    tmp_reg = REG.R_86(14)
    reg_three = REG.R_86(15)

    class_map = _class_map
    implementation_map = _implementation_map
    ast = _ast
    parent_map = _parent_map
    child_map = _child_map
    class_tags = _class_tags
    constant_block = format_constants_casm(class_names, constants)
    create_vtables(class_names)
    create_constructors(class_names)
    create_methods()
    asm += constant_block   

    # asm += UT.create_cmp(class_tags)
    create_start_label()
    asm += string_labels()
    return asm

