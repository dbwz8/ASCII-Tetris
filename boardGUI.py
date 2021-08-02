import sys
import msvcrt
from tkinter.constants import S
import PySimpleGUI as sg
from pathlib import Path

width   = 12
height  = 15
font    = ('Courier New', 16)
bg      = 'gray'
colors  = [bg, 'gold', 'blue', 'tomato', 'red', 'green', 'purple', 'brown']

class AccumLine:
    def __init__(self):
        self.line             = ''
    def get(self):
        if msvcrt.kbhit():
            chr         = str(msvcrt.getch(),'UTF-8')
            self.line  += chr
            if chr =='\n': 
                line        = self.line
                self.line   = ''
                return line
        return None

class Bitmap:
    def __init__(self,height,width,fileName):
        self.height = height
        self.width  = width
        self.data   = Path(fileName).read_bytes()
        self.pos    = 0
        self.prv    = [1] * (self.height*self.width)

    def get(self):
        if self.pos >= len(self.data): self.pos = 0
        
        bitmap = []
        for y in range(self.height):
            for x in range(self.width):
                if self.pos >= len(self.data):  bitmap.append(0)
                else:                           bitmap.append(self.data[self.pos])
                self.pos += 1

        return bitmap

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


bm  = Bitmap(height,width,'./tetris.bm')
al  = AccumLine()

while True:
    bm.draw(bm.get())
    #line    = al.get()
    #if line: print(f"Got Line: {line}")

    event, values = window.read(timeout=1)

    if event in [None, 'Over']:
        break

window.close()
