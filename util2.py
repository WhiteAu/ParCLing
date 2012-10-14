from parser import *
from math import *

def printChart(chart, sentence, widths=(10,10,10,10,10), printBackPointers=True, printProbs=True):
    #w = int(ceil(columnWidth / 3))
    N = len(sentence)
    
    (labelw,bpLw,bpRw,prec1,prec2) = widths
    
    columnWidth = labelw
    if printBackPointers: columnWidth += bpLw+bpRw
    if printProbs: columnWidth += prec1+prec2

    for i in range(N):
        print ('row%d'%i).ljust(columnWidth*(N+1), '_')
        for j in range(1,N+1):
            print ' '*columnWidth*(j-1)+'%d'%j
            for item in chart.iter_cell(i, j):
                print ' '*columnWidth*(j-1),
                print '%*s' % (-labelw, item.label),
                if printBackPointers:
                    print '%*s%*s' % (-bpLw, str(item.backPtrLeft), -bpRw, str(item.backPtrRight)),

                if printProbs:
                    print '%*.*f' % (prec1, prec2, item.logProb),

                print ''
