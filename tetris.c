#include "tetris.h"
#include "randoms.h"
#include <stdbool.h>
#include <stdlib.h>

static volatile int count;

#ifdef ARM
#include "ARMCM0plus.h"
#include "SEGGER_RTT.h"


#else //DESKTOP

#include <stdio.h>
#include <stdarg.h>
#include <conio.h>
#include <synchapi.h>
#include <windows.h>
#include <wchar.h>

// Windows VT100 handling
#define ENABLE_VIRTUAL_TERMINAL_PROCESSING 4

void setVT100() {
    HANDLE hOut     = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwMode    = 0;
    GetConsoleMode(hOut, &dwMode);
    dwMode         |= ENABLE_VIRTUAL_TERMINAL_PROCESSING;
    SetConsoleMode(hOut, dwMode);
}

int SEGGER_RTT_HasData(int x) { return kbhit(); }
void SEGGER_RTT_printf(int x,char* fmt,...) { 
    va_list args;
    va_start (args, fmt);
    vprintf (fmt, args);
    va_end (args);
}
size_t SEGGER_RTT_Read(int offset,char* buf,int bufSiz) {
    *buf = getch();
    return 1;
}
void SEGGER_RTT_WriteString(int x,char* y) { printf("%s", y); }
void __disable_irq() { }
void __enable_irq() { }
void SEGGER_RTT_Init() { }

int tickConfig = 10000;
void SysTick_Config(int x) { tickConfig = x; }

void __WFI() {
    SleepEx(1,false);
    if (tickConfig >= 10000) count += 10;
    else                     count += 50;
}

#endif

#define ASSERT(x)                                                              \
    do {                                                                       \
        if (!(x)) {                                                            \
            SEGGER_RTT_printf(0, "assert failed! %s %d\n", __FUNCTION__, __LINE__);          \
            while (1)                                                          \
                ;                                                              \
        }                                                                      \
    } while (0)

/* Some cursor functions */
// static inline void move_cursor_up(int n) { printf("\033[%dA", n); }
// static inline void move_cursor_down(int n) { printf("\033[%dB", n); }
// static inline void move_cursor_left(int n) { printf("\033[%dC", n); }
// static inline void move_cursor_right(int n) { printf("\033[%dD", n); }

// move the cursor to line L column C
static inline void
move_cursor(int L, int C)
{
    SEGGER_RTT_printf(0, "\033[%d;%dH", L, C);
}

static inline void
clear_screen(void)
{
    SEGGER_RTT_WriteString(0, "\033[2J");
}

#define COLOR_STR "\033[%dm"
#define END_FMT "\033[0m"

struct tetris_level
{
    int score;
    int nsec;
};

struct tetris_block blocks[] = {
    { { "##", "##" }, 2, 2, NONE },       { { " X ", "XXX" }, 3, 2, NONE },
    { { "@@@@" }, 4, 1, NONE },           { { "OO", "O ", "O " }, 2, 3, NONE },
    { { "&&", " &", " &" }, 2, 3, NONE }, { { "ZZ ", " ZZ" }, 3, 2, NONE }
};

struct tetris_level levels[] = { { 0, 1200000 },    { 1500, 900000 },
                                 { 8000, 700000 },  { 20000, 500000 },
                                 { 40000, 400000 }, { 75000, 300000 },
                                 { 100000, 200000 } };

#define TETRIS_PIECES (sizeof(blocks) / sizeof(struct tetris_block))
#define TETRIS_LEVELS (sizeof(levels) / sizeof(struct tetris_level))

void
tetris_init(struct tetris* t, int w, int h)
{
    int x, y;
    t->level = 1;
    t->score = 0;
    t->gameover = 0;
    t->w = w;
    t->h = h;
    for (x = 0; x < w; x++) {
        for (y = 0; y < h; y++)
            t->game[x][y] = (tile){ ' ', NONE };
    }
}

void
tetris_print(struct tetris* t)
{
    int x, y;
    move_cursor(0, 0);

    SEGGER_RTT_printf(0, "[LEVEL: %d | SCORE: %d]\n", t->level, t->score);

    for (y = 0; y < t->h; y++) {
        SEGGER_RTT_WriteString(0, "!");
        for (x = 0; x < t->w; x++) {
            if (x >= t->x && y >= t->y && x < (t->x + t->current.w) &&
                y < (t->y + t->current.h) &&
                t->current.data[y - t->y][x - t->x] != ' ')
                SEGGER_RTT_printf(0, COLOR_STR "[]" END_FMT, t->current.color);
            else {
                if (t->game[x][y].val != ' ') {
                    ASSERT(t->game[x][y].color != NONE);
                    SEGGER_RTT_printf(0, COLOR_STR "[]" END_FMT, t->game[x][y].color);
                } else {
                    SEGGER_RTT_WriteString(0, "  ");
                }
            }
        }
        SEGGER_RTT_WriteString(0, "!\n");
    }
    for (x = 0; x < 2 * t->w + 2; x++)
        SEGGER_RTT_WriteString(0, "~");
    SEGGER_RTT_WriteString(0, "\n");
}

int
tetris_hittest(struct tetris* t)
{
    int x, y, X, Y;
    struct tetris_block b = t->current;
    for (x = 0; x < b.w; x++)
        for (y = 0; y < b.h; y++) {
            X = t->x + x;
            Y = t->y + y;
            if (X < 0 || X >= t->w)
                return 1;
            if (b.data[y][x] != ' ') {
                if ((Y >= t->h) || (X >= 0 && X < t->w && Y >= 0 &&
                                    t->game[X][Y].val != ' ')) {
                    return 1;
                }
            }
        }
    return 0;
}

void
tetris_new_block(struct tetris* t)
{
    t->current = blocks[RANDOM()];
    t->x = (t->w / 2) - (t->current.w / 2);
    t->y = 0;
    t->current.color = RED + RANDOM();
    ASSERT(t->current.color < NONE);
    if (tetris_hittest(t)) {
        t->gameover = 1;
    }
}

void
tetris_print_block(struct tetris* t)
{
    int x, y;
    struct tetris_block b = t->current;
    for (x = 0; x < b.w; x++)
        for (y = 0; y < b.h; y++) {
            if (b.data[y][x] != ' ')
                t->game[t->x + x][t->y + y] = (tile){ b.data[y][x], b.color };
        }
}

void
tetris_rotate(struct tetris* t)
{
    struct tetris_block b = t->current;
    struct tetris_block s = b;
    int x, y;
    b.w = s.h;
    b.h = s.w;
    for (x = 0; x < s.w; x++)
        for (y = 0; y < s.h; y++) {
            b.data[x][y] = s.data[s.h - y - 1][x];
        }
    x = t->x;
    y = t->y;
    t->x -= (b.w - s.w) / 2;
    t->y -= (b.h - s.h) / 2;
    t->current = b;
    if (tetris_hittest(t)) {
        t->current = s;
        t->x = x;
        t->y = y;
    }
}

void
tetris_gravity(struct tetris* t)
{
    t->y++;
    if (tetris_hittest(t)) {
        t->y--;
        tetris_print_block(t);
        tetris_new_block(t);
    }
}

void
tetris_fall(struct tetris* t, int l)
{
    int x, y;
    for (y = l; y > 0; y--) {
        for (x = 0; x < t->w; x++)
            t->game[x][y] = t->game[x][y - 1];
    }
    for (x = 0; x < t->w; x++)
        t->game[x][0].val = ' ';
}

void
tetris_check_lines(struct tetris* t)
{
    int x, y, l;
    int p = 100;
    for (y = t->h - 1; y >= 0; y--) {
        l = 1;
        for (x = 0; x < t->w && l; x++) {
            if (t->game[x][y].val == ' ') {
                l = 0;
            }
        }
        if (l) {
            t->score += p;
            p *= 2;
            tetris_fall(t, y);
            y++;
        }
    }
}

// called by the Systick timer.
void
SysTick_Handler(void)
{
    count++;
}

int
tetris_level(struct tetris* t)
{
    for (size_t i = 0; i < TETRIS_LEVELS; i++) {
        if (t->score >= levels[i].score) {
            t->level = i + 1;
        } else
            break;
    }
    return levels[t->level - 1].nsec;
}

void exeCmd(char chr,struct tetris* t,bool* moved,bool* loop) {
    switch (chr) {
        case 'a':
            *moved = true;
            t->x--;
            if (tetris_hittest(t))
                t->x++;
            return;
        case 'd':
            *moved = true;
            t->x++;
            if (tetris_hittest(t))
                t->x--;
            return;
        case 's':
            *moved = true;
            tetris_gravity(t);
            return;
        case 'w':
            *moved = true;
            tetris_rotate(t);
            return;
        case 'l': // Loop execution
            *loop = true;
            SysTick_Config(2000);
            return;
    }
}

#define BUF_SIZE 512
void
tetris_run(int w, int h)
{
    struct tetris t;
    count = 0;
    bool moved = false;
    bool loop  = false;

#ifndef ARM
    setVT100();
#endif

    SEGGER_RTT_Init();
    __enable_irq();
    SysTick_Config(10000);

    do {
        tetris_init(&t, w, h);

        tetris_new_block(&t);
        clear_screen();

        while (!t.gameover) {
            __WFI();

            if (count == 100 || count == 200) {
                if (moved) {
                    tetris_print(&t);
                    moved = false;
                }
            }
            if (count == 300) {
                tetris_gravity(&t);
                tetris_check_lines(&t);
                __disable_irq();
                count = 0;
                __enable_irq();
                tetris_print(&t);
            }

            const char cmds[] = {'a','w','d','a','d','s'};

            if (loop && count % 100 == 0) {
                char cmd = cmds[RANDOM()];
                exeCmd(cmd,&t,&moved,&loop);
            }

            if (SEGGER_RTT_HasData(0)) {
                char buf[BUF_SIZE];
                size_t n = SEGGER_RTT_Read(0, (char*)buf, BUF_SIZE);
                for (size_t i = 0; i < n; i++) {
                    exeCmd(buf[i],&t,&moved,&loop);
            }
        }

        tetris_print(&t);
        SEGGER_RTT_WriteString(0, "*** GAME OVER ***\n");
        }
    } while (loop);
}
