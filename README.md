# midiCNC
This is a quickly hacked together Python program to convert MIDI files to G code commands so they can be played on the stepper motors of a CNC machine. There are a bunch of these MIDI to G code convertes around, but none of them support more than the standard 3; X Y Z axes. I set up some steppers with grbl-mega-5x, which supports up to 6 stepper motor axes. 

The mido python library is used to read the midi files (since it was quick and easy to get going). From there, almost none of the other midi features are used; the program just looks at the note_on and note_off commands (on all channels), and uses that to figure out what to play. I have found that many existing MIDI files do not use this format for some reason, but importing the file into a MIDI editor and exporting it again usually takes care of that. From there, each axes is treated as an availible "instrument" that can be used to play one note. Each note start in the MIDI file is assigned to a stepper randomly, unless all steppers are being used, in which case it is simply ignored. When the note ends, it frees up a stepper that was playing that note.

The tricky part is figuring out the distance and feedrate commands, which affect both the duration and pitch of a note. Critically, the feedrate affects the straight line distance of a G1 move, but that nothing the pythagorean therom can't fix. The only exception is when no notes are being played, which is where the G4 (dwell) command is used.

**vpool2.mid** is an example midi, extracted from an old DOS game's sound card output. 
**output.nc** is what you get when running the program (raw gcode) 

## midiorch.py
This is an offshoot where I used the same principle to try and convert MIDIs to an archaic format for the TRS-80. The Orchestra-85 (and the earlier Orchestra-80) were music solutions for the TRS-80 line of computers. The hardware was pretty much a resistor DAC hooked up to a latch and address decoder, which went directly to one of the Z80's output ports. There was no sound chip of any kind; instead, the auto was completely generated in software - it was an early synthesizer program. Anyway, the software used to program it has this weird syntax unlike anything I've ever seen. While there is a large archive of .ORC files out there still, I wanted to try making new music, and converting some MIDI files seemed like a good start. 

This kind of works, but there's some obvious missing pieces.
