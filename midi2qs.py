import time
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from mido import midifiles

mid     = MidiFile("John_williams_-_Star_Wars_Cello_Bass_Duet.mid")
dic     = {}
noteMin = 127
noteMax = 0
timeMin = 9999
for _, track in enumerate(mid.tracks):
    curTime     = 0
    for msg in track:
        #print(msg)
        if msg.type == 'note_on' or msg.type == 'note_off':
            curTime        += msg.time
            if msg.type == 'note_on':   
                play        = True
                if msg.note < noteMin: noteMin = msg.note
                if msg.note > noteMax: noteMax = msg.note
            else:
                play = False

            # Handle turn off/on in no time
            key         = (curTime,msg.channel,play)
            dic[key]    = msg.time,msg.note

            if msg.time > 0 and msg.time < timeMin:
                timeMin = msg.time

# Split out into channels
if noteMax-noteMin > 63: print(f"*** WARNING *** Note range = {noteMax-noteMin}")
itms        = sorted(dic.items(),key=lambda ele: ele[0])
itms        = [((int(t/(timeMin/5.0)),c,p),(d,n-noteMin)) for ((t,c,p),(d,n)) in itms]

for (t,c,p),(_,n) in itms:
    print(f'{t:6d},{c}: {p},{n}')

############################## Now re-create MIDI file from what we parsed

# open MIDI port to play music
ports = mido.get_output_names()
port = mido.open_output(ports[0])

# create new MIDI file
mid = MidiFile()
track0 = MidiTrack() # tempo
track1 = MidiTrack() # instrument 1
track2 = MidiTrack() # instrument 2
mid.tracks.append(track0)
mid.tracks.append(track1)
mid.tracks.append(track2)

# set tempo
bpm = 240 # beat per minutes
track0.append(MetaMessage('set_tempo', tempo=int(1000000*60/bpm), time=0))

# create notes
mul     = timeMin/5.0
for (t,c,p),(d,n) in itms:
    curTime = t-d
    n      += noteMin
    if c == 0: track = track1
    else:      track = track2

    if p:   mode = 'note_on'
    else:   mode = 'note_off'
    track.append(Message(mode,channel=c, note=n, velocity=70, time=d))

mid.save('midi2qs.mid')

# play notes
for msg in mid:
    time.sleep(msg.time)
    if not msg.is_meta:
        port.send(msg)