#!/usr/bin/evn python
# -*- coding: UTF8 -*-
#coding=UTF8
#
u"""
@author: Alexey "DataGreed" Strelkov
@site:  https://bitbucket.org/DataGreed/docstring-coverage
@email: datagreed<at>gmail.com

This is a simple audit tool to test python code docstring coverage.

Based on the original script from http://code.activestate.com/recipes/355731/ 
created by James Harlow back in 2004 (James, I owe you a beer)

The code doesn't work on classes or functions that are eval'd into existence.
"""

#TODOs:
#оценивать покрытие какой-то субъективной оценкой с учетом длины докстрингов
#добавить ворнинг, что докстринг малоиформативный, т.е. слишком уж короткий (например, символов 15 и меньше)
#добавить статистику по коротким докстрингам и вообще по их длине
#добавить разные уровни вербозности - можно выводить только общий процент покрытия по папке и оценку, или по каждому модулю
#  или также выводить какие докстринги именно пропущены
#  в совсем вербозном случае можно писать какие докстринги есть
#сделать опцию, позволяющую пропускать все магические методы, типа __init__, __str__, __unicode__ и т.п.
#сделать readme
# пропускать пустые __init__.py или вообще все пустые файлы? Под пустыми понимаются те, в которых нет вообще ничего - т.е. и переменных тоже
# опция поддержки симлинков для os.walk? Добавляется легко, но нужна ли?
# вынести парсинг опций за пределы main()!! должно быть в блоке проверки __name__=="__main__" или сделать отдельную функцию main
# можно переименовать main во что-то более удобное для внешнего использования и сделать чтобы он возвращал статистику в каком-то формате
#  внутренем, например в виже кортежа с путями к файлам и статистикой по ним в числовом виде - тогда можно будет во внешних модулях
# это все использовать

import compiler

usage = '''python coverage.py [options] <pythonsourcefile or directory>

Prints a rundown of the classes, functions, and methods in the given module 
that have not been given a docstring. 

Shows statistics on docstring coverage.
'''

__version__ = "0.2"

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
    ("sweet!!", 92),
    ("excelent", 85),
    ("very good", 70),
    ("good", 60),    
    ("not so bad", 40),
    ("not so good", 25),
    ("very-very poor", 10),
    ("not documented at all", 2),
)

def get_docstring_coverage(filenames, count_magic=True, skip_empty_files = True, verbose_level=0):
    '''
    Runs through files in filenames list and seeks classes and methods
    for missing docstrings. 
    Returns a report in a dictionary. Can also print the report if 
    verbose_level is set to 1-3

    @param filenames: a list of string containing filenames with
                      absolute or relative paths
    @param count_magic: a bool. If False, skips all __magic__
                        methods and does not include them in the report
    @param skip_emtpty_files: a bool, if True, skips all empty files,
                              still includes them in the report, but
                              doesn't require a module docstring for them
    @param verbose_level: an int, possible vallues 0..3:
                          0 - does not print anything
                          1 - prints only total stats
                          2 - prints stats for every file
                          3 - prints missing docstrings for every file
    @rtype: list
    @returns: returns a list of the following format:
             [
                 {'<filename>': 
                                {
                                    'missing': ["<method_or_class_name","..."],                                    
                                    'module_doc': <True or False>,  #has module docstring 
                                    'missing_count': <missing_count>,
                                    'needed_count': <needed_docstrings_count>,
                                    'coverage': <percent_of_coverage>,                                
                                },
                    ...
                  },
                  
                  #totals
                  {
                      'missing_count': <total_missing_count>,
                      'needed_count': <total_needed_docstrings_count>,
                      'coverage': <total_percent_of_coverage>,                                
                  },
                  
             ]
                  
    '''
    verbose_level = int(verbose_level)
    
    def log(text, level=1, append=False):
        u"""Prints to log depending on verbosity level"""
        if verbose_level>= level:
            if append: print text,
            else: print text
            
    def printDocstring(base, node):
        
        missing_list = []
        
        docs_needed = 1
        docs_covered = 0
        
        name, isDoc, childNodes = node
        if isDoc == False:
            print ' - No docstring for %s%s!' % (base, name)
            missing_list.append(base+name)
        else:
            #можно выводить, что есть докстринг при максимальной вербозности
            docs_covered+=1
            
        for symbol in childNodes:
            temp_docs_needed, temp_docs_covered, temp_missing_list = printDocstring('%s.' % name, symbol)
            docs_needed+=temp_docs_needed
            docs_covered+=temp_docs_covered
            missing_list += temp_missing_list
            
        return docs_needed, docs_covered, missing_list
    
    
    #handle docstrings
    total_docs_needed = 0       #for statistics
    total_docs_covered = 0      #
    
    result_dict = {}        #a dictionary with file statisics
    
    for filename in filenames:
        
        print "\nFile %s" % filename
        
        file_docs_needed = 1    #module docstring
        file_docs_covered = 1  #we assume we have module docstring
        file_missing_list = []  #list of all symbos missing docstrings in file
        
        module = DocStringCoverageVisitor(filename).getResult()
        
        if not module[0]:
            print " - No module dostring!"
            file_docs_covered-=1    
        
        #traverse through functions and classes    
        for symbol in module[1]:
            temp_docs_needed, temp_docs_covered, missing_list = printDocstring('', symbol)
            
            file_docs_needed+=temp_docs_needed
            file_docs_covered+=temp_docs_covered
            file_missing_list+=missing_list
            
        total_docs_needed+=file_docs_needed
        total_docs_covered+=file_docs_covered    
        
        result_dict[filename] = { 
                                'missing': file_missing_list,                                    
                                'module_doc': bool(module[0]),
                                'missing_count': file_docs_needed-file_docs_covered,
                                'needed_count': file_docs_needed,
                                'coverage': float(file_docs_covered)*100/float(file_docs_needed)
                                }
                                
        print " Needed: %s; Exist: %s; Missing: %s; Coverage: %.1f%%" % (file_docs_needed, file_docs_covered,
                                                                    result_dict[filename]['missing_count'],
                                                                    result_dict[filename]['coverage'])
    
    total_result_dict = {
                        'missing_count': total_docs_needed - total_docs_covered,                                
                        'needed_count': total_docs_needed,
                        'coverage': float(total_docs_covered)*100/float(total_docs_needed),
    }
    
    postfix=""
    if(not count_magic): postfix=" (all magic methods omited!)"    
    
    if len(filenames)>1:
        print "\nOverall statistics for %s files%s:" % (len(filenames), postfix)
    else:
        print "\nOverall statistics%s:" % postfix
        
    print "Docstrings needed: %s;" % total_docs_needed,
    print "Docstings exist: %s;" % total_docs_covered,
    print "Docstings missing: %s" % (total_result_dict['missing_count'])
    print "Total docstring coverage: %.1f%%; " % (total_result_dict['coverage']), 
    
    grade = ""
    for grade, value in GRADES:
        if value<= total_result_dict['coverage']:
            grade = grade
            break;
            
    print "Grade: %s" % grade
    
    return result_dict, total_result_dict

if __name__ == '__main__':
    
    import sys, os
    from optparse import OptionParser
    
    #creating options
    parser = OptionParser(usage = usage, version="%prog " + __version__)
    parser.add_option("-v", "--verbose", dest="verbosity", default="2",metavar="LEVEL",
                      help="verbose level <0-3>",type="choice", choices = ['0','1','2','3'])
    parser.add_option("-m", "--nomagic",
                      action="store_false", dest="magic", default=True,
                      help="don't count docstrings for __magic__ methods")
    #parsing options
    (options, args) = parser.parse_args()
    
    #handle invalid args
    if len(args) !=1:
        print usage
        sys.exit()
    
    #a list of filenames to be checked for docstrings
    filenames = []
        
    if 'py' in args[0]:
        #one module
        filenames = [args[0]]
    else:
        #supposedely directory name supplied, traverse through it
        #to find all py-files
        for root, dirs, fnames in os.walk(args[0]):
            for fname in fnames:
                if fname.endswith('.py'):
                    sep = os.sep
                    if(root.endswith(os.sep)): sep=""   #root can be "./", we should not use separator then
                    filenames.append(root + sep + fname)
    
    if(len(filenames)<1):
        sys.exit('No python files found')
    
    if(not options.magic):
        raise NotImplementedError("Omitting magic methods not supported yet")
    
    get_docstring_coverage(filenames, options.magic, verbose_level = options.verbosity)
