EXE=Tetris
OBJECTS=main.o tetris.o
CC=gcc
FLAGS=-I./ -O3 -Wall -Werror -flto -g
#FLAGS=-I./ -O0 -Wall -Werror -g

$(EXE): $(OBJECTS)
	$(CC) $(FLAGS) $(OBJECTS) -o $(EXE)

%.o: %.c
	$(CC) $(FLAGS) -c $< -o $@

clean:
	rm -f Tetris *.o
