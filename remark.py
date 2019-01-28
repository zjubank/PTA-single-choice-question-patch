# -*- coding: utf-8 -*-

import os
import os.path
import fileinput


def main():
    print("Input root directory: ")
    # 遍历路径
    rootdir = str(input())
    print("Input problem file name with path: ")
    # 完整文件名
    problempath = str(input())

    problemlist = getproblem(problempath)
    print(problemlist)
    comparefile(problemlist, rootdir)

    print("Done!")


def getproblem(problempath):
    cnt = 0
    problemlist = list()
    problemnum = ""
    problemtype = ""
    problemstr = ""
    problemanswer = ""
    problemanswertodo = ""
    
    for line in fileinput.input(problempath):
        # 题号
        if(cnt % 5 == 0): 
            problemnum = line
            
        # 类型
        # C:选择
        # B:填空
        # 数字:关键字到答案所在行的差值
        elif (cnt % 5 == 1):
            problemtype = line
        # 题干关键词
        elif(cnt % 5 == 2):
            problemstr = line
        # 标准答案
        elif(cnt % 5 == 3):
            problemanswer = line
        # 手动判定答案
        elif(cnt % 5 == 4):
            problemanswertodo = line
            # 读到这里说明读完了一道题目，然后加入列表
            problemlist.append([problemnum[:-1], problemtype[:-1], problemstr[:-1], problemanswer[:-1], problemanswertodo[:-1]]) # win去回车
            
        cnt += 1
        
    return problemlist
    


def comparefile(problemlist, rootdir):
    readdir(rootdir, problemlist)
    
    
def readdir(rootdir, problemlist):
    stulist = list()
    stuid = ""
    stuname = ""

    # 按题目分，每个题目去遍历一次所有文件
    for problem in problemlist:
               
        # 获取给定目录下所有文件名
        for path, dirnames, filenames in os.walk(rootdir):
            '''
            for dirname in dirnames:
                print("path: " + path)
                print("dirname: " + dirname)
            '''
            # 对每一个文件进行打开
            for filename in filenames:
                # 通过文件名获取学号和姓名
                stuid = str(filename)[:str(filename).find('-')]
                stuname = str(filename)[str(filename).find('-')+1:str(filename).find('.')]
                # 题号
                stuproblemid = problem[0]
                # 题目关键词
                stuproblem = problem[2]
                # 学生答案
                stuanswer = ""
                # 题目类型
                problemtype = problem[1]
                problemanswer = problem[3]
                problemanswertodo = problem[4]
                # 关键词行到答案行的偏移量
                problemdelta = int(problemtype[1:])

                # 对打开的文件开始逐行读文件
                if(filename.find('html')!=-1): # 只要html的偷懒写法
                    print("processing problem: "+ problem[0])
                    print("processing file: " + os.path.join(path,filename))

                    try:
                        file = open(os.path.join(path,filename),'r', encoding='UTF-8') # PTA导出的html是GBK编码
                        lines = file.readlines()
                        
                        linecnt = 0
                        deltacnt = 0
                        lineflag = False
                        for line in lines:
                            linecnt += 1

                            
                            # 本次循环中找到了关键词
                            if(line.find(problem[2])>=0):
                                print("found in line " + str(linecnt))
                                lineflag = True
                            # 循环中已经找到了关键词
                            if(lineflag == True):
                                # 判断delta
                                if(deltacnt == problemdelta):
                                    # 对于选择题，找checked
                                    if(problem[1].find("C")>=0):
                                        checkpos = line.find("checked=")
                                        # 录入学生答案
                                        if(checkpos>=0):
                                            leftpos = line.find(">",checkpos)
                                            rightpos = line.find("<",checkpos)
                                            stuanswer = line[leftpos+1:rightpos].strip()
                                        else: # 考生该题未作答
                                            stuanswer = "-"
                                    elif(problem[1].find("B")>=0):
                                        valuepos = line.find("value=")
                                        if(valuepos>=0):
                                            leftpos = line.find("\"",valuepos)
                                            rightpos = line.find("\"",leftpos+1)
                                            stuanswer = line[leftpos+1:rightpos].strip()
                                        else:
                                            stuanswer = "-"
                                            
                                    print("answer: " + stuanswer)
                                    
                                    # 该考生该题检查完毕，跳出内层循环
                                    deltacnt = 0
                                    lineflag = False
                                    break
                                else:
                                    #再往下找一行
                                    deltacnt += 1
                    finally:
                        # csv转义
                        if(stuproblem.find(",")>=0):
                            stuproblem = "\""+str(stuproblem)+"\""
                        if(stuanswer.find(",")>=0):
                            stuanswer = "\""+str(stuanswer)+"\""
                        if(problemanswer.find(",")>=0):
                            problemanswer = "\""+str(problemanswer)+"\""
                        if(problemanswertodo.find(",")>=0):
                            problemanswertodo = "\""+str(problemanswertodo)+"\""
                        # 如果学生试卷中出现了此题则写入列表
                        if(len(stuanswer)>0):
                             stulist.append([stuid,stuname,stuproblemid,stuproblem,stuanswer,problemanswer,problemanswertodo])
                        # 关闭文件
                        file.close()

        # 输出这一题的结果
        writeresult(rootdir, stulist)
        # 清空list
        stulist.clear()
    return 

def writeresult(rootdir,stulist):
    stutmp = stulist[0]
    answernum = stutmp[2]
    
    resultpath = rootdir+"\\"+str(answernum)+".csv" # win路径分隔符
    result = open(resultpath, 'w')

    orianswernum = 0
    blankanswernum = 0
    todoanswernum = 0
    todostu = list()
    
    result.writelines("学号,姓名,题号,题目关键词,学生选择结果,当前标准答案,需要调整答案\n")
    for stu in stulist:
        result.writelines(",".join(stu))
        result.write("\n")
        if(stu[4]==stu[5]):
            orianswernum += 1
        if(stu[4]=="-"):
            blankanswernum += 1
        if(stu[4]==stu[6]):
            todoanswernum += 1
            todostu.append([stu[0],stu[1]])
            
    result.writelines("\n共有 "+str(orianswernum)+" 位学生和原始答案一样\n共有 "+str(blankanswernum)+" 位学生此题没有填写\n共有 "+str(todoanswernum)+" 位学生该题需要加分。\n")    
    result.writelines("加分学生列表为:\n")
    for stu in todostu:
        result.writelines(",".join(stu))
        result.write("\n")

    result.close()


if __name__ == "__main__":
    main()
