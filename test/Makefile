BUILD_SUPPORT=build_support.py

support: $(BUILD_SUPPORT)
	python $(BUILD_SUPPORT)

.PHONY: test
test: support
	python -m unittest -v

.PHONY: clean
clean:
	$(RM) -f support.*
	$(RM) -rf __pycache__
