import sys
from branch import *
from cut import *

class fch: #abstract base class for file and chain classes
    def __init__(self):
        self.name="" #nickname for the file or chain
        self.quality = {} #handy for comparing files, e.g., quality["year"]="2015"
        self.t=[]
        self.tname=[]
        self.b=[]
        self.c=[]#cuts to be applied to the file
        self.thething = None #should be set to a tree for file and the chain for chain
        self.bMaxes = {}
        self.bMins  = {}

    def set_name(self,name):
        self.name = name
    def set_quality(self,quality):
        self.quality = quality
    def add_branch(self,*args,**kwargs):
        self.b.append(branch(*args,**kwargs))
    def add_cut(self,*args,**kwargs):
        self.c.append(cut(*args,**kwargs))
    def GetNtrees(self):
        if len(self.t) != len(self.tname):
            print repr(self.name)+" has "+len(t)+" trees but "+len(tname)+" tree names. How did this happen?"
            sys.exit()
        return len(self.t)
    def check_tsize_1(self):
        if self.GetNtrees()==1:
            return True
        else:
            print repr(self.name)+" has a tree list with "+repr(self.GetNtrees())+" trees."
            return False
    def file_1tree_check(self,fname):
        if self.thething.__class__.__name__=='file':
            if not self.check_tsize_1():
                print "file."+fname+" is only available for objects with only one tree."
                sys.exit()
    def can_Draw(self):
        if self.check_tsize_1():
            return True
        else:
            print "fch::Draw is only available for objects with just one associated tree."
    def GetListOfBranches(self):
        self.file_1tree_check("GetListOfBranches")
        temp = []
        for nm in self.thething.GetListOfBranches():
            temp.append(nm.GetName())
        return temp
    def GetNbranches(self):
        self.file_1tree_check("GetNbranches")
        return self.thething.GetNbranches()
    def GetMaximum(self,brname):
        self.file_1tree_check("GetMaximum")
        return self.thething.GetMaximum(brname)
    def GetMinimum(self,brname):
        self.file_1tree_check("GetMinimum")
        return self.thething.GetMinimum(brname)
    def GetbMaxMin(self,brlist=[]):
        self.file_1tree_check("GetMaxMin")
        bloop = []
        if brlist:
            bloop = brlist
        elif self.b:
            for ib in self.b:
                bloop.append(ib.branch)
        else:
            bloop = self.GetListOfBranches()
        for bname in bloop:
            self.bMaxes[bname] = self.GetMaximum(bname)
            self.bMins [bname] = self.GetMinimum(bname)
    def make_histogram(self,thisbranch,linecolor=0): #create an empty histogram
        assocbranch = thisbranch.associated_branch
        if not thisbranch.nBins: thisbranch.nBins = 100 #set default binning if not specified
        hilospec = False #is either loBin or hiBin non-0?
        if thisbranch.loBin or thisbranch.hiBin: hilospec = True
        binning_set = all([thisbranch.nBins,hilospec]) #is the binning completely specified now?
        if assocbranch: #repeat for assocbranch
            if not assocbranch.nBins: assocbranch.nBins = 100
            hilospec = False #is either loBin or hiBin non-0?
            if assocbranch.loBin or assocbranch.hiBin: hilospec = True
            assocbinning_set = all([assocbranch.nBins,hilospec])
            if not assocbranch:
                h = TH1F(hname,thisbranch.name,thisbranch.nBins,thisbranch.loBin,thisbranch.hiBin)
            else:
                h = TH2F(hname,thisbranch.name+' vs. '+assocbranch.name,thisbranch.nBins,thisbranch.loBin,thisbranch.hiBin,assocbranch.nBins,assocbranch.loBin,assocbranch.hiBin)
            if not assocbranch:
                if(not binning_set or thisbranch.can_extend): h.SetCanExtend(TH1.kAllAxes)
            else:
                if(not binning_set or thisbranch.can_extend): h.SetCanExtend(TH1.kXaxis)
                if(not assocbinning_set or assocbranch.can_extend): h.SetCanExtend(TH1.kYaxis)
                h.GetXaxis().SetTitle(thisbranch.branch)
                h.GetYaxis().SetTitle(assocbranch.branch)


    def Draw(self,thisbranch,acut="",opt="",return_hist=False):
        if self.can_Draw():
            if not thisbranch.__class__.__name__ == 'branch': #if a string is passed
                self.thething.Draw(varexp,acut,opt)
            else: #if a branch object is passed
                #draw histograms
                if not assocbranch:
                    h.SetLineColor(hi+1)
                    if((hi+1==5) or (hi+1==10)): h.SetLineColor(hi+21)
                    #if any branches have these options set, draw them that way:
                    if(thisbranch.set_log_X): ci.SetLogx()
                    if(thisbranch.set_log_Y): ci.SetLogy()
                    placeholder = thisbranch.branch+">>"+hname
                else:
                    placeholder = assocbranch.branch+":"+thisbranch.branch+">>"+hname
                    if(thisbranch.set_log_X):  ci.SetLogx()
                    if(assocbranch.set_log_X): ci.SetLogy()
                    if(thisbranch.set_log_Y or assocbranch.set_log_Y): ci.SetLogz()
                try:
                    thisfile.Draw(placeholder,thiscut.cut,drawopt)#one tree per file
                except:
                    print "Draw() failed for "+placeholder
                    print "in file: "+thisfile.name
                    print "with cut: "+thiscut.name
                    print "Attempting to draw again..."
                    h.SetCanExtend(TH1.kAllAxes)
                    thisfile.Draw(placeholder,thiscut.cut,drawopt)#one tree per file
                if(verbose): print "done"
