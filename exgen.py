#!/usr/bin/env python

import copy
import re

whitekeys = ["c","d","e","f","g","a","b"]
offsets = [ 0,2,4,5,7,9,11 ]
names = ["c","d","e","f","g","a","b"]
accidentals = ["bb","b",None,"#","x"]
class Note():
    def __init__(self,key,octave,accidental=None):
        self.key = key
        self.octave = octave
        self.accidental = accidental
    def __repr__(self):
        if not self.accidental is None:
            return "[ %s%s, %d ]" % (self.key,self.accidental,self.octave)
        else:
            return "[ %s, %d ]" % (self.key,self.octave)
    def NoteNumber(self):
        return 12*(self.octave-1) + \
               offsets[whitekeys.index(self.key)] + \
               accidentals.index(self.accidental)-2
    def sharpen(self):
        ai = accidentals.index(self.accidental)
        if ai<len(accidentals)-1:
            self.accidental = accidentals[ai+1]
    def flatten(self):
        ai = accidentals.index(self.accidental)
        if ai>0:
            self.accidental = accidentals[ai-1]
    def next(self):
        keyindex = whitekeys.index(self.key)
        if keyindex==len(whitekeys)-1:
            n = Note( whitekeys[0], self.octave+1 )
        else:
            n = Note( whitekeys[keyindex+1], self.octave )
        return n
    def chromaticnext(self):
        if self.accidental=="x":
            print "Can not handle double sharps"; return self
        if self.accidental==None:
            if self.key in ["e","b"]:
                return self.next()
            else:
                return Note(self.key,self.octave,"#")
        elif self.accidental=="bb":
            return Note(self.key,self.octave,"b")
        elif self.accidental=="b":
            return Note(self.key,self.octave,None)
        elif self.accidental=="#": 
            keyindex = whitekeys.index(self.key)
            if keyindex==len(whitekeys)-1:
                n = Note( whitekeys[0], self.octave+1 )
            else:
                n = Note( whitekeys[keyindex+1], self.octave )
            return n
        else:
            print "What did we miss?"
    def prev(self):
        keyindex = whitekeys.index(self.key)
        if keyindex==0:
            n = Note( whitekeys[len(whitekeys)-1], self.octave-1 )
        else:
            n = Note( whitekeys[keyindex-1], self.octave )
        return n
    def EnharmonicRespell(self):
        if self.accidental=="b":
            n = self.prev()
            if self.key not in ["c","f"]:
                n.accidental = "#"
            return n
        elif self.accidental=="#":
            n = self.next()
            if self.key not in ["b","e"]:
                n.accidental = "b"
            return n
        else: return self                
    def EnharmonicPrefered(self):
        if (self.accidental=="#" and self.key in ["c","d","g","a"]) or \
                (self.accidental=="b" and self.key in ["g"]):
            return self.EnharmonicRespell()
        else: return self
    def Major2nd(self):
        n = self.next()
        if self.key in ["e","b"]:
            n.accidental = accidentals[accidentals.index(self.accidental)+1]
        else:
            n.accidental = self.accidental
        return n
    def Minor2nd(self):
        n = self.next()
        if self.key in ["e","b"]:
            n.accidental = self.accidental
        else:
            n.accidental = accidentals[accidentals.index(self.accidental)-1]
        return n
    def Major3rd(self):
        return self.Major2nd().Major2nd()
    def Minor3rd(self):
        return self.Major2nd().Minor2nd()
    def Natural5th(self):
        return self.Major3rd().Minor3rd()
    def Octave(self):
        return Note(self.key,self.octave+1,self.accidental)
    def WhiteKeyJump(self,num):
        if num<=0:
            print "No intervals down supported"; return copy.copy(self)
        else:
            res = copy.copy(self)
            for i in range(num-1):
                r = res.next()
                res = r
            return res
    def NoteChromaticRange(self,n2):
        """ inclusive range from self to n2"""
        t = copy.copy(self)
        while t<n2:
            yield t
            t = t.chromaticnext()
        yield t
    def WhiteKeyRange(self,n2):
        """inclusive range from note n1 to note n2"""
        if self.octave>n2.octave:
            yield None
        elif self.octave==n2.octave:
            for whitekey in \
                    whitekeys[ whitekeys.index(self.key) :
                               whitekeys.index(n2.key)+1 ]:
                yield Note(whitekey,self.octave)
        else:
            # remaining notes in this octave
            for whitekey in whitekeys[ whitekeys.index(self.key) : ]:
                yield Note(whitekey,self.octave)
            # intervening full octaves in between
            for o in range(self.octave+1,n2.octave):
                for whitekey in whitekeys:
                    yield Note(whitekey,o)
            # notes in top octave
            for whitekey in whitekeys[ : whitekeys.index(n2.key)+1 ]:
                yield Note(whitekey,n2.octave)
    def WhiteKeyRangeRelative(self,n):
        top = copy.copy(self)
        for i in range(n): top = top.next()
        return self.WhiteKeyRange(top)
    def ChromaticRangeRelative(self,n):
        top = copy.copy(self)
        for i in range(n): top = top.next()
        return self.NoteChromaticRange(top)
    def __eq__(self,n):
        return self.key==n.key and self.octave==n.octave \
               and self.accidental==n.accidental
    def __lt__(self,n):
        return self.octave<n.octave or \
               ( self.octave==n.octave and \
                 whitekeys.index(self.key)<whitekeys.index(n.key) ) or \
               ( self.octave==n.octave and \
                 whitekeys.index(self.key)==whitekeys.index(n.key) and \
                 accidentals.index(self.accidental)<accidentals.index(n.accidental) )
    def __le__(self,n):
        return self<n or self==n
    def max(self,other):
        if self<other: return other
        else: return self
    def WhiteKeyDistance(self,n2):
        if n2<self:
            return -n2.WhiteKeyDistance(self)
        return ( whitekeys.index(n2.key)-whitekeys.index(self.key)+1 ) + \
               7*(n2.octave-self.octave)
    def ChromaticDistance(self,n2):
        if n2<self:
            return n2.ChromaticDistance(self)
        else:
            return 1+self.next().ChromaticDistance(n2)
    def Lilyize(self):
        r = self.key
        if self.accidental=="x": r += "isis"
        if self.accidental=="#": r += "is"
        if self.accidental=="b": r += "es"
        if self.accidental=="bb": r += "eses"
        return r
    def LilyizeRelative(self,n):
        r = self.Lilyize(); w = n.WhiteKeyDistance(self)
        if w<0:
            w *= -1; c = ","
        else: c = "'"
        if w>0:
            w -= 4
            while w>0:
                r += c; w -= 7
        return r
class NoteFromNumber(Note):
    def __init__(self,number):
        octave = int(number/12); offset = number-12*octave
        for i in range(len(offsets)):
            if offsets[i]==offset:
                Note.__init__(self,names[i],0); break
            if offsets[i]>offset:
                Note.__init__(self,names[i-1],"#"); break

def testNoteNumbers():
    n = Note("c",1,"b").NoteNumber(); print n
    assert( n==-1 )
    n = Note("c",2,"x").NoteNumber(); print n
    assert( n==14 )
def testNotePrevNext():
    print "prev next"
    n = Note("c",1); nn = n.next()
    assert( nn.key=="d" )
    n = Note("b",1); nn = n.next()
    assert( nn.key=="c" and nn.octave==n.octave+1 )
    n = Note("b",1); nn = n.prev()
    assert( nn.key=="a" )
    n = Note("c",1); nn = n.prev()
    assert( nn.key=="b" and nn.octave==n.octave-1 )
    print ".. chromatic"
    n = Note("c",1); nn = n.chromaticnext(); print n,nn
    assert (nn.key=="c" and nn.octave==n.octave and nn.accidental=="#")
    n = Note("c",1,"b"); nn = n.chromaticnext(); print n,nn
    assert (nn.key=="c" and nn.octave==n.octave and nn.accidental==None)
    n = Note("c",1,"#"); nn = n.chromaticnext(); print n,nn
    assert (nn.key=="d" and nn.octave==n.octave and nn.accidental==None)
    n = Note("b",1); nn = n.chromaticnext(); print n,nn
    assert (nn.key=="c" and nn.octave==2 and nn.accidental==None)

def testEnharmonic():
    print "enharmonic substitutions"
    n = Note("c",1,"#"); nn = n.EnharmonicRespell(); print n,nn
    assert( nn.key=="d" and nn.accidental=="b" )
    n = Note("b",1,"#"); nn = n.EnharmonicRespell(); print n,nn
    assert( nn.key=="c" and nn.accidental==None and nn.octave==n.octave+1 )
    n = Note("c",3,"b"); nn = n.EnharmonicRespell(); print n,nn
    assert( nn.key=="b" and nn.accidental==None and nn.octave==n.octave-1 )
    print "enharmonic preferences"
    n = Note("d",1,"#"); nn = n.EnharmonicPrefered(); print n,nn
    assert( nn.key=="e" and nn.accidental=="b" )
    n = Note("g",1,"b"); nn = n.EnharmonicPrefered(); print n,nn
    assert( nn.key=="f" and nn.accidental=="#" )

def testNoteRelations():
    print "relations"
    assert( Note("f",1)<Note("g",1) )
    assert( Note("g",1)<Note("g",2) )

def testIntervals():
    print "interval computation, white key"
    i = Note("c",1).WhiteKeyDistance(Note("f",1)); print i
    assert ( i==4 )
    i = Note("c",1).WhiteKeyDistance(Note("d",2)); print i
    assert ( i==9 )
    i = Note("g",1).WhiteKeyDistance(Note("c",1)); print i
    assert ( i==-5 )
    print ".. chromatic"
    n = Note("c",3).Major2nd(); print n
    assert( n.key=="d" and n.octave==3 and n.accidental==None )
    n = Note("e",3).Major2nd(); print n
    assert( n.key=="f" and n.octave==3 and n.accidental=="#" )
    n = Note("c",3).Minor2nd(); print n
    assert( n.key=="d" and n.octave==3 and n.accidental=="b" )
    n = Note("e",3).Minor2nd(); print n
    assert( n.key=="f" and n.octave==3 and n.accidental==None )
    print "interval formation, white key"
    n = Note("a",2).WhiteKeyJump(5); print n
    assert( n.key=="e" and n.octave==3 and n.accidental==None)
    n = Note("a",2,"b").WhiteKeyJump(5); print n
    assert( n.key=="e" and n.octave==3 and n.accidental==None)

def testWhiteKeyRange():
    print "ranges, white key"
    r = [ n for n in Note("d",1).WhiteKeyRange(Note("g",1)) ]
    print r
    assert ( len(r)==4 and r[3].key=="g" )
    r = [ n for n in Note("g",2).WhiteKeyRange(Note("d",3)) ]
    print r
    assert ( len(r)==5 and r[4].key=="d" )
    r = [ n for n in Note("g",1).WhiteKeyRange(Note("d",3)) ]
    print r
    assert ( len(r)==12 and r[11].key=="d" )
    # relative
    r = [ n for n in Note("g",1).WhiteKeyRangeRelative(7) ]
    print r
    assert ( len(r)==8 and r[7].key=="g" and r[7].octave==2 )

def testChromaticRange():
    print "ranges, chromatic"
    r = [ n for n in Note("c",1).NoteChromaticRange( Note("d",1) ) ]
    print r
    assert( len(r)==3 and r[1].accidental=="#" )
    r = [ n for n in Note("c",1,"#").NoteChromaticRange( Note("d",1) ) ]
    print r
    assert( len(r)==2 and r[1].accidental==None )
    r = [ n for n in Note("c",1).NoteChromaticRange( Note("f",1,"#") ) ]
    print r
    assert( len(r)==7 and r[2].accidental==None )
    r = [ n for n in Note("e",1).NoteChromaticRange( Note("g",1) ) ]
    print r
    assert( len(r)==4 and r[1].accidental==None )

def testLilyizing():
    p = Note("g",1).LilyizeRelative(Note("c",1)); print p
    assert( p=="g'" )
    p = Note("g",2).LilyizeRelative(Note("c",1)); print p
    assert( p=="g''" )

enharmonicsharps = [ "d", "g", "a" ]
class Melody():
    def __init__(self,row,rhythm=None,relative=None):
        self.row = row # a row of note objects
        self.relative = relative
        self.rhythm = rhythm; self.multiple = 1
    def LilyNames(self):
        if self.relative is None:
            last = self.row[0]
        else: last = self.relative
        r = []
        for n in self.row:
            r.append( n.LilyizeRelative(last) )
            last = n
        return r
    def EnharmonicPretty(self):
        if self.row[0].key in enharmonicsharps and \
           self.row[0].accidental=="#":
            return self.EnharmonicFlatten()
        elif len(self.row)>1 and self.row[0].accidental==None and \
             self.row[1].key in enharmonicsharps and \
             self.row[1].accidental=="#":
            return self.EnharmonicFlatten()
        else: return self
    def EnharmonicFlatten(self):
        r = []
        for n in self.row:
            if n.accidental=="#":
                r.append(n.EnharmonicRespell())
            else: r.append(n)
        return Melody(r,self.rhythm)
    def defaultRhythm(self):
        while True: yield 4
    def RhythmInsert(self,n):
        """this takes a note row as argument and yields a lilypond string
        that has the notes with lengths attached"""
        s = ""; i = 0
        flen = self.multiple*int(len(self.row)/self.multiple)
        for r in self.rhythm:
            s += n[i]+str(r)+" "; i+=1
            if i>=flen: break
        if flen<len(self.row):
            for r in self.defaultRhythm():
                s += n[i]+str(r)+" "; i+=1
                if i>=len(self.row): break
        return s
    def LilyString(self,rhythm=None):
        if self.rhythm==None and rhythm==None:
            self.rhythm = self.defaultRhythm()
        i=0; s = ""; n = self.LilyNames()
        s = self.RhythmInsert(n)
        return s
    def RelativeLilyString(self):
        return "\\relative %s { %s }" % (str(self.relativec()),self.LilyString())
    def relativec(self):
        if self.row==[]:
            self.rootc = 0 # octave?
        elif self.row[0].key in ["g","a","b"]:
            self.rootc = self.row[0].octave+1
        else:
            self.rootc = self.row[0].octave
        s = "c"
        if self.rootc>0:
            for i in range(self.rootc):
                s += "'"
        if self.rootc<0:
            for i in range(-self.rootc):
                s += ","
        return s
    def __add__(self,other):
        return Melody( self.row + other.row )
    def __str__(self):
        return str(self.row)
    def __len__(self):
        return len(self.row)

def testRespelling():
    r = Melody( [ Note("d",1,"#"), Note("g",1,"#") ] )
    s = r.EnharmonicFlatten(); print r.row,s.row
    assert( len(s.row)==2 and s.row[1].key=="a" and s.row[1].accidental=="b" )

def testLilyMapping():
    r = Melody( [ Note("c",1), Note("f",1,"#") ] )
    l = r.LilyNames(); print l
    assert ( l==["c","fis"] )
    r = Melody( [ Note("c",1), Note("g",1) ] )
    l = r.LilyNames(); print l
    assert ( l==["c","g'"] )
    r = Melody( [ Note("c",2), Note("g",1) ] )
    l = r.LilyNames(); print l
    assert ( l==["c","g"] )
    r = Melody( [ Note("c",2), Note("f",1,"#") ] )
    l = r.LilyNames(); print l
    assert ( l==["c","fis,"] )

class SubsetMelody(Melody):
    def __init__(self,row,indices,rhythm=None,relative=None):
        for i in indices: assert( indices[i]<len(row) and indices[i]>=0 )
        Melody.__init__(self, [ row[i] for i in indices ],
                        rhythm=rhythm, relative=relative )

def testFormulaMapping():
    f = [ 0,2,1,2 ]
    m = SubsetMelody( [ Note("c",1), Note("d",2), Note("c",2) ] ,f ).row
    print m
    assert( len(m)==4 and m[2].key=="d" )


class TransposableMelody(Melody):
    def __init__(self,row):
        Melody.__init__(self,row)
        self.direction = "up"
    def RotateUp(self):
        if self.direction=="up":
            top = copy.copy(self.row[1]); top.octave += 1
            t = self.row[1:]+[top]
            return Scale(row=t,direction=self.direction)
        elif self.direction=="updown":
            l = (len(self.row)+1)/2
            r1 = copy.copy( self.row[1:l] )
            r2 = copy.copy( self.row[l-1:len(self.row)-1] )
            top = copy.copy(self.row[1]); top.octave += 1
            return Scale(row=r1+[top]+r2,direction=self.direction)
        else: # direction is down
            print "Can not handle down scales"

class Scale(TransposableMelody):
    def __init__(self,root=None,row=None,direction="up"):
        self.direction = direction; self.rhythm = None
        if row is not None:
            Melody.__init__(self,row)
        elif root is None:
            Scale.__init__(self,root=Note("c",1),direction=direction)
        else:
            n2 = root.Major2nd(); n3 = n2.Major2nd();
            n4 = n3.Minor2nd(); n5 = n4.Major2nd();
            n6 = n5.Major2nd(); n7 = n6.Major2nd(); n8 = n7.Minor2nd();
            row = [root,n2,n3,n4,n5,n6,n7,n8]
            if direction=="down":
                r = copy.copy(row)
                r.reverse()
                Scale.__init__(self,row=r,direction=direction)
            elif direction=="updown":
                t = copy.copy(row); t.reverse()
                Scale.__init__(self,row=row[:len(row)-1]+t,direction=direction)
            else: # direction=="up":
                Scale.__init__(self,row=row,direction=direction)

def testScales():
    s = Scale(Note("f",1),direction="updown"); print s.row
    assert( s.row[11].accidental=="b" )
def testScaleRotating():
    print "scale rotating"
    f = Scale(Note("f",1),direction="up")
    g = f.RotateUp(); print g.row
    assert( len(f)==len(g) )
    assert( g.row[2].key=="b" and g.row[2].accidental=="b")
    assert( g.row[0].key==f.row[1].key and g.row[7].key==f.row[1].key )
    assert( g.row[0].octave+1==g.row[7].octave )
    f = Scale(Note("f",1),direction="updown")
    g = f.RotateUp(); print g.row
    assert( len(f)==len(g) )
    assert( g.row[2].key=="b" and g.row[2].accidental=="b")
    assert( g.row[0].key==f.row[1].key and g.row[7].key==f.row[1].key )
    assert( g.row[0].octave+1==g.row[7].octave )

class FingeringChart():
    def __init__(self,lo,row):
        self.offset = lo.NoteNumber()
        self.chart = []
        for f in row:
            f = re.sub("\|","",f)
            f = f+"oooooooo"[len(f):]
            self.chart.append( f )
    def Fingering(self,Note):
        number = Note.NoteNumber()
        return self.chart[number-self.offset]
    def Notes(self):
        for i in range(len(self.chart)):
            number = self.offset+i
            yield FingeredNote(i) # unfinished
    def FingerStatus(self,Note,finger):
        return self.Fingering(Note)[finger]
    def Transition(self,n1,n2):
        f1 = self.Fingering(n1); f2 = self.Fingering(n2)
        changes = ""
        for i in range(len(f1)):
            if f1[i]==f2[i]:
                changes += "-"
            elif f1[i] in ["x","h"] and f2[i]=="o":
                changes += "o"
            elif f1[i]=="o" and f2[i] in ["x","h"]:
                changes += "x"
            elif (f1[i]=="x" and f2[i]=="h") or (f1[i]=="h" and f2[i]=="x"):
                changes += "h"
            else:
                changes += "."
        return changes

regchart = [ "x|xxx|xxxx","x|xxx|xxxh","x|xxx|xxx","x|xxx|xxh","x|xxx|xx",# F-A
           "x|xxx|xoxx","x|xxx|oxx","x|xxx","x|xxo|xxh","x|xx",# Bb-D
           "x|xox|x","xx","xox","oxx","oox","o|oxx|xxx",# Eb-Ab
           "h|xxx|xx","h|xxx|xox","h|xxx|oxo","h|xxx","h|xxox", # A-C#
           "h|xx","h|xxo|xxx","h|xxo|xx","h|xoo|xx", # D-F
           "h|xox|xxxx","h|xox|xoxx"
           ]
Fchart = FingeringChart( Note("f",1), regchart)
Cchart = FingeringChart( Note("c",1), regchart)

def testFingerings():
    print "fingering chart"
    chart = FingeringChart(Note("c",2),
                       ["x|xxx","x|xxo|xxh","x|xx","x|xox|x","x|x","x|0x"])

    s = chart.FingerStatus( Note("e",2,"b"),2 ); print s
    assert( s=="o" )
    s = chart.FingerStatus( Note("e",2,"b"),3 ); print s
    assert( s=="x" )
    t = Fchart.Transition( Note("f",1), Note("f",1,"#") ); print t
    assert( t=="-------h" )

 
if __name__== "__main__":
    testNoteNumbers()
    testNotePrevNext()
    testEnharmonic()
    testNoteRelations()
    testIntervals()
    testWhiteKeyRange()
    testChromaticRange()
    testRespelling()
    testLilyizing()
    testLilyMapping()
    testFormulaMapping()
    testScales()
    testScaleRotating()
    testFingerings()
    
