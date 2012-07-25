#!/usr/bin/evn python
# -*- coding: UTF8 -*-
#coding=UTF8
#
u"""
@author: Alexey "DataGreed" Strelkov
@site:  https://bitbucket.org/DataGreed/docstring-coverage
@email: datagreed<at>gmail.com

This is a simple audit tool to test python code docstring coverage.

Based on the original script from http://code.activestate.com/recipes/355731/ by James Harlow back in 2004 (James, I owe you a beer)
The code doesn't work on classes or functions that are eval'd into existence.
"""

#TODOs:
#показывать какой процент методов/классов покрыт докстрингами для отдельных модулей
#оценивать покрытие какой-то сбъективной оценкой (можно в будущем учитывать размеры докстрингов)
#добавить ворнинг, что докстринг малоиформативный, т.е. слишком уж короткий (например, символов 15 и меньше)
#добавить статистику по коротким докстрингам
#добавить опцию для рекурсивного поиска модулей в указанной директории [!]
#добавить разные уровни вербозности - можно выводить только общий процент покрытия по папке и оценку, или по каждому модулю
#  или также выводить какие докстринги именно пропущены
#  в совсем вербозном случае можно писать какие докстринги есть

import compiler

usage = '''python coverage.py <pythonsourcefile>

Prints a rundown of the classes, functions, and methods in the given module 
that have not been given a docstring.
'''

class DocStringCoverageVisitor(compiler.visitor.ASTVisitor):
    
    def __init__(self, filename):
        self.currentnode = []
        self.symbolcount = 0
        ast = compiler.parseFile(filename)
        compiler.walk(ast, self)
    
    def visitModule(self, module):
        self.symbolcount += 1
        node = (module.doc is not None and module.doc.strip() != '', [])
        self.currentnode.append(node)
        compiler.walk(module.node, self)
        self.result = self.currentnode.pop()
    
    def visitClass(self, clazz):
        self.symbolcount += 1
        isDoc = clazz.doc is not None and clazz.doc.strip() != ''
        node = (clazz.name, isDoc, [])
        self.currentnode[-1][-1].append(node)
        self.currentnode.append(node)
        compiler.walk(clazz.code, self)
        self.currentnode.pop()
    
    def visitFunction(self, func):
        self.symbolcount += 1
        isDoc = func.doc is not None and func.doc.strip() != ''
        node = (func.name, isDoc, [])
        self.currentnode[-1][-1].append(node)
        self.currentnode.append(node)
        compiler.walk(func.code, self)
        self.currentnode.pop()
    
    def getResult(self):
        return self.result

GRADES=(
    ("IMPOSSIBRUU!", 100),
    ("sweet!", 90),
    ("very good", 80),
    ("good", 65),    
    ("not so bad", 50),
    ("not so good", 35),
    ("very-very poor", 20),
    ("not documented at all", 2),
)

def main():
    import sys, os
    
    total_docs_needed = 0
    total_docs_covered = 0
    
    def printDocstring(base, node):
        
        docs_needed = 1
        docs_covered = 0
        
        name, isDoc, childNodes = node
        if isDoc == False:
            print 'No docstring for %s%s!' % (base, name)
        else:
            #можно выводить, что есть докстринг при максимальной вербозности
            docs_covered+=1
            
        for symbol in childNodes:
            temp_docs_needed, temp_docs_covered = printDocstring('%s.' % name, symbol)
            docs_needed+=temp_docs_needed
            docs_covered+=temp_docs_covered
            
        return docs_needed, docs_covered
    
    if len(sys.argv) != 2:
        print usage
        raise SystemExit
    module = DocStringCoverageVisitor(sys.argv[1]).getResult()
    if not module[0]:
        print "No module dostring!"
    for symbol in module[1]:
        temp_docs_needed, temp_docs_covered = printDocstring('', symbol)
        total_docs_needed+=temp_docs_needed
        total_docs_covered+=temp_docs_covered
    
    print "\nOverall statistics:"
    print "Docstrings needed: %s;" % total_docs_needed,
    print "Docstings exist: %s;" % total_docs_covered,
    print "Docstings missing: %s" % (total_docs_needed - total_docs_covered)
    percentage = total_docs_covered*100/total_docs_needed
    print "Total docstring coverage: %s%%; " % (percentage), 
    
    grade = ""
    
    for grade, value in GRADES:
        if value<= percentage:
            grade = grade
            break;
            
    print "Grade %s" % grade

if __name__ == '__main__':
    main()
