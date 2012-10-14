from tree import *
from util import *

class RHS:
    def __init__(self, rhs1, rhs2=None):
        self.rhs1 = rhs1
        if rhs2 is None:
            self.isUnary = True
        else:
            self.isUnary = False
            self.rhs2 = rhs2

    def __str__(self):
        if self.isUnary:
            return self.rhs1
        else:
            return self.rhs1 + " " + self.rhs2

    def __repr__(self):
        return "'" + str(self) + "'"

    def __eq__(self, other):
        if self.isUnary != other.isUnary: return False
        if self.rhs1 != other.rhs1: return False
        if self.isUnary: return True
        if self.rhs2 != other.rhs2: return False
        return True

    def __hash__(self):
        if self.isUnary:
            return hash( (True, self.rhs1) )
        return hash( (False, self.rhs1, self.rhs2) )

class Rule:
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
        self.isUnary = rhs.isUnary

    def __str__(self):
        return self.lhs + " => " + str(self.rhs)

    def __repr__(self):
        return "'" + str(self) + "'"

    def __eq__(self, other):
        if self.lhs != other.lhs: return False
        return eq(self.rhs, other.rhs)

    def __hash__(self):
        return hash( (self.lhs, self.rhs) )

class PCFG:
    def __init__(self, pcfgC={}):
        self.pcfgC = pcfgC  # the raw cfg itself, pcfgC[lhs][rhs] = Count(lhs -> rhs)
        self.pcfg  = None   # the normalized version of pcfgC, pcfg[lhs][rhs] = p(rhs | lhs)
        self.pcfgR = None   # a "rotated" version of pcfg, pcfgR[rhs1][rhs2][lhs] = p(rhs1 rhs2 | lhs), where rhs2 is None for unary rules

    def __str__(self):
        rules = []
        for lhs in self.pcfgC.iterkeys():
            for rhs,count in self.pcfgC[lhs].iteritems():
                rules.append(str(Rule(lhs, rhs)) + '\t| ' + str(count) + '\n')
        return ''.join(rules)

    def __len__(self):   # number of unique rules
        count = 0
        for lhs in self.pcfgC.iterkeys():
            count += len(self.pcfgC[lhs])
        return count

    def increase_rule_count(self, rule):
        self.pcfg  = None
        self.pcfgR = None
        
        if not self.pcfgC.has_key(rule.lhs):
            self.pcfgC[rule.lhs] = Counter()
            
        self.pcfgC[rule.lhs][rule.rhs] += 1

    def normalize(self):
        self.pcfg = {}
        for lhs in self.pcfgC.iterkeys():
            # first, copy the elements
            self.pcfg[lhs] = Counter()
            for rhs,c in self.pcfgC[lhs].iteritems():
                self.pcfg[lhs][rhs] = c
            # now normalize
            self.pcfg[lhs].normalize()
        # since pcfg has changed, pcfgR should be reset to None
        self.pcfgR = None

    def rotate(self):
        if self.pcfg is None:
            self.normalize()

        self.pcfgR = {}
        for lhs in self.pcfg.iterkeys():
            for rhs,prob in self.pcfg[lhs].iteritems():
                rhs1 = rhs.rhs1
                rhs2 = None
                if not rhs.isUnary:
                    rhs2 = rhs.rhs2

                # we have a rule of the form "lhs -> rhs1 rhs2"
                # so set probability of lhs in [rhs1][rhs2] to prob
                    
                if not self.pcfgR.has_key(rhs1):
                    self.pcfgR[rhs1] = {}
                    
                if not self.pcfgR[rhs1].has_key(rhs2):
                    self.pcfgR[rhs1][rhs2] = {}
                    
                self.pcfgR[rhs1][rhs2][lhs] = prob

    def iter_binary_rules_on_rhs(self, rhs1, rhs2):
        if self.pcfgR is None:
            self.rotate()

        if not self.pcfgR.has_key(rhs1):
            return

        if not self.pcfgR[rhs1].has_key(rhs2):
            return

        for lhs,ruleLogProb in self.pcfgR[rhs1][rhs2].iteritems():
            yield (lhs, ruleLogProb)

    def iter_unary_rules_on_rhs(self, rhs):
        for lhs,ruleLogProb in self.iter_binary_rules_on_rhs(rhs, None):
            yield (lhs, ruleLogProb)


timeFliesPCFG = PCFG({
    "TOP"  : { RHS("S")            : 1.0 },
    "S"    : { RHS("NP", "VP")     : 0.5,
               RHS("VP")           : 0.2,
               RHS("NP", "VP_PP")  : 0.2,
               RHS("VP", "PP")     : 0.1 },
    "VP_PP": { RHS("VP", "PP")     : 1.0 },
    "NP"   : { RHS("Det", "Noun")  : 0.7,
               RHS("Noun")         : 0.3 },
    "VP"   : { RHS("Verb", "NP")   : 0.6,
               RHS("Verb", "PP")   : 0.2,
               RHS("Verb", "NP_PP"): 0.1,
               RHS("Verb")         : 0.1 },
    "NP_PP": { RHS("NP", "PP")     : 1.0 },
    "PP"   : { RHS("Prep", "NP")   : 1.0 },
    "Det"  : { RHS("an")    : 1.0 },
    "Noun" : { RHS("time")  : 0.2,
               RHS("flies") : 0.4,
               RHS("arrow") : 0.4 },
    "Verb" : { RHS("time")  : 0.3,
               RHS("flies") : 0.5,
               RHS("like")  : 0.2 },
    "Prep" : { RHS("like")  : 1.0 }
    })
timeFliesSent = "time flies like an arrow".split()

desiredTimeFliesParse = Tree("TOP", [Tree("S", [Tree("VP", [Tree("Verb", ["time"]),
                                                            Tree("NP", [Tree("Noun", ["flies"])]),
                                                            Tree("PP", [Tree("Prep", ["like"]),
                                                                        Tree("NP", [Tree("Det", ["an"]),
                                                                                    Tree("Noun", ["arrow"])])])])])])

