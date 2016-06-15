BUILD_SUPPORT=build_support.py

support: $(BUILD_SUPPORT)
	python $(BUILD_SUPPORT)

.PHONY: test
test: support
	python test.py

.PHONY: clean
clean:
	$(RM) -f support.*
	$(RM) -rf __pycache__
	$(RM) -rf runner/__pycache__
