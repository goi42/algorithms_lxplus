class cbfch:  # abstract base class for cut, branch, and fch classes
    nh = 0  # number of created histograms to avoid duplicate names and memory leaks
    
    def __init__(self, linecolor=None, fillcolor=None, fillstyle=None, hname=None, neededbranchnames=None, evaltemp=None, needednames=None):
        self.linecolor = linecolor
        self.fillcolor = fillcolor
        self.fillstyle = fillstyle
        self.hname = hname
        self.h = None
        self.neededbranchnames = neededbranchnames  # what branch names is this composed of? only really useful for cut and branch
        self.evaltemp = evaltemp  # to be called like `eval(evaltemp.format(tree))`
        self.needednames = needednames  # things that must be defined in the environment for evaltemp to evaluate
