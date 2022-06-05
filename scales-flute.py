from exgen import *
import copy

def alltransposes(scale):
    yield copy.copy(scale)
    for i in range(15):
        old = copy.copy(scale)
        scale = old.RotateUp()
        yield scale

def group2(i):
    if i==0:
        while True:
            yield "8"
            yield "8"
    elif i==1:
        while True:
            yield "8."
            yield "16"
    else:
        while True:
            yield "16"
            yield "8."
def group3(i):
    if i==0:
        while True:
            yield "8."
            yield "32"
            yield "32"
    elif i==1:
        while True:
            yield "32"
            yield "8."
            yield "32"
    else:
        while True:
            yield "32"
            yield "32"
            yield "8."
def grouptrio(g,n):
    def groupone(n):
        return n[0]+"8( "+n[0]+"32) "+n[1]+" "+n[2]+" "+n[3]+" "
    def grouptwo(n):
        return n[0]+"16 "+n[1]+"8 "+n[2]+"32 "+n[3]+" "
    def groupthree(n):
        return n[0]+"32 "+n[1]+" "+n[2]+"8 "+n[3]+"16 "
    def groupfour(n):
        return n[0]+"32 "+n[1]+" "+n[2]+" "+n[3]+"( "+n[3]+"8) "
    s = ""
    for l in [0,4,8]:
        if g==0:
            s += groupone(n[l:])
        elif g==1:
            s += grouptwo(n[l:])
        elif g==2:
            s += groupthree(n[l:])
        elif g==3:
            s += groupfour(n[l:])
    s += n[12]+"8. "+n[13]+"32 "+n[14]+"32 "
    return s

class TwoOctaveScale(Scale):
    def __init__(self,root=None,row=None,direction="up"):
        scale1 = Scale(root=root,direction="up")
        scale1.Shorten()
        scale2 = Scale(root=root.Octave(),direction="up")
        #scale2.Shorten()
        Scale.__init__(self, row=scale1.row+scale2.row, direction=direction )
        self.gamut = 2

print """\\header {
title = \"Scale exercises for Flute\"
composer = \"Victor Eijkhout\"
copyright = \"Victor Eijkhout 2014\"
}
"""
roots = [ Note("c",1), Note("c",1,"#"), Note("d",1), 
                 Note("e",1,"b"), Note("e",1), Note("f",1),
                 Note("f",1,"#"), Note("g",1), Note("a",1,"b"),
                 Note("a",1), Note("b",1,"b"), Note("b",1),
                 Note("c",2) ]
roots = [ Note("c",1) ]

for scale in [ TwoOctaveScale( n ,direction="updown") for n in roots ]:
    for n in [6, 2, 5, 1, 4, 3, 0]: # that last zero has no effect
        for g in range(3):
            for s in alltransposes(scale):
                s.rhythm = group2(g); s.multiple=2
                print "\\relative",s.relativec(),"{",s.LilyString(),"}"
        for g in range(3):
            for s in alltransposes(scale):
                s.rhythm = group3(g); s.multiple=3
                print "\\relative",s.relativec(),\
                      "{ \\time 5/4 ",s.LilyString(),"}"
        for g in range(4):
            for s in alltransposes(scale):
                s.RhythmInsert = lambda n : grouptrio(g,n); s.multiple=2
                print "\\relative",s.relativec(),"{",s.LilyString(),"}"
        scale.row[n].flatten()
print "\\paper{ page-breaking=#ly:minimal-breaking }"
print "\\version \"2.11.39\" "

