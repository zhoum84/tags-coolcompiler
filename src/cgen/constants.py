import registers as REG
# Class --> Attributes
class_map = {}

# Class --> Methods
implementation_map = {}

# static strings --> string labels
constant_labels = {}

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

