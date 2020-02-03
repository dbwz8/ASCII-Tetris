#include "tetris.h"
#include <stdio.h>
#include <stdlib.h>

int
main(void)
{
    tetris_run(GAME_WIDTH, GAME_HEIGHT);
    return EXIT_SUCCESS;
}

/*

game loop runs as follows

tetris_gravity
    bumps the y value
    check for collision






*/
