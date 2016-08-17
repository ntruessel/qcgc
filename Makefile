CFLAGS=-Wall -Wextra -std=gnu99 -Wmissing-declarations -Wmissing-prototypes
SRC=qcgc.c arena.c allocator.c bag.c event_logger.c gray_stack.c
LDFLAGS=-lrt

lib: $(SRC)
	$(CC) $(CFLAGS) -fpic -shared -o qcgc.so $^ $(LDFLAGS)

support:
	cd test && make $@

.PHONY: test
test:
	cd test && make $@

.PHONY: doc
doc:
	doxygen Doxyfile

.PHONY: clean
clean:
	$(RM) -f *.so *.o *.gcov *.gcda *.gcno
	$(RM) -rf doc
	cd test && make $@
