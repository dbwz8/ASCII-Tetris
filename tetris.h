#pragma once

#define GAME_WIDTH 12
#define GAME_HEIGHT 15

typedef enum color_t
{
    RED = 41,
    GREEN,
    YELLOW,
    BLUE,
    MAGENTA,
    CYAN,
    NONE,
} color_t;

typedef struct tile
{
    char val;
    color_t color;
} tile;

struct tetris
{
    tile game[GAME_WIDTH][GAME_HEIGHT];
    int w;
    int h;
    int level;
    int gameover;
    int score;
    struct tetris_block
    {
        char data[5][5];
        int w;
        int h;
        color_t color;
    } current;
    int x;
    int y;
};

void
tetris_cleanup_io();

void
tetris_signal_quit(int);

void
tetris_set_ioconfig();

void
tetris_init(struct tetris* t, int w, int h);

void
tetris_print(struct tetris* t);

void
tetris_run(int width, int height);

void
tetris_new_block(struct tetris* t);

void
tetris_new_block(struct tetris* t);

void
tetris_print_block(struct tetris* t);

void
tetris_rotate(struct tetris* t);

void
tetris_gravity(struct tetris* t);

void
tetris_fall(struct tetris* t, int l);

void
tetris_check_lines(struct tetris* t);

int
tetris_level(struct tetris* t);
