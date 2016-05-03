CC=clang
CFLAGS=-Wall -Wextra
SRC=qcgc.c qcgc.h

lib: $(SRC)
	$(CC) $(CFLAGS) -fpic -shared -o qcgc.so $<

support:
	cd test && make $@

.PHONY: test
test:
	cd test && make $@

.PHONY: clean
clean:
	$(RM) -f qcgc.so qcgc.o
	cd test && make $@
