support: build_support.py
	python $^

.PHONY: test
test: support
	python test.py

.PHONY: clean
clean:
	$(RM) -f support.* *.gcov
	$(RM) -rf __pycache__
	$(RM) -rf runner/__pycache__
	$(RM) -f *.pyc
