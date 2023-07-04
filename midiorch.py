#!/usr/bin/python3
# Alnwlsn's MIDI to orch80 converter - 2023/02/13
# modified from my MIDI to gcode converter
# converts a Midi file to ORC files which are used on the Orchestra80/85/90 for the various TRS-80 computers
# the midi files should have note on and note off messages. Not all do, but opening them in a MIDI editor and exporting again seems to fix them
from Tone import Tone
import random
import math
import mido
import sys
axes = ["V1", "V2", "V3", "V4", "V5"]
shiftnote = -12  # notes to shift output up by
timescale = 10 # adjusts tempo (multiplier)

mid = mido.MidiFile(sys.argv[1])  # midi file to open


def simplify(noteString):  # breaks up long strings of notes into shorter (properly notated) versions (in 64ths) +C_+C_+C_+C_+C_ --> S+CX+C
    output = ""
    simplify32 = [
        "XN",
        "TN",
        "T.N",
        "SN",
        "SNXN",
        "S.N",
        "S.NXN",
        "IN",
        "INXN",
        "INTN",
        "INT.N",
        "I.N",
        "I.NXN",
        "I.NTN",
        "I.NT.N",
        "QN",
        "QNXN",
        "QNTN",
        "QNT.N",
        "QNSN",
        "QNSNXN",
        "QNS.N",
        "QNS.NXN",
        "Q.N",
        "Q.NXN",
        "Q.NTN",
        "Q.NT.N",
        "Q.NSN",
        "Q.NSNXN",
        "Q.NS.N",
        "Q.NS.NXN",
        "HN",
        "HNXN",
        "HNTN",
        "HNT.N",
        "HNSN",
        "HNSNXN",
        "HNS.N",
        "HNS.NXN",
        "HNIN",
        "HNINXN",
        "HNINTN",
        "HNINT.N",
        "HNI.N",
        "HNI.NXN",
        "HNI.NTN",
        "HNI.NT.N",
        "H.N",
        "H.NXN",
        "H.NTN",
        "H.NT.N",
        "H.NSN",
        "H.NSNXN",
        "H.NS.N",
        "H.NS.NXN",
        "H.NIN",
        "H.NINXN",
        "H.NINTN",
        "H.NINT.N",
        "H.NI.N",
        "H.NI.NXN",
        "H.NI.NTN",
        "H.NI.NT.N",
        "WN",
        "WNXN",
        "WNTN",
        "WNT.N",
        "WNSN",
        "WNSNXN",
        "WNS.N",
        "WNS.NXN",
        "WNIN",
        "WNINXN",
        "WNINTN",
        "WNINT.N",
        "WNI.N",
        "WNI.NXN",
        "WNI.NTN",
        "WNI.NT.N",
        "WNQN",
        "WNQNXN",
        "WNQNTN",
        "WNQNT.N",
        "WNQNSN",
        "WNQNSNXN",
        "WNQNS.N",
        "WNQNS.NXN",
        "WNQ.N",
        "WNQ.NXN",
        "WNQ.NTN",
        "WNQ.NT.N",
        "WNQ.NSN",
        "WNQ.NSNXN",
        "WNQ.NS.N",
        "WNQ.NS.NXN",
        "WNHN",
        "WNHNXN",
        "WNHNTN",
        "WNHNT.N",
        "WNHNSN",
        "WNHNSNXN",
        "WNHNS.N",
        "WNHNS.NXN",
        "WNHNIN",
        "WNHNINXN",
        "WNHNINTN",
        "WNHNINT.N",
        "WNHNI.N",
        "WNHNI.NXN",
        "WNHNI.NTN",
        "WNHNI.NT.N",
        "WNH.N",
        "WNH.NXN",
        "WNH.NTN",
        "WNH.NT.N",
        "WNH.NSN",
        "WNH.NSNXN",
        "WNH.NS.N",
        "WNH.NS.NXN",
        "WNH.NIN",
        "WNH.NINXN",
        "WNH.NINTN",
        "WNH.NINT.N",
        "WNH.NI.N",
        "WNH.NI.NXN",
        "WNH.NI.NTN",
        "WNH.NI.NT.N",
        "WNWN"
    ]
    # look for repeating entries
    index = 0
    while index < len(noteString):
        count = 0
        note = noteString[index:index + 3]
        while noteString[index:index + 3] == note:
            index += 3
            count += 1
            # print(note,noteString[index:index + 3])
            # print(output)
            # if(len(noteString)<=count): #got stuck here if going past end
            #     print("halt",index,count,note,noteString[index:index + 3],noteString)
            #     for i in noteString:
            #         print("-",i)
            #     quit()
        # print(count, noteString[0:index])
        newNote = simplify32[count - 1].replace("N", note.replace("_", ""))  # replace with simplified version
        output += newNote
    return output


def note(note_number):  # get name and frequency of note
    out = {}
    note_names = [
        "C ",
        "Db",
        "D ",
        "Eb",
        "E ",
        "F ",
        "Gb",
        "G ",
        "Ab",
        "A ",
        "Bb",
        "B "
    ]
    orchName = [
        "-F&",  # Bb1
        "-F_",  # B1
        "-E_",  # C1
        "-D&",  # Db2
        "-D_",  # D2
        "-C&",  # Eb2
        "-C_",  # E2
        "-B_",  # F2
        "-A&",  # Gb2
        "-A_",  # G2
        "-9&",  # Ab2
        "-9_",  # A2
        "-8&",  # B&2
        "-8_",  # B2
        "-7_",  # C2
        "-6&",  # D&3
        "-6_",  # D3
        "-5&",  # E&3
        "-5_",  # E3
        "-4_",  # F3
        "-3&",  # Gb3
        "-3_",  # G3
        "-2&",  # Ab3
        "-2_",  # A3
        "-1&",  # Bb3
        "-1_",  # B3
        "0__",  # C4
        "+1&",  # Db4
        "+1_",  # D4
        "+2&",  # Eb4
        "+2_",  # E4
        "+3_",  # F4
        "+4&",  # Gb4
        "+4_",  # G4
        "+5&",  # Ab4
        "+5_",  # A4
        "+6&",  # Bb4
        "+6_",  # B4
        "+7_",  # C5
        "+8&",  # Db5
        "+8_",  # D5
        "+9&",  # Eb5
        "+9_",  # E5
        "+A_",  # F5
        "+B&",  # Gb5
        "+B_",  # G5
        "+C&",  # Ab5
        "+C_",  # A5
        "+D&",  # Bb5
        "+D_",  # B5
        "+E_",  # C6
        "+F&",  # Db6
        "+F_",  # D6
        "+Gb",  # Eb6
        "+G_"  # E6
    ]
    f = 440 * 2**((note_number - 69) / 12)  # note frequency
    out['freq'] = f
    out['name'] = note_names[note_number % 12] + str((note_number // 12) - 1)
    out['orch'] = "$"
    try:
        if note_number >= 34:
            out['orch'] = orchName[note_number - 34]
    except:
        pass
    return out


# instrument array - -1 if nothing playing, note value otherwise
instrument = []
for x in axes:
    instrument.append(-1)

# count the number of events, and find the smallest time between events
eventCount = 0
minTime = 10000
for msg in mid:
    if (msg.time != 0):
        eventCount += 1
        if (msg.time <= minTime):
            minTime = msg.time
# print("midtime=",minTime," events=",eventCount)

# list all the events, and the number of ticks between them
timeTotal = 0
score = []  # state of all instruments at a particular time
for msg in mid:
    if (msg.time != 0):
        # print("ticks:",int(msg.time/minTime)," event:",eventCount)
        score.append([instrument[:], int(msg.time / minTime)])
    if (msg.type == 'note_on'):
        # print("note_on:",msg.note)
        try:
            idlematch = [i for i, x in enumerate(instrument) if x == -1]  # get list of idle insturment indexes
            i=random.choice(idlematch) #randomly select one of the idle instruments
            # i = idlematch[0] #just use the first availible voice
            instrument[i] = msg.note  # play note
        except:  # there are none spare
            pass
    if (msg.type == 'note_off'):
        # print("note_off:",msg.note)
        try:
            i = instrument.index(msg.note)  # look for an instrument playing this note
            instrument[i] = -1  # stop playing note
        except:  # the note is not being played
            pass
ff = []
for x in instrument:
    ff.append(-1)
score.append([ff, minTime])

minTime = minTime / timescale  # do any time scaling if needed

reFlow = []

for l in score:  # generate "waterfall" - put notes back into a "track"
    # each line
    rounder = 1
    d = ((l[1]) // rounder)
    if d > 0:
        # hack - do this to show the note length properly
        for k in range(0, d):
            pl = []
            rf = []
            for i in l[0]:  # instruments
                if (i != -1):
                    n = note(i)
                    print(n['orch'].ljust(3) + " ", end="")
                    pl.append(n['freq'])
                    rf.append(n['orch'])
                    if n['orch'] == "$":
                        print("can't play", n["name"])
                        quit()
                else:
                    rf.append("$__")
                    print("$   ", end="")
            rounder = 16
            reFlow.append(rf)
            print("")
        print("  {}".format(d))

        # Tone.play(pl,d*minTime*rounder)

inFlow = []  # put into tracks
for j in range(0, len(axes)):
    inFlow.append([i[j] for i in reFlow])


subsinMeasure = 64
currentSub = 0
measureNumber = 0

voiceLine = ["" for x in range(len(axes))]

f = open(sys.argv[1]+".orc", mode="w", newline='')
f.write("V1YA V2YA V3YA V4YA\r\nNQ=25\r\n")

def writeLine(Mnumber):
    st = "M{} ".format(Mnumber)
    for l in range(len(axes)):
        if (voiceLine[l] != "$__" * subsinMeasure):  # if voice is just rests, don't print it
            st += axes[l]
            st += simplify(voiceLine[l])
            st += "\r\n"
    # st=st.replace('_', '')
    print(st)
    f.write(st)


for i in range(0, len(inFlow[0])):
    if (currentSub >= subsinMeasure):
        currentSub = 0
        writeLine(measureNumber)
        measureNumber += 1
        voiceLine = ["" for x in range(len(axes))]
    currentSub += 1
    for l in range(len(axes)):
        voiceLine[l] += inFlow[l][i]
writeLine(measureNumber + 1)

f.close()
