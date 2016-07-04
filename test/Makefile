support: build_support.py
	python3 $^

.PHONY: test
test: support
	python3 test.py

.PHONY: clean
clean:
	$(RM) -f support.* *.gcov
	$(RM) -rf __pycache__
	$(RM) -rf runner/__pycache__
