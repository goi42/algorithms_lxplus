import sys
from branch import branch
from cut import cut
from bfch import bfch
from ROOT import TCanvas, TString


class fch(bfch):  # abstract base class for file and chain classes
    def __init__(self, linecolor=None, markercolor=None, fillcolor=None, fillstyle=None, hname=None):
        bfch.__init__(self, linecolor=linecolor, markercolor=markercolor, fillcolor=fillcolor, fillstyle=fillstyle, hname=hname)
        self.name = ""  # nickname for the file or chain
        self.quality = {}  # handy for comparing files, e.g., quality["year"]="2015"
        self.dframedict = None
        self._thething = None  # should be set to a TTree for file and the TChain for chain
        self._theotherthing = None  # should be set to the TFile for file and the TChain for chain
        self.b = []
        self.bMaxes = {}
        self.bMins  = {}
    # def __enter__(self):
    #     return self
    # def __exit__(self, exc_type, exc_value, traceback):
    #     self._thething.Delete()
    
    def set_name(self, name):
        self.name = name
    
    def set_quality(self, quality):
        self.quality = quality
    
    def make_dframedict(self, overwrite=False):
        'initializes dframedict if it does not exist (or `overwrite` specified)'
        if self.dframedict is None or overwrite:
            from ROOT import RDataFrame
            self.dframedict = {
                '': RDataFrame(self.GetTree())
            }
        
        return self.dframedict
    
    def add_filtered_dframe(self, c, overwrite=False):
        def get_title(c):
            'get the Title (or equivalent) of c'
            if isinstance(c, cut):
                ctit = c.cut.GetTitle()
            elif isinstance(c, str):
                ctit = c
            else:
                ctit = c.GetTitle()
            return ctit
        
        def get_uniquenm(c):
            'get the uniquenm (or equivalent) of c'
            if isinstance(c, cut):
                unm = c.uniquenm
            else:
                unm = get_title(c)
            return unm
        
        if isinstance(c, cut):
            if c.stackcut is None:
                dictkey = ''
            else:
                self.add_filtered_dframe(c.stackcut, overwrite=overwrite)
                dictkey = get_uniquenm(c.stackcut)
        else:
            dictkey = ''
        
        self.make_dframedict()
        
        unm = get_uniquenm(c)
        if overwrite or unm not in self.dframedict:
            self.dframedict[unm] = self.dframedict[dictkey].Filter(get_title(c))
        
        return self.dframedict[unm]
    
    def range_dframes(self, begin, end, stride=1):
        'all existing dframes are replaced by limited range versions of themselves'
        self.make_dframedict()
        for k, df in self.dframedict.iteritems():
            self.dframedict[k] = df.Range(begin, end, stride)
    
    def add_branch(self, *args, **kwargs):
        if all(isinstance(x, branch) for x in args):
            self.b += args
        else:
            self.b.append(branch(*args, **kwargs))
    
    def add_columns(self, *args):
        'adds branches as columns to all existing dframes if no arguments'
        'else, adds specified branches as columns without adding them to b'
        blist = args if args else self.b
        for b in blist:
            b.add_column(self)
    
    def file_1tree(self, fname):
        if self.__class__.__name__ == 'file':  # this check is only necessary for files, not chains
            if self.GetNtrees() == 1:  # class member declared in file class
                return True
            else:
                raise NotImplementedError("file.{} is only available for objects with only one tree.".format(fname))
        else:
            return True
        
    def file_uniquetrees(self):
        if self.__class__.__name__ == 'file':  # this check is only necessary for files, not chains
            if len(self.t) == len(set(self.t)):
                return True
            else:
                return False
    
    def chain_istree(self, tname):
        if self.__class__.__name__ == 'chain':  # this check is only necessary for chains, not files
            if tname == self._thething.GetName():
                return True
            else:
                return False
        else:
            return True
    
    def GetListOfBranches(self):
        assert self.file_1tree("GetListOfBranches")
        temp = []
        for nm in self._thething.GetListOfBranches():
            temp.append(nm.GetName())
        return temp
    
    def GetNbranches(self):
        assert self.file_1tree("GetNbranches")
        return self._thething.GetNbranches()
    
    def GetMaximum(self, brname):
        assert self.file_1tree("GetMaximum")
        return self._thething.GetMaximum(brname)
    
    def GetMinimum(self, brname):
        assert self.file_1tree("GetMinimum")
        return self._thething.GetMinimum(brname)
    
    def GetbMaxMin(self, brlist=[]):
        assert self.file_1tree("GetMaxMin")
        bloop = []
        if not isinstance(brlist, list):
            raise TypeError("GetbMaxMin takes a _list_, not a " + brlist.__class__.__name__)
        if brlist:
            bloop = brlist
        elif self.b:
            for ib in self.b:
                bloop.append(ib.branch)
        else:
            bloop = self.GetListOfBranches()
        for bname in bloop:
            self.bMaxes[bname] = self.GetMaximum(bname)
            self.bMins[bname] = self.GetMinimum(bname)
    
    def GetEntries(self, selection=''):
        if isinstance(selection, str):
            p = selection
        elif isinstance(selection, cut):
            p = selection.cut.GetTitle()
        elif isinstance(selection, TCut):
            p = selection.GetTitle()
        else:
            raise TypeError('GetEntries requires a str, cut, or TCut, not a ' + selection.__class__.__name__)
        return self._thething.GetEntries(p)
    
    def GetTree(self, trname=None):
        '''gets tree or chain as appropriate
        '''
        if not trname:
            assert self.file_1tree('GetTree')
            return self._thething
        else:
            if self.__class__.__name__ == 'chain':
                assert self.chain_istree(trname)
                return self._thething
            elif self.__class__.__name__ == 'file':
                assert self.file_uniquetrees()
                for tr in self.t:
                    if tr.GetName() == trname:
                        return tr
    
    def Draw(self, thisbranch, thiscut="", opt="", nentries=None, firstentry=0, canvas=None, treename=None):
        if isinstance(thiscut, cut):
            tempcut = thiscut if thiscut.weight is None else thiscut * thiscut.weight if isinstance(thiscut.weight, cut) else thiscut * cut(thiscut.weight)
            acut = tempcut.cut
        else:
            acut = thiscut
        if nentries is None:
            nentries = self._thething.kMaxEntries
        if canvas is None:  # make canvas
            canvas = TCanvas(self.name, self.name, 1200, 800)
        if not isinstance(canvas, TCanvas):
            raise TypeError('canvas must be TCanvas or None')
        canvas.cd()
        
        if isinstance(thisbranch, str) or isinstance(thisbranch, TString):  # if a string is passed
            return self.GetTree(treename).Draw(thisbranch, acut, opt, nentries, firstentry)
        elif isinstance(thisbranch, branch):  # if a branch object is passed
            if not thisbranch.h:  # make histogram
                thisbranch.make_histogram()
            thisbranch.h.Reset()
            h = thisbranch.h
            hname = h.GetName()
            assocbranch = thisbranch.associated_branch
            # draw histograms
            if not assocbranch:
                # if any branches have these options set, draw them that way:
                if(thisbranch.set_log_X):
                    canvas.SetLogx()
                if(thisbranch.set_log_Y):
                    canvas.SetLogy()
                StringToDraw = "{}>>{}".format(thisbranch.branch, hname)
            else:
                StringToDraw = "{}:{}>>{}".format(assocbranch.branch, thisbranch.branch, hname)
                if(thisbranch.set_log_X):
                    canvas.SetLogx()
                if(assocbranch.set_log_X):
                    canvas.SetLogy()
                if(thisbranch.set_log_Y or assocbranch.set_log_Y):
                    canvas.SetLogz()
            # try:
            self.Draw(StringToDraw, acut, opt, nentries, firstentry, canvas, treename)
            # except:
            #     print "Draw() failed for "+placeholder
            #     print "in file: "+self.name
            #     if ctypepassed == 'cut': placeholder2 = thiscut.name
            #     else: placeholder2 = thiscut
            #     print "with cut: "+placeholder2
            #     print "Attempting to draw again with extendable axes..."
            #     h.SetCanExtend(TH1.kAllAxes)
            #     thisfile.Draw(placeholder,acut,drawopt)#one tree per file
        else:
            raise TypeError('cannot draw object of type {}'.format(type(thisbranch)))
    
    def EntryPasses(self, anentry, acut, abranch=None, **kwargs):
        if abranch is None:
            abranch = self.GetListOfBranches()[0]
        return self.Draw(abranch, acut, 'goff', nentries=1, firstentry=anentry, **kwargs)
    
    def __getattr__(self, name):
        try:
            return getattr(self._thething, name)
        except AttributeError:
            return getattr(self._theotherthing, name)
