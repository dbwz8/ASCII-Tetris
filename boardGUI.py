import PySimpleGUI as sg

width   = 12
height  = 15
font    = ('Courier New', 16)
bg      = 'gray'

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
for i in range(height):
    row     = []
    for j in range(width):
        nam     = f'{i},{j}'
        row.append(B('  ',nam,color=bg,width=2))
    layout1.append(row)

layout2 = [[M('Score')], [T('Score', text='000000', size=(16, 1))],
           [M('', bg=bg)],
           [M('Level')], [T('Level', text='00', size=(16, 1))],
           [M('', bg=bg)],
           [M('Left:Move Left')], [M('Right:Move Right')], [M('Down:Move Down')],
           [M('Up:Rotate')], [M('Space:Drop')], [M('ESC:Pause')],
           [M('', bg=bg)], [M(' ', bg=bg)],
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
while True:

    event, values = window.read(timeout=10)

    if event in [None, 'Over']:
        break

window.close()
