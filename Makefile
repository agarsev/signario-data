DATA:=videos
VID_IDS:=$(notdir $(wildcard $(DATA)/*))
VID_TARGET:=cuts # lowq.mp4 detected.txt

all: $(patsubst %,$(DATA)/%/$(VID_TARGET),$(VID_IDS))

$(DATA)/%/detected.txt: $(DATA)/%/raw.mp4 scripts/get_cut_times.py
	python3 scripts/get_cut_times.py $< >$@

$(DATA)/%/lowq.mp4: $(DATA)/%/raw.mp4
	-ffmpeg -loglevel error -stats -n \
		-i $< -an -vcodec libx264 \
		-vf crop=iw-480:ih,scale=640:480,fps=fps=25 \
		$@ || touch $@

$(DATA)/%/cuts: $(DATA)/%/lowq.mp4 $(DATA)/%/info.json scripts/cut_video.py
	python3 scripts/cut_video.py $@ $(@D)
