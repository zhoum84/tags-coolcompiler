import main as M

# ASM that will always be generated and will never change

comparisons = ["lt", "le", 'eq']
def create_cmp(class_tags):
    s = ""
    for c in comparisons:
        s += cmp(c, class_tags)
    return s
    
def cmp(oper, class_tags):
    s = f"{oper}_handler:\n"
    s += f";;{M.acc_reg} holds e1, {M.tmp_reg} holds e2\n"
    s += '\t\tmov fp <- sp\n'
    s += '\t\tpop r0\n'
    s += '\t\tpush ra\n'
    s += f'\t\tli {M.reg_three} <- 0\n'
    s += f'\t\tld {M.acc_reg} <- fp[3]\n'
    s += f'\t\tld {M.tmp_reg} <- fp[2]\n'
    if oper != 'lt':
        s += f'\t\tbeq {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    s += f'\t\tbeq {M.acc_reg} {M.reg_three} {oper}_false\n'
    s += f'\t\tbeq {M.tmp_reg} {M.reg_three} {oper}_false\n'
    s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[0]\n'
    s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[0]\n'
    
    s += f'\t\tadd {M.acc_reg} <- {M.acc_reg} {M.tmp_reg}\n'
    s += f'\t\tli {M.tmp_reg} <- {2 * class_tags["Bool"]}\n'
    s += f'\t\tbeq {M.acc_reg} {M.tmp_reg} {oper}_bool\n'
    s += f'\t\tli {M.tmp_reg} <- {2 * class_tags["Int"]}\n'
    s += f'\t\tbeq {M.acc_reg} {M.tmp_reg} {oper}_int\n'
    s += f'\t\tli {M.tmp_reg} <- {2 * class_tags["String"]}\n'
    s += f'\t\tbeq {M.acc_reg} {M.tmp_reg} {oper}_string\n'
    if oper == 'eq':
        s += f'\t\tld {M.acc_reg} <- fp[3]\n'
        s += f'\t\tld {M.tmp_reg} <- fp[2]\n'
        s += f'\t\tbeq {M.acc_reg} {M.tmp_reg} eq_true\n'
        
    s += f'{oper}_false:\n'
    s += '\t\tpush fp\n'
    s += '\t\tpush r0\n'
    s += f'\t\tla {M.tmp_reg} <- Bool..new\n'
    s += f'\t\tcall {M.tmp_reg}\n'
    s += '\t\tpop r0\n'
    s += '\t\tpop fp\n'
    s += f'\t\tjmp {oper}_end\n'

    s += f'{oper}_true:\n'
    s += '\t\tpush fp\n'
    s += '\t\tpush r0\n'
    s += f'\t\tla {M.tmp_reg} <- Bool..new\n'
    s += f'\t\tcall {M.tmp_reg}\n'
    s += '\t\tpop r0\n'
    s += '\t\tpop fp\n'
    s += f'\t\tli {M.tmp_reg} <- 1\n'
    s += f'\t\tst {M.acc_reg}[{M.bool_contents_offset}] <- {M.tmp_reg}\n'
    s += f'\t\tjmp {oper}_end\n'

    s += f'{oper}_bool:\n'
    s += f'\t\tld {M.acc_reg} <- fp[3]\n'
    s += f'\t\tld {M.tmp_reg} <- fp[2]\n'
    s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[{M.bool_contents_offset}]\n'
    s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[{M.bool_contents_offset}]\n'
    if oper == 'lt':
        s += f'\t\tblt {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    elif oper == 'le':
        s += f'\t\tble {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    elif oper == "eq":
        s += f'\t\tble {M.acc_reg} {M.tmp_reg} {oper}_true\n'

    s += f'\t\tjmp {oper}_false\n'

    s += f'{oper}_int:\n'
    s += f'\t\tld {M.acc_reg} <- fp[3]\n'
    s += f'\t\tld {M.tmp_reg} <- fp[2]\n'
    s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[{M.int_contents_offset}]\n'
    s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[{M.int_contents_offset}]\n'
    if oper == 'lt':
        s += f'\t\tblt {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    elif oper == 'le':
        s += f'\t\tble {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    elif oper == 'eq':
        s += f'\t\tbeq {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    
    s += f'\t\tjmp {oper}_false\n'

    s += f'{oper}_string:\n'
    s += f'\t\tld {M.acc_reg} <- fp[3]\n'
    s += f'\t\tld {M.tmp_reg} <- fp[2]\n'
    # s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[3]\n'
    # s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[3]\n'
    s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[{M.string_contents_offset}]\n'
    s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[{M.string_contents_offset}]\n'
    if oper == 'lt':
        s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[0]\n'
        s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[0]\n'
        s += f'\t\tblt {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    elif oper == 'le':
        s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[0]\n'
        s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[0]\n'
        s += f'\t\tble {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    elif oper == 'eq':
        s += f'\t\tld {M.acc_reg} <- {M.acc_reg}[0]\n'
        s += f'\t\tld {M.tmp_reg} <- {M.tmp_reg}[0]\n'
        s += f'\t\tbeq {M.acc_reg} {M.tmp_reg} {oper}_true\n'
    s += f'\t\tjmp {oper}_false\n'

    s += f'{oper}_end:\n'
    s += '\t\tpop ra\n'
    s += f'\t\tli {M.tmp_reg} <- 2\n'
    s += f'\t\tadd sp <- sp {M.tmp_reg}\n'
    s += '\t\treturn\n'

    return s

def dfs(cls_map, name):
    result = []
    stack = [name]

    while stack:
        current_node = stack.pop()
        result.append(current_node)

        # Add children in reverse order to process them from left to right
        if current_node in cls_map:
            for child in reversed(cls_map[current_node]):
                stack.append(child)
    return result

