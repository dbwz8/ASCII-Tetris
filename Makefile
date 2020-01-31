EXE=Tetris
OBJECTS=main.o tetris.o
CC=gcc
FLAGS=-I./ -O3 -Wall -Wpedantic -Werror -flto

$(EXE): $(OBJECTS)
	$(CC) $(FLAGS) $(OBJECTS) -o $(EXE)

%.o: %.c
	$(CC) $(FLAGS) -c $< -o $@

clean:
	rm -f Tetris *.o
