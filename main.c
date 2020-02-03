#include "tetris.h"
#include <stdio.h>
#include <stdlib.h>

#include "alta_gpio.h"

int
main(void)
{
    set_gpio_direction(GPIO_PIN6_VAL, GPIO_OUTPUT);

    set_gpio(GPIO_PIN6_OFFSET, GPIO_PIN6_VAL);
    clear_gpio(GPIO_PIN6_OFFSET);
    set_gpio(GPIO_PIN6_OFFSET, GPIO_PIN6_VAL);

    tetris_run(GAME_WIDTH, GAME_HEIGHT);
    return EXIT_SUCCESS;
}

/*

game loop runs as follows

tetris_gravity
    bumps the y value
    check for collision






*/
