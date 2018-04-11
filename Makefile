#
# Makefile
# Malcolm Ramsay, 2018-04-11 11:23
#
build_dir = build

all: $(build_dir)
	cd $(build_dir); cmake ..
	$(MAKE) -C $(build_dir)

install: build
	$(MAKE) -C $(build_dir)

clean:
	rm -rf $(build_dir)

$(build_dir):
	mkdir -p $@



# vim:ft=make
#
