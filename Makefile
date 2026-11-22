.PHONY: build serve publish clean

build:
	python tools/build_calendar.py
	pelican content -s pelicanconf.py -o output

serve: build
	pelican --listen -o output

publish:
	python tools/build_calendar.py
	pelican content -s publishconf.py -o output

clean:
	rm -rf output
