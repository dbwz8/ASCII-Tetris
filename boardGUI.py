import PySimpleGUI as sg

width   = 12
height  = 15
font    = ('Courier New', 16)
bg      = 'gray'
colors  = [bg, 'gold', 'blue', 'tomato', 'red', 'green', 'purple', 'brown']

class Bitmap:
    def __init__(self,height,width):
        self.height = height
        self.width  = width
        self.row    = self.height-1
        self.base   = [ 
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,0,0,0,0,0,0,0,
            0,0,0,0,0,7,7,0,0,0,0,0,
            0,0,0,0,0,7,7,6,0,0,0,0,
            0,0,0,0,4,4,0,6,0,0,0,0,
            0,0,0,0,3,4,0,6,0,0,0,0,
            0,1,1,0,3,4,0,6,0,0,0,0,
            0,1,2,2,3,0,5,5,0,0,0,0,
            0,1,2,2,3,0,5,5,0,0,0,0,
            ]

    def get(self):
        self.row += 1
        if self.row > self.height-2: self.row = 0
        if self.row == 0: return self.base
        
        bitmap = self.base.copy()
        for x in range(self.width-4,self.width):
            bitmap[self.row*self.width+x] = 1
        bitmap[(self.row+1)*self.width+self.width-1] = 1
        return bitmap

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
def draw(bm):
    for y in range(height):
        for x in range(width):
            window[f'{y},{x}'].Update(button_color=colors[bm[y*width+x]])

bm  = Bitmap(height,width)

while True:
    draw(bm.get())
    event, values = window.read(timeout=300)

    if event in [None, 'Over']:
        break

window.close()
