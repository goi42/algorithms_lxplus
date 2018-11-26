import sys
import copy
from cut import cut
from cbfch import cbfch
from bfch import bfch
from ROOT import TH1F, TH1, TH2F, TCut


class branch(bfch):
    def __init__(self, branch, name=None, nBins=0, loBin=0, hiBin=0, units=None, xlabel="", ylabel="", set_log_X=False, set_log_Y=False, can_extend=False, c=None, associated_branch=None, uniquenm=None):
        bfch.__init__(self, c=c)
        self.branch = branch  # name of branch as it appears in the tree
        self.name = branch  # nickname--usually what you want to appear on a plot
        if name:
            self.name = name
        self.nBins = nBins
        self.loBin = loBin
        self.hiBin = hiBin
        self.units = units
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.set_log_X = set_log_X  # do you want a log scale?
        self.set_log_Y = set_log_Y  # do you want a log scale?
        self.can_extend = can_extend  # do you want Draw to change the bin range?
        self.associated_branch = associated_branch if associated_branch is not None else None  # branch() object that this will be plotted against, as <thisbranch>:<associated branch>
        self.uniquenm = self.branch if uniquenm is None else uniquenm
        # self.legxi = 0.3
        # self.legxf = 0.6
        # self.legyi = 0.7
        # self.legyf = 0.9
        # self.legend = TLegend(self.legxi,self.legyi,self.legxf,self.legyf)
        self.h = None

    def set_binning(self, nBins, loBin, hiBin, can_extend=False):
        if nBins < 0:
            raise ValueError("branch {} cannot be assigned nBins = {}. nBins must be >=0!".format(repr(self.name), repr(nBins)))
        if loBin > hiBin:
            raise ValueError("branch {} cannot be assigned loBin = {} and hiBin = {} loBin must be <= hiBin!".format(repr(self.name), repr(loBin), repr(hiBin)))
        self.nBins = nBins
        self.loBin = loBin
        self.hiBin = hiBin
        self.can_extend = can_extend
        
    def get_bin_width(self):
        return (float(self.hiBin) - float(self.loBin)) / float(self.nBins)
    
    def make_histogram(self, hname=None, linecolor=None, fillcolor=None, fillstyle=None, overwrite=False, return_histogram=True):  # create an empty histogram
        if linecolor is None and self.linecolor is None:
            linecolor = 1
        elif linecolor is None:
            linecolor = self.linecolor
        if fillcolor is None:
            fillcolor = self.fillcolor
        if fillstyle is None:
            fillstyle = self.fillstyle
            
        if not hname:
            hname = 'h' + repr(cbfch.nh)
            cbfch.nh += 1
        if self.h and not overwrite:
            raise Exception('{} has h already'.format(self.name))
        elif overwrite:
            self.h = None
        assocbranch = self.associated_branch
        if not self.nBins:
            self.nBins = 100  # set default binning if not specified
        hilospec = False  # is either loBin or hiBin non-0?
        if self.loBin or self.hiBin:
            hilospec = True
        binning_set = all([self.nBins, hilospec])  # is the binning completely specified now?
        if assocbranch:  # repeat for assocbranch
            if not assocbranch.nBins:
                assocbranch.nBins = 100
            hilospec = False  # is either loBin or hiBin non-0?
            if assocbranch.loBin or assocbranch.hiBin:
                hilospec = True
            assocbinning_set = all([assocbranch.nBins, hilospec])
        if not assocbranch:
            h = TH1F(hname, self.name, self.nBins, self.loBin, self.hiBin)
            if(not binning_set or self.can_extend):
                h.SetCanExtend(TH1.kAllAxes)
            h.SetLineColor(linecolor)
            if fillcolor is not None:
                h.SetFillColor(fillcolor)
            if fillstyle is not None:
                h.SetFillStyle(fillstyle)
        else:
            h = TH2F(hname, self.name + ' vs. ' + assocbranch.name, self.nBins, self.loBin, self.hiBin, assocbranch.nBins, assocbranch.loBin, assocbranch.hiBin)
            if(not binning_set or self.can_extend):
                h.SetCanExtend(TH1.kXaxis)
            if(not assocbinning_set or assocbranch.can_extend):
                h.SetCanExtend(TH1.kYaxis)
            h.GetXaxis().SetTitle(self.branch)
            h.GetYaxis().SetTitle(assocbranch.branch)
        self.h = h
        if return_histogram:
            return h

    def _arithmetic(self, sym, another):
        newbranch = '(' + self.branch + ') ' + sym + ' (' + another.branch + ')'
        newname = '(' + self.name + ') ' + sym + ' (' + another.name + ')'
        if not(self.hiBin - self.loBin == 0 or another.hiBin - another.loBin):
            binning_rate = max(float(self.nBins) / (self.hiBin - self.loBin), float(another.nBins) / (another.hiBin - another.loBin))
        else:
            binning_rate = 0
        if all([self.xlabel, self.ylabel, another.xlabel, another.ylabel]):
            xlabel = self.xlabel + ' ' + sym + ' ' + another.xlabel
            ylabel = self.ylabel + ' ' + sym + ' ' + another.ylabel
        else:
            xlabel = None
            ylabel = None
        if self.set_log_X or another.set_log_X:
            set_log_X = True
        else:
            set_log_X = False
        if self.set_log_Y or another.set_log_Y:
            set_log_Y = True
        else:
            set_log_Y = False
        if self.can_extend or another.can_extend:
            can_extend = True
        else:
            can_extend = False
        c = list(set(self.c + another.c))
        if not (self.associated_branch and another.associated_branch):
            if self.associated_branch:
                associated_branch = self.associated_branch
            elif another.associated_branch:
                associated_branch = another.associated_branch
            else:
                associated_branch = None
        else:
            associated_branch = None
        return newbranch, newname, binning_rate, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch

    def __add__(self, another):
        newbranch, newname, binning_rate, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch = self._arithmetic('+', another)
        hiBin = self.hiBin + another.hiBin
        loBin = self.loBin + another.loBin
        nBins = int(round(binning_rate * (hiBin - loBin)))
        if nBins == 0:
            nBins = 100
        if self.associated_branch and another.associated_branch:
            associated_branch = self.associated_branch + another.associated_branch
        return branch(newbranch, newname, nBins, loBin, hiBin, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch)

    def __sub__(self, another):
        newbranch, newname, binning_rate, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch = self._arithmetic('-', another)
        # hiBin = self.hiBin - another.hiBin
        # loBin = self.loBin - another.loBin
        # nBins = int(round(binning_rate*(hiBin-loBin)))
        # if nBins == 0: nBins = 100
        hiBin = loBin = 0
        nBins = 100
        if self.associated_branch and another.associated_branch:
            associated_branch = self.associated_branch - another.associated_branch
        return branch(newbranch, newname, nBins, loBin, hiBin, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch)

    def __mul__(self, another):
        newbranch, newname, binning_rate, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch = self._arithmetic('*', another)
        if self.hiBin >= 0 and another.hiBin >= 0 and self.loBin >= 0 and another.loBin >= 0:
            hiBin = self.hiBin * another.hiBin
            loBin = self.loBin * another.loBin
            nBins = int(round(binning_rate * (hiBin - loBin)))
            if nBins == 0:
                nBins = 100
        else:
            hiBin = 0
            loBin = 0
            nBins = 100
        if self.associated_branch and another.associated_branch:
            associated_branch = self.associated_branch * another.associated_branch
        return branch(newbranch, newname, nBins, loBin, hiBin, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch)

    def __pow__(self, power):  # special case; does not call _arithmetic
        outbranch = copy.deepcopy(self)
        if power == 0.5:
            outbranch.branch = 'sqrt(' + self.branch + ')'
            outbranch.name = '#sqrt{' + self.name + '}'
            if self.xlabel:
                outbranch.xlabel = '#sqrt{' + self.xlabel + '}'
            if self.ylabel:
                outbranch.ylabel = '#sqrt{' + self.ylabel + '}'
        else:
            outbranch.branch = 'pow(' + self.branch + ',' + repr(power) + ')'
            outbranch.name = '(' + self.name + ')^{' + repr(power) + '}'
            if self.xlabel:
                outbranch.xlabel = '(' + self.xlabel + ')^{' + repr(power) + '}'
            if self.ylabel:
                outbranch.ylabel = '(' + self.ylabel + ')^{' + repr(power) + '}'
        if not(self.hiBin - self.loBin == 0):
            binning_rate = float(self.nBins) / (self.hiBin - self.loBin)
        else:
            binning_rate = 0
        outbranch.hiBin = self.hiBin ** power
        outbranch.loBin = self.loBin ** power
        outbranch.nBins = int(round(binning_rate * (outbranch.hiBin - outbranch.loBin)))
        if outbranch.nBins == 0:
            outbranch.nBins = 100
        return outbranch

    def __div__(self, another):
        newbranch, newname, binning_rate, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch = self._arithmetic('/', another)
        if self.hiBin >= 0 and another.hiBin > 0 and self.loBin >= 0 and another.loBin > 0:
            hiBin = self.hiBin / another.loBin
            loBin = self.loBin / another.hiBin
            nBins = int(round(binning_rate * (hiBin - loBin)))
            if nBins == 0:
                nBins = 100
        else:
            hiBin = 0
            loBin = 0
            nBins = 100
        if self.associated_branch and another.associated_branch:
            associated_branch = self.associated_branch * another.associated_branch
        return branch(newbranch, newname, nBins, loBin, hiBin, xlabel, ylabel, set_log_X, set_log_Y, can_extend, c, associated_branch)

    def __iadd__(self, another):
        return self + another
        
    def __isub__(self, another):
        return self - another
        
    def __imul__(self, another):
        return self * another
    
    def __ipow__(self, power):
        return self ** power
        
    def __idiv__(self, another):
        return self / another

    def __str__(self):
        return self.branch
