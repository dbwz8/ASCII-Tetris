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
regs        = 0                 # Global register
play        = [False,False]     # play state
curTime     = [0,0]             # Time on each channel
gates       = []

def doFlips(gate,cur):
    global regs

    if regs & 0x80 == 0: cur |= 0x80      # Always flip top bit
    prv         = regs
    flips       = prv ^ cur
    if flips == 0: raise(Exception("Should always have at least 1 flip for top bit"))
    for idx,bit in enumerate([1,2,4,8,16,32,64,128]):
        if flips & bit != 0:
            gates.append((gate,[idx]))
            regs ^= bit
    
def doDelay(chan,n):
    hgh = (n >> 6) & 0x7F
    low = n & 0x3F
    if chan: low |= 0x40

    doFlips('Z',hgh)
    doFlips('X',low)

def doNote(chan,n):    
    if chan == 0:   gate = 'H'
    else:           gate = 'S'
    doFlips(gate,n & 0x7F)

for (t,c,p),(d,n) in itms:

    print(f'//                     {t:6d},{c}: {p:3},{d:4},{n:3}')

    doDelay(c,t-curTime[c])
    curTime[c]      =  t

    # Turn off the current guy?
    if (not p and play[c]) or (p and not play[c]):
        doNote(c,n)
        play[c] = p
    else:
        raise(Exception(f"# Got case: c={c} p={p} play={play[c]} n={n} regs={regs}"))

# Collapse gates together
if True:
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
            if totLen == 2: g = 'C' + g
            else:           g = 'CC' + g
            qs = qs0 + qs1
            qs.sort()
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
        use qs = Qubit[8];
''',file=f)

    for (g,qs) in gates: 
        print(f"        {g}(",end='',file=f)
        for i,q in enumerate(qs): 
            if i > 0: print(f',qs[{q}]',end='',file=f)
            else:     print(f'qs[{q}]',end='',file=f)
        if False and qs[-1] > 4:
            if   g == 'X':  str = '    // store low 5 bits'
            elif g == 'Y':  str = '    // store mid 5 bits'
            elif g == 'Z':  str = '    // store hgh 5 bits'
            elif g == 'M':  str = '    // Do Delay'
            elif g == 'H':  str = '    // Do Chan1'
            elif g == 'S':  str = '    // Do Chan2'
        else:
            str = ''
        print(f');{str}',file=f)

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

# create notes from Q# circuit:
if True:
    regs    = 0
    play    = [0,0]
    delay   = 0
    state   = 0
    prvTop  = 0
    chan    = 0
    note    = 0
    for g,qs in gates:
        for q in qs: regs ^= 1 << q
        #print(f'@@@DBG g={g} q={q} regs={regs:02x} prvTop={prvTop} state={state} delay={delay} chan={chan} note={note}')
        if (regs & 0x80) != (prvTop & 0x80):        # Top bit toggles when something to do
            prvTop  = 0x80 ^ prvTop
            if state == 0:
                if g[-1] != 'Z': raise(Exception(f"In wrong state {state} for {g}"))
                delay   = (regs & 0x7F) << 6
                state = 1
            elif state == 1:
                if g[-1] != 'X': raise(Exception(f"In wrong state {state} for {g}"))
                delay   |= (regs & 0x3F)
                if regs & 0x40: chan = 1
                else:           chan = 0
                state = 2
            elif state == 2:
                if g[-1] != 'H' and g[-1] != 'S': raise(Exception(f"In wrong state {state} for {g}"))
                note        = regs & 0x7F
                state       = 0

                play[chan]    ^= 1
                if play[chan]:  mode = 'note_on'
                else:           mode = 'note_off'
                print(f'Message({mode},channel={chan}, note={note}, velocity=70, time={delay})')
                if chan == 0: track = track1
                else:      track = track2
                track.append(Message(mode,channel=chan, note=note, velocity=70, time=delay))
            else: raise(Exception(f"Unexpected state: {state}"))

# Try reading back the compiled Q# code and create the midi file
if False:
    regs    = [0,0,0,0] # Z,X,Y,M
    play    = [0,0]
    delay   = 0
    with open("compiledQS.log","r") as inp:
        while True:
            line    = inp.readline()
            if not line: break
            if len(line) != 10: continue

            qs = []
            g  = '?'
            for i in range(8):
                if line[i] == 'C':
                    qs.append(i)
                else:
                    for j,tst in enumerate(['Z','X','H','S']):
                        if line[i] == tst:
                            qs.append(i)
                            g = tst
                            c = j
                            break
            if len(qs) > 0 and g != '?':
                for q in qs:
                    if q < 7: regs[c] ^= 1 << q
                    elif g == 'X' or g == 'Z':
                        play[c]    ^= 1
                        if play[c]: mode = 'note_on'
                        else:       mode = 'note_off'
                        print(f'Message({mode},channel={c}, note={regs[c]}, velocity=70, time={delay})')
                        if c == 0: track = track1
                        else:      track = track2
                        track.append(Message(mode,channel=c, note=regs[c], velocity=70, time=delay))
                    elif g == 'H':
                        delay = (delay & 0x3F80) | regs[c]
                    elif g == 'S':
                        delay = (delay & 0x07F) | (regs[c] << 7)
                    else: raise(Exception(f"Unexpected gate: {g}"))

mid.save('midi2qs.mid')

# play notes
if True:
    for msg in mid:
        time.sleep(msg.time)
        if not msg.is_meta:
            port.send(msg)
