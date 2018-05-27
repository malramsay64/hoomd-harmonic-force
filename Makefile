#
# Makefile
# Malcolm Ramsay, 2018-04-11 11:23
#
build_dir = build

# Check OS to determine if CUDA is enabled, defaults to True
CUDA_ENABLED=True
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
	CUDA_ENABLED=True
endif
ifeq ($(UNAME_S),Darwin)
	CUDA_ENABLED=False
endif

all: $(build_dir)
	cd $(build_dir); cmake .. -DENABLE_CUDA=$(CUDA_ENABLED)
	$(MAKE) -C $(build_dir)

install: all
	$(MAKE) -C $(build_dir) install

clean:
	rm -rf $(build_dir)

test:
	pytest


$(build_dir):
	mkdir -p $@


.PHONY: test clean

# vim:ft=make
#
