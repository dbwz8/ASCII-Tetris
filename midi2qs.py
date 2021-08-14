import time
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from mido import midifiles

mid     = MidiFile("John_williams_-_Star_Wars_Cello_Bass_Duet.mid")
dic     = {}
for _, track in enumerate(mid.tracks):
    curTime     = 0
    for msg in track:
        print(msg)
        if msg.type == 'note_on' or msg.type == 'note_off':
            curTime        += msg.time
            if msg.type == 'note_on':   
                play        = True
            else:
                play = False

            # Handle turn off/on in no time
            key         = (curTime,msg.channel,play)
            dic[key]    = msg.time,msg.note

# Split out into channels
itms        = sorted(dic.items(),key=lambda ele: ele[0])
itms        = [((t,c,p),(d,n)) for ((t,c,p),(d,n)) in itms]

# Create Q#
regs        = [0,0,0,0]         # Z,X,Y,M
play        = [False,False]     # play state
curTime     = [0,0]             # Time on each channel
gates       = []

def doFlips(gate,chan,cur):
    prv         = regs[chan]
    didFlips    = False
    flips       = prv ^ cur
    for idx,bit in enumerate([1,2,4,8,16,32,64]):
        if flips & bit != 0:
            gates.append((gate,[idx]))
            didFlips = True
    regs[chan]  = cur
    return didFlips

def doDelay(dly):
    global regs

    hgh = dly // 128
    low = dly % 128

    doFlips('M',3,hgh)
    gates.append(('M',[8]))
    doFlips('Y',2,low)
    gates.append(('Y',[7]))

for (t,c,p),(d,n) in itms:
    print(f'//                     {t:6d},{c}: {p:3},{d:4},{n:3}')

    doDelay(t-curTime[c])
    curTime[c]      =  t

    if c == 0:  gate = 'Z'
    else:       gate = 'X'

    # Turn off the current guy?
    if not p and play[c]:
        if c == 0: gates.append((gate,[7]))
        else:      gates.append((gate,[8]))
        play[c] = p

    elif p and not play[c]:
        doFlips(gate,c,n)
        if c == 0: gates.append((gate,[7]))
        else:      gates.append((gate,[8]))
        play[c] = p
    else:
        raise(Exception(f"# Got case: c={c} p={p} play={play[c]} n={n} regs={regs}"))

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

with open("midi2qs.qs","w") as f:

    print('''namespace QMIDI{
    open Microsoft.Quantum.Convert;
    open Microsoft.Quantum.Math;
    open Microsoft.Quantum.Measurement;
    open Microsoft.Quantum.Canon;
    open Microsoft.Quantum.Intrinsic;

    @EntryPoint()
    operation RunMIDI() : Unit {
        use qs = Qubit[9];
''',file=f)

    for (g,qs) in gates: 
        print(f"        {g}(",end='',file=f)
        for i,q in enumerate(qs): 
            if i > 0: print(f',qs[{q}]',end='',file=f)
            else:     print(f'qs[{q}]',end='',file=f)
        print(');',file=f)

    print('''
        ResetAll(qs);
    }
}
''',flush=True,file=f)

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

# create notes from parsed info
if False:
    for (t,c,p),(d,n) in itms:
        if c == 0: track = track1
        else:      track = track2

        if p:   mode = 'note_on'
        else:   mode = 'note_off'
        #print(f'Message({mode},channel={c}, note={n}, velocity=70, time={d})')
        track.append(Message(mode,channel=c, note=n, velocity=70, time=d))

# create notes from Q# circuit
else:
    regs    = [0,0,0,0] # Z,X,Y,M
    play    = [0,0]
    delay   = 0
    for g,qs in gates:
        if g[-1] == 'Z':    c = 0
        elif g[-1] == 'X':  c = 1
        elif g[-1] == 'Y':  c = 2
        elif g[-1] == 'M':  c = 3
        else: raise(Exception(f'Unexpected gate: {g}'))

        for q in qs:
            if q < 7: regs[c] ^= 1 << q
            elif g[-1] == 'X' or g[-1] == 'Z':
                play[c]    ^= 1
                if play[c]: mode = 'note_on'
                else:       mode = 'note_off'
                print(f'Message({mode},channel={c}, note={regs[c]}, velocity=70, time={delay})')
                if c == 0: track = track1
                else:      track = track2
                track.append(Message(mode,channel=c, note=regs[c], velocity=70, time=delay))
            elif g[-1] == 'Y':
                delay = (delay & 0x3F80) | regs[c]
            elif g[-1] == 'M':
                delay = (delay & 0x07F) | (regs[c] << 7)
            else: raise(Exception(f"Unexpected gate: {g}"))

mid.save('midi2qs.mid')

# play notes
if False:
    for msg in mid:
        time.sleep(msg.time)
        if not msg.is_meta:
            port.send(msg)
