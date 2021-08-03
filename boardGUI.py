import sys
import msvcrt
import subprocess
from tkinter.constants import S
import PySimpleGUI as sg
from pathlib import Path

width   = 12
height  = 15
font    = ('Courier New', 16)
bg      = 'gray'
colors  = [bg, 'gold', 'blue', 'tomato', 'red', 'green', 'purple', 'brown']

import sys
import threading
import time
import queue
import re

class NoBlock:
    def add_input(self,input_queue):
        while True:
            line    = self.pipe.stdout.readline().rstrip()
            if len(line) > 0: input_queue.put(line)

    def __init__(self):
        self.pipe                   = subprocess.Popen('tetrisGame.exe',stdout=subprocess.PIPE,bufsize=1,universal_newlines=True)
        self.input_queue            = queue.Queue()
        self.input_thread           = threading.Thread(target=self.add_input, args=(self.input_queue,))
        self.input_thread.daemon    = True
        self.input_thread.start()

    def getLine(self):
        if not self.input_queue.empty():
            line    = self.input_queue.get()
            return line
        return None

class Bitmap:
    def __init__(self,height,width,fileName=None):
        self.height     = height
        self.width      = width
        self.fileName   = fileName
        self.prv        = [1] * (self.height*self.width)
        self.pos        = 0
        if self.fileName is not None:
            self.data   = Path(fileName).read_bytes()
        else:
            self.nb     = NoBlock()
            self.re     = re.compile(r'^(\d+):(\d+)$')
            self.y      = 0
            self.bm     = []

    def get(self):
        if self.fileName is not None:
            if self.pos >= len(self.data): self.pos = 0
        
            bitmap = []
            for y in range(self.height):
                for x in range(self.width):
                    if self.pos >= len(self.data):  bitmap.append(0)
                    else:                           bitmap.append(self.data[self.pos])
                    self.pos += 1
            return bitmap
        else:
            line        = self.nb.getLine()
            if line is None: return None
            #print(f'@@@DBG: line={line}')
            m       = self.re.match(line)
            if m is None: return None
            y       = int(m.group(1))
            if y != self.y:
                self.bm = []
                self.y  = 0
                return None

            for itm in m.group(2):
                self.bm.append(int(itm))

            self.y += 1
            if self.y == self.height:
                self.pos += 1
                print(f"@@@DBG: return BM {self.pos}")
                bm      = self.bm
                self.bm = []
                self.y  = 0
                return bm
            else:
                return None

    def draw(self,bm):
        i = 0
        for y in range(height):
            for x in range(width):
                if self.prv[i] != bm[i]:
                    window[f'{y},{x}'].Update(button_color=colors[bm[y*width+x]])
                i += 1
        self.prv = bm.copy()

def T(key, text=None, color='white', size=(None, None)):
    if text == None:
        text = ' '*2
    return sg.Text(text, key=key, pad=(1,1), size=size, justification='center',
        font=font, background_color=bg, text_color=color)

def M(text, bg='green'):
    return sg.Text(text, font=font, size=(16, 1), justification='center',
        background_color=bg, text_color='white')

def B(text, key, color=bg, width=16):
    return sg.Button(text, font=font, size=(width, 1), key=key,
        bind_return_key=False, focus=False,pad=((0,0),(0,0)))

layout1     = []
for y in range(height):
    row     = []
    for x in range(width):
        nam     = f'{y},{x}'
        row.append(B('  ',key=nam,color=bg,width=2))
    layout1.append(row)

layout2 = [[M('Score')], [T('Score', text='000000', size=(16, 1))],
           [M('', bg=bg)],
           [M('Level')], [T('Level', text='00', size=(16, 1))],
           [M('', bg=bg)],
           [M('a:Move Left')], [M('s:Move Down')], [M('d:Move Right')],
           [M('w:Rotate')], [M('l:Loop')],
           [M(' ', bg=bg)], [M(' ', bg=bg)],
           [B('New Game', 'New')], [B('Game Pause', 'Pause')],
           [B('Game Over', 'Over')]]
           
frame1 = sg.Frame('', layout=layout1, background_color=bg,
                  border_width=5)

frame2 = sg.Frame('', layout=layout2, background_color=bg,
                 border_width=5, size=(None, height*32))

layout = [[frame1, frame2]]

window = sg.Window('Tetris Game', layout=layout, finalize=True,
                   use_default_focus=False, return_keyboard_events=True,
                   background_color=bg)


# Bitmap input or pipe
#bm  = Bitmap(height,width,'./tetris.bm')
bm  = Bitmap(height,width)

nb  = NoBlock()

while True:
    bitmap  = bm.get()
    if bitmap != None: bm.draw(bitmap)

    event, values = window.read(timeout=1)

    if event in [None, 'Over']:
        break

window.close()
