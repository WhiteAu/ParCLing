from parser import *
from math import *

def printChart(chart, sentence, columnWidth=40, printBackPointers=True):
    w = int(ceil(columnWidth / 3))
    N = len(sentence)
    for i in range(N):
        print ('row%d'%i).ljust(columnWidth*(N+1), '_')
        for j in range(1,N+1):
            print ' '*columnWidth*j+'%d'%j
            for item in chart.iter_cell(i, j):
                if printBackPointers:
                    print ' '*columnWidth*j + '%*s%*s%*s' % (-w, item.label, -w, str(item.backPtrLeft), -w, str(item.backPtrRight))
                else:
                    print ' '*columnWidth*j + '%*s' % (-w, item.label)
