#
# Makefile
# Malcolm Ramsay, 2018-04-11 11:23
#
build_dir = build

all: $(build_dir)
	cd $(build_dir); cmake .. -DENABLE_CUDA=False
	$(MAKE) -C $(build_dir)

install: all
	$(MAKE) -C $(build_dir) install

clean:
	rm -rf $(build_dir)

test: install
	pytest

debug: $(build_dir)
	cd $(build_dir); cmake .. -DENABLE_CUDA=False -DCMAKE_BUILD_TYPE=DEBUG
	$(MAKE) -C $(build_dir) install


$(build_dir):
	mkdir -p $@



# vim:ft=make
#
