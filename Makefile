#
# Makefile
# Malcolm Ramsay, 2018-04-11 11:23
#
build_dir = build

# Set shell to bash to allow module command
SHELL:=/bin/bash

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

conda-build:
	module load gcc/4.8.4 cuda/8.0.44 && export CC=/usr/local/gcc/4.8.4/bin/gcc
	conda build .

$(build_dir):
	mkdir -p $@


.PHONY: test clean conda-build

# vim:ft=make
#
