#Alnwlsn's MIDI to CNC converter - 2021/02/14
#converts a Midi file to Gcode which can play on stepper motors
#the midi files should have note on and note off messages. Not all do, but opening them in a MIDI editor and exporting again seems to fix them
#tested with 5 steppers on a Ramps 1.4 board / Arduino Mega running grbl-mega-5x
stepsmm = 128 #steps per mm
shiftnote = 6 #notes to shift output up by
timescale = 1.5 #adjusts tempo (multiplier)
dlimit = 25 #keep position close to + or - this many mm (center 0)
axes = ["X","Y","Z","A","B","C"] #axes names as if they would be used in a G1 command

import mido
import math
import random

mid = mido.MidiFile('vpool2.mid') #midi file to open

#instrument array - -1 if nothing playing, note value otherwise
instrument = []
for x in axes:
    instrument.append(-1)

#count the number of events, and find the smallest time between events
eventCount=0
minTime=10000
for msg in mid:
    if(msg.time!=0):
        eventCount+=1
        if(msg.time<=minTime):
            minTime=msg.time
#print("midtime=",minTime," events=",eventCount)

#list all the events, and the number of ticks between them
timeTotal=0
score = [] #state of all instruments at a particular time
for msg in mid:
    if(msg.time!=0):
        #print("ticks:",int(msg.time/minTime)," event:",eventCount)
        score.append([instrument[:],int(msg.time/minTime)])
    if(msg.type=='note_on'):
        #print("note_on:",msg.note)
        try:
            idlematch = [i for i, x in enumerate(instrument) if x == -1] #get list of idle insturment indexes
            i=random.choice(idlematch) #randomly select one of the idle instruments
            instrument[i]=msg.note #play note
        except: #there are none spare
            pass
    if(msg.type=='note_off'):
        #print("note_off:",msg.note)
        try:
            i=instrument.index(msg.note) #look for an instrument playing this note
            instrument[i]=-1 #stop playing note
        except: #the note is not being played
            pass
ff=[]
for x in instrument:
    ff.append(-1)
score.append([ff,minTime])

minTime=minTime/timescale #do any time scaling if needed

#convert score instrument note numbers to moves (and times from ticks to seconds)
for x in score:
    x[1] = x[1]*minTime #time from ticks to seconds
    v=[]
    if(max(x[0])==-1): #a special case for all instruments at zero: just wait
        #we just keep x[1] as the time in seconds
        for z in x[0]:
            v.append(0)
    else:
        #calculate moves with the correct feedrates
        w = []
        for y in x[0]:
            if(y==-1):
                y=0
            else:
                y = 440*2**((y+shiftnote-69)/12) #note frequency
            w.append(y)
        #calculate 3D correction (instead of going in single axis, feedrate now affects straight line distance in nth dimension (pythagoras))
        dc = 0
        for z in w:
            dc+=(z)*(z)
        dc = math.sqrt(dc)
        f=(dc*60)/stepsmm #feedrate in mm/s
        for y in w:            
            y = ((y*f*x[1])/60)/dc #frequency to distance in mm
            v.append(y)
        x[1] = f #time to feedrate
    x[0] = v

#open the output file
f = open("output.nc",mode="w",newline='')
f.write("G10 P0 L20 X0 Y0 Z0 A0 B0 C0\r\n") #reset axes to zero
f.write("G90\r\n") #units mm
positions = [] #need to accumulate the relative moves from above into absolute potsitions
dir = [] #direction multiplier for each axes
for x in instrument:
    positions.append(0)
    dir.append(1)

for x in score: #go through the score and make the g code
    #print(x)
    oline = ""
    if(all(y==0 for y in x[0])): #all notes "0" - need to wait instead of move
        oline = "G4 P{:.4}\r\n".format(round(x[1],4))
    else:
        i=0
        for y in x[0]:
            positions[i]+=(y*dir[i])
            if(positions[i]>dlimit):
                dir[i]=-1
            if(positions[i]<-dlimit):
                dir[i]=1
            i+=1
        oline = "G1 "
        j=0
        for z in axes:
            oline += z + "{:.4f} ".format(round(positions[j],4))
            j+=1
        oline += "F{:.4f}\r\n".format(round(x[1],4))
    print(oline)
    f.write(oline)
f.close()
