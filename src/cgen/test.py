import os
import sys
test_files = [
    'hello-world.cl-type',
    'correct.cl-type',
    'basic_math.cl-type',
    'if.cl-type',
    'func.cl-type',
    'block.cl-type',
    'abort.cl-type',
    'type_name.cl-type',
    'new.cl-type',
    'let.cl-type',
    'let1.cl-type',
    'let2.cl-type',
    'compare.cl-type',
    'le.cl-type',
    'eq.cl-type',
    'isvoid.cl-type',
    'copy.cl-type',
    'neg.cl-type',
    'strlen.cl-type',
    'concat.cl-type',
    'substr.cl-type',
]

tests2 = [
    'while.cl-type',
    'case.cl-type',
    'alias.cl-type',
    'dnest.cl-type',
    'other_funcs.cl-type',
    'static.cl-type',
    'self.cl-type',
    'self-case.cl-type',
    's_copy.cl-type',
    'void-cmp.cl-type',
    'ms.cl-type',
    'new_self_type.cl-type',
    'letbool.cl-type',
    'mlet.cl-type',
    'bigcase.cl-type',
    'scoping.cl-type',
    'eval.cl-type',
    'fact.cl-type',
    'sinit.cl-type',
    'lneg.cl-type',
]

examples = [
    'atoi.cl-type',
    'list.cl-type'
]

errors = [
    'void-case.cl-type',
    'badsubstr.cl-type',
    'void-stat.cl-type',
    'casev.cl-type',
]

t3 = [
    "test1.cl-type",
    "test2.cl-type",
    "test3.cl-type",
]

def call(f, d):
    global bad
    result = ""
    fname = f[:-4] + 'asm'
    os.system(f'./cool {d}/cl-asm/{fname} > {f[:-7]}out')
    with open(f[:-7] + 'out', 'r') as f1, open(f'./{d}/out/' + f[:-7] + 'out-c', 'r') as f2:
        content1 = f1.read()
        content2 = f2.read()
        if content1 == content2:
            result += (f"{fname}: \033[92mGOOD\033[0m") + '\n'
        else:
            result += (f"{fname}: \033[91mERROR\033[0m") + '\n'
            bad += 1
    os.system(f'mv {f[:-7]}out {d}/out >nul')
    return result


def create_opt():
    for f in test_files:
        # print(f[:-8])
        os.system(f'./cool --opt --asm tests/{f[:-5]} --out {f[:-8]}-opt')
        os.system(f'mv {f[:-8]}-opt.cl-asm tests/opt')
    for f in tests2:
        # print(f[:-8])
        os.system(f'./cool --opt --asm tests2/{f[:-5]} --out {f[:-8]}-opt')
        os.system(f'mv {f[:-8]}-opt.cl-asm tests2/opt')
    for f in examples:
        os.system(f'./cool --opt --asm ce/{f[:-5]} --out {f[:-8]}-opt')
        os.system(f'mv {f[:-8]}-opt.cl-asm ce/opt')
    for f in t3:
        os.system(f'./cool --opt --asm tests3/{f[:-5]} --out {f[:-8]}-opt')
        os.system(f'mv {f[:-8]}-opt.cl-asm tests3/opt')

def test_86():
    result = ''
    result += 'SUITE 1:\n'
    for f in test_files:
        os.system(f'python main.py tests/type/{f} --casm')
        result += call(f, 'tests')
    result += '\nSUITE 2:\n'
    for f in tests2:
        os.system(f'python main.py tests2/type/{f} --casm')
        result += call(f, 'tests2')

    result += '\nSUITE 3:\n'    
    for f in examples:
        os.system(f'python main.py ce/type/{f} --casm')
        result += call(f, 'ce')

    result += '\nSUITE 4:\n'    
    for f in t3:
        os.system(f'python main.py tests3/type/{f} --casm')
        result += call(f, 'tests3')

    result += '\nERROR SUITE:\n'
    for f in errors:
        os.system(f'python main.py bad/type/{f} --casm')
        result += call(f, 'bad')
    print(result[:-1])
    if bad > 0:
        print(f"There are {bad} failures.")

def test_casm():
    result = ''
    result += 'SUITE 1:\n'
    for f in test_files:
        os.system(f'python main.py tests/type/{f}')
        result += call(f, 'tests')
    result += '\nSUITE 2:\n'
    for f in tests2:
        os.system(f'python main.py tests2/type/{f}')
        result += call(f, 'tests2')

    result += '\nSUITE 3:\n'    
    for f in examples:
        os.system(f'python main.py ce/type/{f}')
        result += call(f, 'ce')

    result += '\nSUITE 4:\n'    
    for f in t3:
        os.system(f'python main.py tests3/type/{f}')
        result += call(f, 'tests3')

    result += '\nERROR SUITE:\n'
    for f in errors:
        os.system(f'python main.py bad/type/{f}')
        result += call(f, 'bad')
    print(result[:-1])
    if bad > 0:
        print(f"There are {bad} failures.")

bad = 0
def main():
    if len(sys.argv) == 1:
        print("Testing x86...")
        test_86()
    elif sys.argv[1] == "setup":
        create_opt()
    elif sys.argv[1] == "clasm":
        print("Testing cl-asm...")
        test_casm()
    else:
        test_86()

if __name__ == "__main__": 
    main()

