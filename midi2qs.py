import time
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from mido import midifiles

mid     = MidiFile("John_williams_-_Star_Wars_Cello_Bass_Duet.mid")
dic     = {}
noteMin = 127
noteMax = 0
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

# Split out into channels
if noteMax-noteMin > 63: print(f"*** WARNING *** Note range = {noteMax-noteMin}")
itms        = sorted(dic.items(),key=lambda ele: ele[0])
itms        = [((t,c,p),(d,n-noteMin)) for ((t,c,p),(d,n)) in itms]

# Create Q#
regs        = [0,0]             # Current bits
play        = [False,False]     # play state
curTime     = 0
gates       = []

def doFlips(gate,prv,cur):
    flips = prv ^ cur
    for idx,bit in enumerate([1,2,4,8,16,32]):
        if flips & bit != 0:
            gates.append((gate,[idx]))

def doDelay(len):
    hgh = len // 64
    low = len % 64

    if low != 0: doFlips('Y',regs[0],low)
    if hgh != 0: doFlips('M',regs[0],hgh)

for (t,c,p),(d,n) in itms:
    print(f'#                     {t:6d},{c}: {p:3},{d:4},{n:3}')

    # See if we need to wait
    if t > curTime:
        doDelay(curTime-t)
        curTime     = t

    if c == 0:  gate = 'Z'
    else:       gate = 'X'
    # Turn off the current guy?
    if not p and play[c]:
        if c == 0: gates.append((gate,[6]))
        else:      gates.append((gate,[7]))
        play[c] = p

    elif p and not play[c]:
        doFlips(gate,regs[0],n)
        if c == 0: gates.append((gate,[6]))
        else:      gates.append((gate,[7]))
        play[c] = p
        regs[c] = n
    else:
        raise(Exception(f"# Got case: c={c} p={p} play={play[c]} n={n} regs={regs[c]}"))

# Collapse gates together
for i in range(1,len(gates)):
    g0,qs0  = gates[i-1]
    g1,qs1  = gates[i]
    totLen  = len(qs0) + len(qs1)
    g       = g0[-1]
    if g == g1[-1] and totLen < 4:
        rpt = False
        for q in qs0:
            if q in qs1: 
                rpt = True
                break
        if rpt: continue
        if g != 'M':
            if totLen == 2: g = 'C' + g
            else:           g = 'CC' + g
        qs = qs0 + qs1
        gates[i-1] = ('',[])
        gates[i]   = (g,qs)

gates = [(q,qs) for (q,qs) in gates if len(qs) > 0]

for (q,qs) in gates: print(q,qs)

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
for (t,c,p),(d,n) in itms:
    n      += noteMin
    if c == 0: track = track1
    else:      track = track2

    if p:   mode = 'note_on'
    else:   mode = 'note_off'
    track.append(Message(mode,channel=c, note=n, velocity=70, time=d))

mid.save('midi2qs.mid')
print("",flush=True)

# play notes
if False:
    for msg in mid:
        time.sleep(msg.time)
        if not msg.is_meta:
            port.send(msg)
