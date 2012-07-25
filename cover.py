#!/usr/bin/evn python
# -*- coding: UTF8 -*-
#coding=UTF8
#based on original script from http://code.activestate.com/recipes/355731/ by James Harlow back in 2004
#The code doesn't work on classes or functions that are eval'd into existence.
#
#
#TODOs:
#показывать какой процент методов/классов покрыт докстрингами
#оценивать покрытие какой-то сбъективной оценкой (можно в будущем учитывать размеры докстрингов)
#добавить ворнинг, что докстринг малоиформативный, т.е. слишком уж короткий (например, символов 15 и меньше)
#добавить опцию для рекурсивного поиска модулей в указанной директории [!]
#добавить разные уровни вербозности - можно выводить только общий процент покрытия по папке и оценку, или по каждому модулю
#  или также выводить какие докстринги именно пропущены

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

def main():
    import sys, os

    def printDocstring(base, node):
        name, isDoc, childNodes = node
        if isDoc == False:
            print 'No docstring for %s%s!' % (base, name)
        for symbol in childNodes:
            printDocstring('%s.' % name, symbol)
    
    if len(sys.argv) != 2:
        print usage
        raise SystemExit
    module = DocStringCoverageVisitor(sys.argv[1]).getResult()
    if not module[0]:
        print "No module dostring!"
    for symbol in module[1]:
        printDocstring('', symbol)
        

if __name__ == '__main__':
    main()
