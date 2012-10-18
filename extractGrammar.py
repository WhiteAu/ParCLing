from tree import *
from util import *
from grammar import *
from parser import *

def binarizeTree(tree, horizSize=None, verticSize=1, runFancyCode=False):
    def binarizeTree_rec(t, pN):
        # just return pre-terminals
        if t.height() <= 2: return t
        
        # otherwise we're an internal node
        # our label MUST be of the form "label^ANNOTATION" if you want to add annotation
        myLabel = t.node

        if runFancyCode:     # this is for the competition
            ### TODO: YOUR CODE HERE
            util.raiseNotDefined()
            

        if verticSize > 1:   # your code for parent annotation!
            pass 



        # if we're already binary or unary, life is good
        if len(t) <= 2:
            newChildren = []
            for i,child in enumerate(t):
                newChildren.append(binarizeTree_rec(child, pN))
            return Tree(myLabel, newChildren)

        # else, we need to binarize.  we'll assume the LAST child is the head

        # grab all children except the last one
        newLeftChildren = t[0:-1]
        
        # make a label that consists of their node labels; the initial
        # "_" signals that this is the result of binarization, so that
        # debinarize can find it
        newLeftChildLabels = [ child.node for child in newLeftChildren ]
        newLeftChildLabel  = '_' + '_'.join(newLeftChildLabels)
        
        # make them into a tree and binarize it
        newLeftChild = binarizeTree_rec( Tree(newLeftChildLabel, newLeftChildren), pN )

        # binarize the right child        
        newRightChild = binarizeTree_rec(t[-1], pN)     # last child

        if horizSize is not None:   # None means "infinity" -- this is your code for
                if((len(newLeftChildren)) > horizSize):
                    newLeftChildren = t[0:horizSize-1]
                #else:
                    #Grab all children except last one
                    #newLeftChildren = t[0:-1]
                newLeftChildLabels = [ child.node for child in newLeftChildren ]
                newLeftChildLabel  = '_' + '_'.join(newLeftChildLabels)
                # make them into a tree and binarize it
                newLeftChild = binarizeTree_rec( Tree(newLeftChildLabel, newLeftChildren), pN )
        
                # binarize the right child
                newRightChild = binarizeTree_rec(t[-1], pN)
    
        # return the tree
        return Tree(myLabel, [newLeftChild, newRightChild])

    if tree is None: return None
    if verticSize > 1:
        tree = _v_rec(tree, [], verticSize)
    return binarizeTree_rec(tree, [])

    
def debinarizeTree(tree):
    def removeAnnotations(s):
        if type(s) is not str: return s
        j = s.find('^')
        if j == -1:
            return s
        return s[0:j]
    
    def debinarizeTree_rec(t):
        # just return pre-terminals
        if type(t) is str:  return removeAnnotations(t)
        if t.height() <= 2:
            t.node = removeAnnotations(t.node)
            return t
        
        # if this is a unary node, life is good
        if len(t) == 1:
            return Tree(removeAnnotations(t.node), [debinarizeTree_rec(t[0])])
        
        # this might have been the result of binarization.  for BOTH children,
        # if their node name STARTS WITH "_" then they are binarized
        children = []
        for i in range(len(t)):
            children.append(t[i])
        
        while True:
            newChildren = []
            for i in range(len(children)):
                if type(children[i]) is str:
                    newChildren.append(children[i])
                elif children[i].node.startswith('_'):
                    for j in range(len(children[i])):
                        newChildren.append(children[i][j])
                else:
                    newChildren.append(children[i])
            if len(newChildren) == len(children): # nothing changed
                break
            children = newChildren
        
        # de-binarize all the children
        for i in range(len(children)):
            children[i] = debinarizeTree_rec(children[i])
        
        return Tree(removeAnnotations(t.node), children)
    
    if tree is None: return None
    return debinarizeTree_rec(tree)

        
def de_annotate(tree):
    if type(tree) is str:
        if len(tree) == 0: return None
        if tree == '-NONE-': return None
        return tree.split('-')[0]

    if len(tree.node) == 0: return None
    if tree.node == '-NONE-': return None
    children = []
    for i,child in enumerate(tree):
        newChild = de_annotate(child)
        if newChild is not None:
            children.append(newChild)
    if len(children) == 0:
        return None
    return Tree(tree.node.split('-')[0], children)

def iterateTreebank(filename, horizSize=None, verticSize=1, runFancyCode=False):
    h = open(filename, 'r')
    for line in h:
        tree = de_annotate(bracket_parse(line))
        if tree is None: continue

        # TEMPORARY:
        #print "Tree before binarization:"
        #print tree.pp()
        tree = binarizeTree(tree, horizSize, verticSize, runFancyCode)
        #print "Tree after binarization:"
        #print tree.pp()

        yield tree
    h.close()

def iterateTaggedSentences(filename):
    sents = []
    h = open(filename, 'r')
    for line in h:
        wts = line.strip().split()
        words = []
        tags  = []
        for wt in wts:
            wt_list = wt.split('_')
            words.append(wt_list[0])
            tags.append('_'.join(wt_list[1:]))
        yield (words, tags)

def computePCFG(filename, horizSize=None, verticSize=1):
    pcfg = PCFG({})
    
    # iterate over all the trees in the treebank
    for tree in iterateTreebank(filename, horizSize=horizSize, verticSize=verticSize):
        # iterate over all its subtrees
        for subtree in tree.subtrees():
            # make sure it's NOT a pre-terminal -- yes, you could do this in subtrees() too!
            if subtree.height() <= 2:   # 1 is leaf, 2 is pre-terminal
                continue

            # get the rule LHS -> RHS
            lhs = subtree.node
            rhs = None
            if len(subtree) == 1:   # it's a unary rule
                rhs =RHS(subtree[0].node)
            elif len(subtree) == 2: # it's a binary rule
                rhs = RHS(subtree[0].node, subtree[1].node)
            else:
                raise Exception("tree must be binarized!")

            pcfg.increase_rule_count( Rule(lhs, rhs) )

    return pcfg
def _v_rec(t, pN, verticSize):
    #if len(t) <= 2:
    #    return t
    #print t.node
    pN.insert(0, t.node)
    if (len(pN) >= verticSize):
        #print pN
        pN.pop()
        #print 'popping'
        #print pN
    
    for child in t:
        #pN.append(child.node)
        if child.height() > 2:
            newNode = child.node+'^'+'^'.join(pN)
            #print pN
            pNcopy = list(pN)
            #print child.node
            child = _v_rec(child, pNcopy, verticSize)
            child.node = newNode    
        #apply to the tree structure
    return t
        


nonBinaryTree = Tree("TOP", [Tree("S", [Tree("NP", [Tree("DT" , ["the"]),
                                                    Tree("RB" , ["really"]),
                                                    Tree("JJ" , ["happy"]),
                                                    Tree("NN" , ["computer"]),
                                                    Tree("NN" , ["science"]),
                                                    Tree("NN" , ["student"])]),
                                        Tree("VP", [Tree("VBD", ["loves"]),
                                                    Tree("NP" , [Tree("NNP", ["CL1"])])]),
                                        Tree(".", ["."])])])

if __name__ == '__main__':
    w = 80
    #print "compute PCFG on wsj.dev".center(w,'_')
    #pcfg = computePCFG('wsj.dev')
    #print len(pcfg)
    #print str(pcfg)

    #print "compute PCFG on wsj.train".center(w,'_')
    #pcfg = computePCFG('wsj.train')
    #print len(pcfg)
    #print parse(pcfg, ['NN', 'VBZ', 'IN', 'DT', 'NN'])
    #print parse(pcfg, ['VBZ', 'NN', 'IN', 'DT', 'NN'])
    #print nonBinaryTree
    #print binarizeTree(nonBinaryTree)
    '''
    print "Tree before binarization:"
    tree = nonBinaryTree
    print tree.pp()
    tree = binarizeTree(tree, horizSize=None, verticSize=2)
    print "Tree after binarization:"
    print tree.pp()
    '''
    #print debinarizeTree(binarizeTree(nonBinaryTree))
    #evaluateParser(pcfg, 'wsj.dev')
    #evaluateParser(pcfg, 'wsj.dev', pruningPercent=0.00001)
    #evaluateParser(pcfg, 'wsj.dev', pruningPercent=0.001)
    #evaluateParser(pcfg, 'wsj.dev', pruningPercent=0.1)
    #pcfg = computePCFG('wsj.train', horizSize=2)
    #print evaluateParser(pcfg, 'wsj.dev', pruningPercent=0.00001, horizSize=2)
    # THIS IS NOT WORKING!
    pcfg = computePCFG('wsj.train', verticSize=2)
    print evaluateParser(pcfg, 'wsj.dev', pruningPercent=0.00001, verticSize=2)

    #runParserOnTest(pcfg, 'wsj.test', 'wsj.test.out', pruningPercent=0.001)
    
    
