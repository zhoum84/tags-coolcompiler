import sys
import ply.lex as lex
filename = sys.argv[1]
file_handle = open(filename, "r")
file_contents = file_handle.read()

reserved = {
   'then' : 'then',
   'case' : 'case',
   'class' : 'class',
   'else' : 'else',
   'esac' : 'esac',
    'fi' : 'fi',
    'if' : 'if',
    'in' : 'in',
    'inherits' : 'inherits',
    'isvoid' :     'isvoid',
    'let' : 'let',
    'loop' : 'loop',
    'new' : 'new',
    'not' : 'not',
    'of' : 'of',
    'pool' : 'pool',
    'then' : 'then',
    'while' : 'while',
}

tokens = [
    'at',
    'colon',
    'comma',
    'divide',
    'dot',
    'equals',
    'integer',
    'larrow',
    'lbrace',
    'le',
    'lparen',
    'lt',
    'minus',
    'plus',
    'rarrow',
    'rbrace',
    'rparen',
    'semi',
    'string',
    'tilde',
    'times',
    'true',
    'false',
    'singlelinecomment',
    'multilinecomment',
    'identifier',
    'type',
    'ID',
]

tokens += reserved.values()


t_plus   = r'\+'
t_times   = r'\*'
t_divide  = r'/'
t_rparen  = r'\)'
t_at = r'@'
t_colon = r':'
t_comma = r','
t_dot = r'\.'
t_equals = r'='
t_larrow = r'<-'
t_lbrace = r'\{'
t_le = r'<='
t_lparen = r'\('
t_lt = r'<'
t_minus = r'-'
t_rarrow = r'=>'
t_rbrace = r'\}'
t_semi = r';'
t_tilde = r'~'

# State declaration
states = (('comment', 'exclusive'),)
comment_count = 0

# True and False require their own rules (first letter lowercase)
def t_true(t):
    r't[rR][uU][eE]'
    return t

def t_false(t):
    r'f[aA][lL][sS][eE]'
    return t
def t_ID(t):
    r'[a-zA-Z][a-zA-Z_0-9]*'
    str = t.value
    type = "type"

    if not (str[0].isupper()):
        type="identifier"
    # Check for reserved words
    # If the word isn't reserved, it defaults to a type or an identifier
    t.type = reserved.get(t.value.lower(),type)    
    return t

def t_string(t):
    r'"((\\\\)|(\\")|[^"])*"'

    # Check for newlines
    if (t.value.count("\n") > 0):
        print('ERROR: %d: Lexer: invalid character: "' % (t.lexer.lineno))
        exit(1)

    # Check for length
    if len(t.value) > 1026:
        print("ERROR: %d: Lexer: string constant is too long (%d > 1024)" % (t.lexer.lineno, len(t.value) - 2))
        exit(1)

    # Check for invalid characters
    for char in t.value:
        if ord(char) == 0:
            print("ERROR: %d: Lexer: string contains non-printable character" % (t.lexer.lineno))
            exit(1)

    # Handle escaped characters
    parsed = ""
    is_skip = False
    for i in range(1, len(t.value)):
        if is_skip:
            is_skip = False
            continue
        if(t.value[i]) == "\\":
        # Skip the next character after a backslash
            is_skip = True
        else:
            parsed += t.value[i]

    # If the closing quote gets escaped, throw an error
    if(len(parsed) == 0 or parsed[-1] != '"'):
        print("ERROR: %d: Lexer: Illegal character '%s'" % (t.lexer.lineno, t.value[0]))
        exit(1)

    # Remove start/end quotes
    t.value = t.value[1:-1]
    return t

def t_singlelinecomment(t):
    r'\-\-[^\n]*'

# Enter Comment state
def t_multilinecomment(t):
    r'\(\*'
    t.lexer.begin("comment")
    global comment_count
    comment_count = 1

def t_comment_newline(t):
    r'\n'
    t.lexer.lineno += 1

def t_comment_morecomment(t):
    r'\(\*'
    global comment_count
    comment_count += 1

def t_comment_endcomment(t):
    r'\*\)'
    global comment_count
    comment_count -= 1
    if(comment_count == 0):
        # Exit comment state
        t.lexer.begin('INITIAL')

def t_integer(t):
    r'\d+'
    t.value = int(t.value)    
    if(t.value > 2 ** 31 - 1):
        print("ERROR: %d: Lexer: not a non-negative 32-bit signed integer: '%s'" % (t.lexer.lineno, t.value))
        exit(1)

    return t

# Define a rule so we can track line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# A string containing ignored characters (spaces and tabs)
t_ignore  = ' \t \r \v \f'

# Error handling rule
def t_error(t):
    print("ERROR: %d: Lexer: Illegal character '%s'" % (t.lexer.lineno, t.value[0]))
    exit(1)

def t_comment_error(t):
    t.lexer.skip(1)

t_comment_ignore = ''

# Build the lexer
lexer = lex.lex()

# Give the lexer some input
lexer.input(file_contents)


out_string = ""

# Tokenize
while True:
    tok = lexer.token()
    if not tok: 
        newline_count = file_contents.count("\n") + 1
        if comment_count > 0:
            # Handle EOF in comments
            print("ERROR: %d: Lexer: EOF in (* comment *) " % newline_count)
            exit(1)
        break      # No more input
    out_string = out_string + (str(tok.lineno) + "\n")
    out_string = out_string +(tok.type + '\n')
    if tok.type in ['integer']:
        out_string = out_string + str(tok.value) + '\n'
    elif tok.type in ['type', 'identifier', 'string']:
        out_string = out_string + tok.value + '\n'
    
out_file = open(sys.argv[1] + "-lex", "w")
out_file.write(out_string)
out_file.close()
