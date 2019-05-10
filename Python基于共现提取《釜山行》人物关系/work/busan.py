import os ,sys
import jieba,codecs,math
import jieba.posseg as pseg

names={}             # 姓名字典 记录人物出现次数
relationships={}    # 关系字典
lineNames=[]        # 每段内人物关系，记录每一句话中有哪些任务

jieba.load_userdict("dict.txt")   # 加载字典
with codecs.open("busan.txt","r","utf8") as f:
    for line in f.readlines():    
        poss=pseg.cut(line)       # 分词并返回该词词性
        lineNames.append([])      # 为新读入的一段添加任务名称列表
        for w in poss:
            if w.flag !="nr" or len(w.word) <2:
                continue          # 当分词长度小于2或该词词性不为nr时，认为该词不为人名
            lineNames[-1].append(w.word)  #为当前段的环境增加一个人物
            if names.get(w.word) is None:
                names[w.word]=0 
                relationships[w.word]={}
            names[w.word]+=1      # 该人物出现次数加1

# for name ,times in names.items():
#     print(name,times)

for line in lineNames:
    for name1 in line:
        for name2 in line:
            if name1==name2:
                continue
            if relationships[name1].get(name2) is None:  #若两人尚未同时出现，则新建两人关系
                relationships[name1][name2]=1
            else:
                relationships[name1][name2]+=1 #两人共同出现次数加1

# 将已经建立好的names和relationships输出到文本，以便gephi可视化处理
# 假设共同出现次数少于3次的是冗余边，在输出时跳过
with codecs.open("busan_node.csv","w","utf8") as f:
    f.write("Id,Label,Weight\r\n")
    for name,times in names.items():
        f.write(name+","+name+","+str(times)+"\r\n")

with codecs.open("busan_edge.csv","w","utf8") as f:
    f.write("Source,Target,Weight\r\n")
    for name,edges in relationships.items():
        for v,w in edges.items():
            if w>3:
                f.write(name+","+v+","+str(w)+"\r\n")
