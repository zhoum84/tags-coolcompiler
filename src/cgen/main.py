import sys
import init as INIT
from constants import * 

def assign_tags(classes):
    tags = {}
    cpy = []
    
    for cls in (classes):
        if cls not in ["Int", "Bool", "String", "Object"]:
            cpy.append(cls)
    for i, cls in enumerate(cpy):
        tags[cls] = i + 11
    tags["Int"] = 1
    tags["Bool"] = 0
    tags["String"] = 3
    tags["Object"] = 10
    return tags

def __main__():

    if len(sys.argv) < 2: 
        print("Specify .cl-type input file.\n")
        exit()
    with open(sys.argv[1]) as f:
        lines = [l[:-1] for l in f.readlines()] # strip \n
    (class_map, class_names) = INIT.load_class_map(lines)
    (implementation_map, ast, constants) = INIT.load_implementation_map_and_ast(lines)
    (parent_map, child_map) = INIT.load_parent_map(lines)
    
    class_tags = assign_tags(class_names)
    if len(sys.argv) == 2:
        from asm import asm86
        asm = asm86(class_names,constants, class_map, implementation_map, ast,parent_map, child_map, class_tags)

        asm_filename = (sys.argv[1])[:-7] + "s"
        fout = open(asm_filename, 'w')
        fout.write(asm)

    elif sys.argv[2] == "--casm":
        from casm import casm
        asm = casm(class_names,constants, class_map, implementation_map, ast,parent_map, child_map, class_tags)

        asm_filename = (sys.argv[1])[:-4] + "asm"
        fout = open(asm_filename, 'w')
        fout.write(asm)

if __name__ == '__main__':
    __main__()
