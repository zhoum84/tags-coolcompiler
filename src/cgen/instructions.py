def tab_and_endl(string):
    return f'\t\t{string}\n'

# General purpose movq
def movq(source, destination):
    return tab_and_endl(f"movq {source}, {destination}")

# Move an int value to a register
def movq_int(i, destination):
    return tab_and_endl(f"movq ${i}, {destination}")

def pushq(source):
    return tab_and_endl(f"pushq {source}")

def popq(source):
    return tab_and_endl(f"popq {source}")

def call(source):
    return tab_and_endl(f'call {source}')

def call_reg(source):
    return tab_and_endl(f'call *{source}')

def addq(source, destination):
    return tab_and_endl(f"addq {source}, {destination}")
def subq(source, destination):
    return tab_and_endl(f"subq {source}, {destination}")

def imull(source, destination):
    return tab_and_endl(f"imull {source}, {destination}")

def idivl(source):
    return tab_and_endl(f"idivl {source}")
def shlq_int(i, reg):
    return tab_and_endl(f"shlq {i}, {reg}")

def shrq_int(i, reg):
    return tab_and_endl(f"shrq {i}, {reg}")

def comment(comment):
    return tab_and_endl(f'## {comment}')

def ret():
    return tab_and_endl('ret')

def cdq():
    return tab_and_endl('cdq')
# moves a double word
def movl(source, destination):
    return tab_and_endl(f"movl {source}, {destination}")

def movl_int(i, destination):
    return tab_and_endl(f"movl ${i}, {destination}")

def cmpq(s1, s2):
    return tab_and_endl(f'cmpq {s1}, {s2}')

def cmpq_int(i, s):
    return tab_and_endl(f'cmpq ${i}, {s}')

def cmovg(source, destination):
    return tab_and_endl(f"cmovg {source}, {destination}")

def cmovl(source, destination):
    return tab_and_endl(f"cmovl {source}, {destination}")

def je(destination):
    return tab_and_endl(f'je {destination}')
def jne(destination):
    return tab_and_endl(f'jne {destination}')
def jmp(destination):
    return tab_and_endl(f'jmp {destination}')
def globl(label):
    return f'.globl {label}\n'

def label(label):
    return f'{label}:\n'