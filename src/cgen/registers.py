
class Register(object):
    def __init__(self, offset = None):
        self.offset = offset

class FP_86(Register):
    def __init__(self, offset=None):
        self.offset = offset
    
    def __str__(self):
        if self.offset == None:
            return "%rbp"
        return "%d(%%rbp)" % (self.offset * 8)

# Frame Pointer - Cool Assembly
class FP(Register):
    def __init__(self, offset=None):
        self.offset = offset
    
    def __str__(self):
        if self.offset == None:
            return "fp"
        return "fp[%d]" % self.offset

# Stack Pointer
class SP(Register):
    def __init__(self, offset=None):
        self.offset = offset
    
    def __str__(self):
        if self.offset == None:
            return "sp"
        return "sp[%d]" % self.offset

class SP_86(Register):
    def __init__(self, offset=None):
        self.offset = offset
    
    def __str__(self):
        if self.offset == None:
            return "%rsp"
        return "rsp[%d]" % self.offset


class R_86(Register):
    def __init__(self, which, offset=None):
        self.which = which
        self.offset = offset
    def off(self, offset): # get something offset from this register
        return R(self.which, offset)
    def __str__(self):
        if self.offset == None:
            return "%%r%d" % self.which
        return "%%r%d[%d]" % (self.which, self.offset)
 


class R(Register):
    def __init__(self, which, offset=None):
        self.which = which
        self.offset = offset
    def off(self, offset): # get something offset from this register
        return R(self.which, offset)
    def __str__(self):
        if self.offset == None:
            return "r%d" % self.which
        return "r%d[%d]" % (self.which, self.offset)
 
class RSI(Register):
    def __init__(self, offset=None):
        self.offset = offset
    
    def __str__(self):
        if self.offset == None:
            return "%rsi"
        return "rsi[%d]" % self.offset
