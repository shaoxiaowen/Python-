import collections
import operator
import dis
import sys
import types
import inspect


class VirtualMachineError(Exception):
    pass

Block=collections.namedtuple("Block","type,handler,stack_height")
class VirtualMachine(object):
    def __init__(self):
        # 调用栈
        self.frames = []
        # 当前运行的帧
        self.frame = None
        # frame返回时的返回值
        self.return_value = None
        self.last_exception = None

    def run_code(self, code, global_names=None, local_names=None):
        """运行python程序的入口，程序编译后生成code_obj,这里的code_obj在参数code中，
            run_code根据输入的code_obj新建一个frame并开始运行
        """
        frame = self.make_frame(
            code, global_names=global_names, local_names=local_names)
        self.run_frame(frame)

    # 新建一个帧，code为code_obj,callargs为函数调用时的参数
    def make_frame(self, code, callargs={}, global_names=None, local_names=None):
        if global_names is not None:
            global_names = global_names
            if local_names is None:
                local_names = global_names
        elif self.frames:
            global_names = self.frame.global_names
            local_names = {}
        else:
            global_names = local_names = {
                '__builtins__': __builtins__,
                '__name__': '__main__',
                '__doc__': None,
                '__package__': None
            }
        # 将函数调用时的参数更新到局部变量空间中
        local_names.update(callargs)
        frame = Frame(code, global_names, local_names, self.frame)
        return frame

    #调用栈压入frame
    def push_frame(self,frame):
        self.frames.append(frame)
        self.frame=frame

    # 调用栈弹出frame
    def pop_frame(self):
        self.frames.pop()
        if self.frames:
            self.frame = self.frames[-1]
        else:
            self.frame = None

    # 运行frame
    def run_frame(self, frame):
        """运行帧直至它返回"""
        self.push_frame(frame)
        while True:
            byte_name,arguments=self.parse_byte_and_args()

            why=self.dispatch(byte_name,arguments)

            while why and frame.block_stack:
                why=self.manage_block_stack(why)
            
            if why:
                break
        self.pop_frame()

        if why=='exception':
            exc,val,tb=self.last_exception
            e=exc(val)
            e.__traceback__=tb
            raise e
        return self.return_value
    
    #数据栈操作
    def top(self):
        return self.frame.stack[-1]

    def pop(self):
        return self.frame.stack.pop()
    
    def push(self,*vals):
        self.frame.stack.extend(vals)
    
    def popn(self,n):
        """弹出多个值"""
        if n:
            ret=self.frame.stack[-n:]
            self.frame.stack[-n:]=[]
            return ret
        else:
            return []

    def parse_byte_and_args(self):
        f=self.frame
        opoffset=f.last_instruction
        #取得要运行的指令
        byteCode=ord(f.code_obj.co_code[opoffset])
        f.last_instruction+=1
        #指令名称
        byte_name=dis.opname[byteCode]
        #指令吗<dis.HAVE_ARGUMENT的都是无参数指令，其他则是有参数指令>
        if byteCode>=dis.HAVE_ARGUMENT:
            #取得后两字节的参数
            arg=f.code_obj.co_code[f.last_instruction:f.last_instruction+2]
            f.last_instruction+=2
            #参数第一个字节为参数实际低位，第二个字节为参数实际高位
            arg_val=ord(arg[0])+(ord(arg[1])*256)
            if byteCode in dis.hasconst:    #查找常量
                arg=f.code_obj.co_consts[arg_val]
            elif byteCode in dis.hasname:   #查找变量名
                arg=f.code_obj.co_names[arg_val]
            elif byteCode in dis.haslocal:  #查找局部变量名
                arg=f.code_obj.co_varnames[arg_val]
            elif byteCode in dis.hasjrel:   #计算跳转位置
                arg=f.last_instruction+arg_val
            else:
                arg=arg_val
            argument=[arg]
        else:
            argument=[]
        
        return byte_name,argument
    
    def dispatch(self,byte_name,argument):
        why=None
        try:
            #通过指令名得到对应的方法函数
            bytecode_fn=getattr(self,'byte_%s' % byte_name,None)
            if bytecode_fn is None:
                #这里对一元操作，二元操作和其他操作做了区分
                if byte_name.startswith('UNARY_'):
                    self.unaryOperator(byte_name[6:])
                elif byte_name.startswith('BINARY_'):
                    self.binaryOperator(byte_name[7:])
                else:
                    raise VirtualMachineError(
                        "unsupported bytecode type: %s" %byte_name
                    )
            else:
                why=bytecode_fn(*argument)
        except:
            #存储运行指令时的异常信息
            self.last_exception=sys.exc_info()[:2]+(None,)
            why='exception'
        return why
    
    def push_block(self,b_type,handler=None):
        stack_height=len(self.frame.stack)
        self.frame.block_stack.append(Block(b_type,handler,stack_height))

    def pop_block(self):
        return self.frame.block_stack.pop()
    
    def unwind_block(self,block):
        """Unwind the value on the data stack corresponding to a given block."""
        if block.type=='except-handler':
            #The exception itself is on the stack as type,value,and traceback
            offset=3
        else:
            offset=0
        while len(self.frame.stack)>block.stack_height+offset:
            self.pop()
        
        if block.type=='except-handler':
            trackback,value,exctype=self.popn(3)
            self.last_exception=exctype,value,trackback
    
    def manage_block_stack(self,why):
        """管理一个frame的block栈，在循环、异常处理、返回这几个方面操作block栈与数据栈"""
        frame=self.frame
        block=frame.block_stack[-1]
        if block.type=='loop' and why=='continue':
            self.jump(self.return_value)
            why=None
            return why
        
        self.pop_block()
        self.unwind_block(block)

        if block.type=='loop' and why=='break':
            why=None
            self.jump(block.handler)
            return why
        
        if(block.type in ['setup-except','finally'] and why=='exception'):
            self.push_block('except-handler')
            exctype,value,tb=self.last_exception
            self.push(tb,value,exctype)
            self.push(tb,value,exctype)
            why=None
            self.jump(block.handler)
            return why

        elif block.type=='finally':
            if why in ('return','continue'):
                self.push(self.return_value)
            
            self.push(why)

            why=None
            self.jump(block.handler)
            return why
        return why
    
    def byte_LOAD_CONST(self,const):
        self.push(const)
    
    def byte_POP_TOP(self):
        self.pop()
    
    # Names
    def byte_LOAD_NAME(self,name):
        frame=self.frame
        if name in frame.f_locals:
            val=frame.f_locals[name]
        
        elif name in frame.f_globals:
            val=frame.f_globals[name]
        
        elif name in frame.f_builtins:
            val=frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined" % name)
        self.push(val)
    
    def byte_STORE_NAME(self,name):
        self.frame.f_locals[name]=self.pop()

    def byte_LOAD_FAST(self,name):
        if name in self.frame.f_locals:
            val=self.frame.f_locals[name]
        else:
            raise UnboundLocalError(
                "local variable '%s' referenced before assignement" % name
            )
        self.push(val)
    
    def byte_LOAD_GLOBAL(self,name):
        f=self.frame
        if name in f.f_globals:
            val=f.f_globals[name]
        elif name in f.f_builtins:
            val=f.f_builtins[name]
        else:
            raise NameError("global name '%s' is not defined" % name)
        
        self.push(val)
    
    ## Operators
    BINARY_OPERATORS = {
        'POWER':    pow,
        'MULTIPLY': operator.mul,
        'FLOOR_DIVIDE': operator.floordiv,
        'TRUE_DIVIDE':  operator.truediv,
        'MODULO':   operator.mod,
        'ADD':      operator.add,
        'SUBTRACT': operator.sub,
        'SUBSCR':   operator.getitem,
        'LSHIFT':   operator.lshift,
        'RSHIFT':   operator.rshift,
        'AND':      operator.and_,
        'XOR':      operator.xor,
        'OR':       operator.or_,
    }

    def binaryOperator(self,op):
        x,y=self.popn(2)
        self.push(self.BINARY_OPERATORS[op](x,y))

    COMPARE_OPERATORS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.gt,
        operator.ge,
        lambda x, y: x in y,
        lambda x, y: x not in y,
        lambda x, y: x is y,
        lambda x, y: x is not y,
        lambda x, y: issubclass(x, Exception) and issubclass(x, y),
    ]
    
    def byte_COMPARE_OP(self,opnum):
        x,y=self.popn(2)
        self.push(self.COMPARE_OPERATORS[opnum](x,y))
    
    ## Attributes and indexing

    def byte_LOAD_ATTR(self,attr):
        obj=self.pop()
        val=getattr(obj,attr)
        self.push(val)
    
    def byte_STORE_ATTR(self,name):
        val,obj=self.popn(2)
        setattr(obj,name,val)

    ##Building
    def byte_BUILD_LIST(self,count):
        elts=self.popn(count)
        self.push(elts)
    
    def byte_BUILD_MAP(self,size):
        the_map,val,key=self.popn(3)
        the_map[key]=val
        self.push(the_map)
    
    def byte_LIST_APPEND(self,count):
        val=self.pop()
        the_list=self.frame.stack[-count]#peek
        the_list.append(val)

    #Jumps    
    def byte_JUMP_FORWARD(self,jump):
        self.jump(jump)
    
    def byte_JUMP_ABSOLUTE(self,jump):
        self.jump(jump)
    
    def byte_POP_JUMP_IF_TRUE(self,jump):
        val = self.pop()
        if val:
            self.jump(jump)
    
    def byte_POP_JUMP_IF_FALSE(self,jump):
        val=self.pop()
        if not val:
            self.jump(jump)
    
    def jump(self,jump):
        self.frame.last_instruction=jump
    
    ## Blocks
    def byte_SETUP_LOOP(self,dest):
        self.push_block('loop',dest)
    
    def byte_GET_ITER(self):
        self.push(iter(self.pop()))
    
    def byte_FOR_ITER(self,jump):
        iterobj=self.top()
        try:
            v=next(iterobj)
            self.push(v)
        except StopIteration:
            self.pop()
            self.jump(jump)
    
    def byte_BREAK_LOOP(self):
        return 'break'
    
    def byte_POP_BLOCK(self):
        self.pop_block()
    
    ## Functions

    def byte_MAKE_FUNCTION(self,argc):
        name=None
        code=self.pop()
        defaults=self.popn(argc)
        globs=self.frame.f_globals
        fn=Function(name,code,globs,defaults,None,self)
        self.push(fn)
    
    def byte_CALL_FUNCTION(self,arg):
        lenKw,lenPos=divmod(arg,256)
        posargs=self.popn(lenPos)

        func=self.pop()
        frame=self.frame
        retval=func(*posargs)
        self.push(retval)
    
    def byte_RETURN_VALUE(self):
        self.return_value=self.pop()
        return "return"

    ## Prints
    def byte_PRINT_ITEM(self):
        item=self.pop()
        sys.stdout.write(str(item))
    
    def byte_PRINT_NEWLINE(self):
        print ("")


class Function(object):
    #__slots__会固定对象的属性，无法再动态添加新的属性，这样可以节省内存空间
    __slots__=[
        'func_code','func_name','func_defaults','func_globals',
        'func_locals','func_dict','func_closure',
        '__name__','__dict__','__doc__',
        '_vm','_func',
    ]

    def __init__(self,name,code,globs,defaults,closure,vm):
        """这部分不需要去探究，但是代码会尽量注释说明"""
        self._vm=vm
        #这里的code即所调用函数的code_obj
        self.func_code=code
        #函数名会存在code.co_name中
        self.func_name=self.__name__=name or code.co_name
        #函数参数的默认值，如func(a=5,b=3),则func_defaults为(5,3)
        self.func_defaults=tuple(defaults)
        self.func_globals=globs
        self.func_locals=self._vm.frame.f_locals
        self.__dict__={}
        #函数的闭包信息
        self.func_closure=closure
        self.__doc__=code.co_consts[0] if code.co_consts else None

        # 又是我们需要用到真实Python的函数，下面的代码是为它准备的。
        kw={
            'argdefs':self.func_defaults,
        }
        #为闭包创建cell对象
        if closure:
            kw['closure']=tuple(make_cell(0) for _ in closure)
        self._func=types.FunctionType(code,globs,**kw)
    def __call__(self,*args,**kwargs):
        """每当调用一次函数，会创建一个新frame运行"""
        #通过inspect获得函数的参数
        callargs=inspect.getcallargs(self._func,*args,**kwargs)
        #创建函数的帧
        frame=self._vm.make_frame(self.func_code,callargs,self.func_globals,{})
        return self._vm.run_frame(frame)

def make_cell(value):
    """创建一个真实的cell对象"""
    fn=(lambda x:lambda:x)(value)
    return fn.__closure__[0]


"""
   Frame对象包括一个 code object，局部，全局、内置（builtin）的名字空间(namespace)，
   对调用它的帧的引用，一个数据栈、一个block栈以及最后运行的指令的序号(在code_obj字节码中的位置)
"""
class Frame(object):
    def __init__(self, code_obj, global_names, local_names, prev_names):
        self.code_obj = code_obj
        self.f_globals = global_names
        self.f_locals = local_names
        self.prev_names = prev_names

        # 数据线
        self.stack = []
        # block栈
        self.block_stack = []
        if prev_names:
            self.builtin_names = prev_names.builtin_names
        else:
            self.builtin_names = local_names['__builtins__']
            if hasattr(self.builtin_names, '__dict__'):
                self.builtin_names = self.builtin_names.__dict__

        # 最后运行的指令
        self.last_instruction = 0

if __name__=='__main__':
    code="""
def loop():
    x = 1
    while x < 5:
        if x==3:
            break
        x = x + 1
        print (x)
    return x
loop()
    """

    code_obj=compile(code,"tmp","exec")
    vm=VirtualMachine()
    vm.run_code(code_obj)
