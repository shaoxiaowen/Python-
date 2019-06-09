# 列表 append：在末尾添加，pop：默认移除最后一个元素，append和pop可以模拟栈操作
class Interpreter:
    def __init__(self):
        self.stack=[]
        #存储变量映射关系的字典变量
        self.environment={}
    
    def STORE_NAME(self,name):
        val=self.stack.pop()
        self.environment[name]=val
    
    def LOAD_NAME(self,name):
        val=self.environment[name]
        self.stack.append(val)

    def LOAD_VALUE(self,number):
        self.stack.append(number)
    
    def PRINT_ANSWER(self):
        answer=self.stack.pop()
        print(answer)

    def ADD_TWO_VALUES(self):
        first_num=self.stack.pop()
        second_num=self.stack.pop()
        total=first_num+second_num
        self.stack.append(total)
    
    def parse_argument(self,instruction,argument,what_to_execute):
        #解析命令参数
        #使用常量列表的方法
        numbers=["LOAD_VALUE"]
        #使用变量名列表的方法
        names=["LOAD_NAME","STORE_NAME"]

        if instruction in numbers:
            argument=what_to_execute["numbers"][argument]
        elif instruction in names:
            argument=what_to_execute["names"][argument]

        return argument

    
    def run_code(self,what_to_execute):
        # 指令列表：
        instructions=what_to_execute["instructions"]        
        #遍历指令列表，一个一个执行
        for each_step in instructions:
            #得到指令和相应的参数
            instruction,argument=each_step
            argument=self.parse_argument(instruction,argument,what_to_execute)
            if instruction=="LOAD_VALUE":
                self.LOAD_VALUE(argument)
            elif instruction=="ADD_TWO_VALUES":
                self.ADD_TWO_VALUES()
            elif instruction=="PRINT_ANSWER":
                self.PRINT_ANSWER()
            elif instruction=="STORE_NAME":
                self.STORE_NAME(argument)
            elif instruction=="LOAD_NAME":
                self.LOAD_NAME(argument)

    #使用反射，简化代码
    def execute(self,what_to_execute):
        instructions=what_to_execute["instructions"]
        for each_step in instructions:
            instruction,argument = each_step
            argument=self.parse_argument(instruction,argument,what_to_execute)
            byteCode_Method=getattr(self,instruction)
            if argument is None:
                byteCode_Method()
            else:
                byteCode_Method(argument)
 
#编译后的字节码
what_to_execute = {
    "instructions": [("LOAD_VALUE", 0),
                     ("STORE_NAME", 0),
                     ("LOAD_VALUE", 1),
                     ("STORE_NAME", 1),
                     ("LOAD_NAME", 0),
                     ("LOAD_NAME", 1),
                     ("ADD_TWO_VALUES", None),
                     ("PRINT_ANSWER", None)],
    "numbers": [1, 2],
    "names":   ["a", "b"] } 

interpreter=Interpreter()
# interpreter.run_code(what_to_execute)
interpreter.execute(what_to_execute)