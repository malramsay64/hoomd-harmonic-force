#
# Makefile
# Malcolm Ramsay, 2018-04-11 11:23
#
build_dir = build

all: $(build_dir)
	cd $(build_dir); cmake .. -DENABLE_CUDA=True
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
