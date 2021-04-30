ifeq ($(OS),Windows_NT)     # is Windows_NT on XP, 2000, 7, Vista, 10...
    detected_OS := Windows
else
    detected_OS := $(shell uname)  # same as "uname -s"
endif


default:
	make deps && make $(detected_OS)

deps:
	pip install -r requirements.txt

Windows:
	pyinstaller --distpath=./dist/$(detected_OS) --icon=./assets/instabot_white_bg.png -c --onedir -n instabot instabot/__main__.py

Darwin:
	pyinstaller --distpath=./dist/$(detected_OS) --icon=./assets/instabot.png -c --onefile -n instabot instabot/__main__.py

Linux:
	pyinstaller --distpath=./dist/$(detected_OS) --icon=./assets/instabot.png -c -n instabot --onefile instabot/__main__.py

clear:
	rm -r build/ dist/ instabot.spec

all:
	make run windows
	make run mac
	make run linux