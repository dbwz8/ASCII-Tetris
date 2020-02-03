#pragma once
#include <stdint.h>
#include <stdlib.h>
#include <ARMCM0plus.h>


/*
  ARM AHB GPIO Peripheral Device.
  See Section A.1 of the Integration Guide
 */
typedef struct
{
    __IO uint8_t  DATA [1024];
    __IO uint32_t DIR;
    __IO uint32_t RESERVED[3];
    __IO uint32_t IE;
} alta_gpio_t;


/******************************************************************************/
/*                         Peripheral memory map                              */
/******************************************************************************/
/* Peripheral and SRAM base address */
#define SRAM_BASE        ((uint32_t)0x20000000)
#define PERIPH_BASE      ((uint32_t)0x40000000)

/* Peripheral memory map */
#define GPIO_BASE        PERIPH_BASE

#define GPIO0_BASE       (GPIO_BASE)

/******************************************************************************/
/*                         Peripheral declaration                             */
/******************************************************************************/
#define GPIO0            ((alta_gpio_t *) GPIO0_BASE)

/* GPIO Definitions
   - The GPIO Driver on Alta has a slightly confusing bit set
   and bit clear functionality.
   The range between 0x40000000-0x400003ff is used to write to the
   GPIO Data register. The bottom two bits of the address chose which
   byte of the DATA register is being addressed. The bits 9:2 apply
   a mask which is combined with the data byte being written to set
   or clear a particular bit.
   Eg: Set bit 9 by writing 0x02 to 0x40000009
   Set bit 0 by writing 0x01 to 0x40000040
 */

#define GPIO_PIN0_OFFSET (0x04)
#define GPIO_PIN0_VAL    (0x01)

#define GPIO_PIN1_OFFSET (0x08)
#define GPIO_PIN1_VAL    (0x02)

#define GPIO_PIN2_OFFSET (0x10)
#define GPIO_PIN2_VAL    (0x04)

#define GPIO_PIN3_OFFSET (0x20)
#define GPIO_PIN3_VAL    (0x08)

#define GPIO_PIN4_OFFSET (0x40)
#define GPIO_PIN4_VAL    (0x10)

#define GPIO_PIN5_OFFSET (0x80)
#define GPIO_PIN5_VAL    (0x20)

#define GPIO_PIN6_OFFSET (0x100)
#define GPIO_PIN6_VAL    (0x40)

#define GPIO_PIN7_OFFSET (0x200)
#define GPIO_PIN7_VAL    (0x80)

typedef enum {
              GPIO_INPUT = 0,
              GPIO_OUTPUT,
} GPIO_DIRECTION;

/* Set a single pin to input/output */
static inline void
set_gpio_direction(uint32_t pin, GPIO_DIRECTION direction)
{
    if (direction == GPIO_OUTPUT)
        GPIO0->DIR |= pin;
    else
        GPIO0->DIR &= ~(pin);
}

/* Write directly to the direction register */
static inline void
set_gpio_direction_all(uint32_t state)
{
    GPIO0->DIR = state;
}

/* Set a single pin to high/low */
static inline void
set_gpio(size_t offset, uint8_t value)
{
    GPIO0->DATA[offset] = value;
}

static inline void
clear_gpio(size_t offset)
{
    GPIO0->DATA[offset] = 0;
}

/* Write to all the GPIO pins */
static inline void
set_gpio_all(uint32_t state)
{
    __IO uint32_t *GPIO0_BASE_PTR = (uint32_t *)GPIO_BASE;
    *GPIO0_BASE_PTR = state;
}

/* Read A single gpio pin */
static inline uint8_t
read_gpio(size_t offset)
{
    return GPIO0->DATA[offset];
}

/* Read All the GPIO Pins */
static inline uint32_t
read_gpio_all(void)
{
    __IO uint32_t *GPIO0_BASE_PTR = (uint32_t *)GPIO_BASE;
    return *GPIO0_BASE_PTR;
}
