from exgen import *
import itertools

def r1():
    while True:
        yield 16
def r2():
    while True:
        yield "8." ; yield 16
def r3():
    while True:
        yield "8." ; yield "32*2/3" ; yield "32*2/3"; yield "32*2/3"

def PermuteUp(chord):
    count = 0; chord = [ n for n in chord ]
    for perm in itertools.permutations( [0,1,2,3] ):
        four = [ e for e in chord ]
        fourp = TransposableMelody( [ four[v] for v in perm ] )
        print fourp
        exercise = Melody( [] )
        while reduce( lambda x,y: x and y,
                      [ n<=Note("d",3) for n in fourp ] ):
            exercise = exercise+Melody( fourp )
            fourp = fourp.RotateUp()
            four = four[1:]+[ four[1].Octave() ]
            fourp = [ four[v] for v in perm ]
        count += 1
        exercise.rhythm = r1()
        if count==-1:
            s = exercise.RelativeLilyString()
            exercise.rhythm = r2() ; s += exercise.RelativeLilyString()
            exercise.rhythm = r3() ; s += exercise.RelativeLilyString()
            yield s
        else:                
            yield exercise.RelativeLilyString()

def threenotes():
    for root in Note("c",1).NoteChromaticRange(Note("b",1)):
        first = root.EnharmonicPrefered()
        third = first.Major3rd()
        fifth = first.Natural5th()
        chord = [ first,third,fifth,first.Octave() ]
        for p in PermuteUp(chord):
            yield p
    for root in Note("c",1).NoteChromaticRange(Note("b",1)):
        first = root.EnharmonicPrefered()
        third = first.Minor3rd()
        fifth = first.Natural5th()
        chord = [ first,third,fifth,first.Octave() ]
        for p in PermuteUp(chord):
            yield p
    for root in Note("c",1).NoteChromaticRange(Note("b",1)):
        first = root.EnharmonicPrefered()
        third = first.Major3rd()
        fifth = first.Natural5th()
        seventh = fifth.Minor3rd()
        chord = [ first,third,fifth,seventh,first.Octave() ]
        for p in PermuteUp(chord):
            yield p

print """\\header {
title = \"Broken Chords exercises for Soprano recorder\"
composer = \"Victor Eijkhout\"
copyright = \"Victor Eijkhout 2013\"
}
"""
count = 1
for t in threenotes():
    print t
    # print "\\relative",c,"{",\
    #       "\\mark\""+str(count)+"\" ",\
    #       t,\
    #       "}"
    count += 1
print "\\paper{ page-breaking=#ly:minimal-breaking }"
print "\\version \"2.16.2\""
