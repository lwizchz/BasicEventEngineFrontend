Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>

BEEFrontend is the graphical editor for the
[BasicEventEngine](https://github.com/piluke/BasicEventEngine/), an
event-driven game engine under heavy development. The issue tracker for this
repository should only be used for bugs with the actual frontend, please direct
all engine bugs to the
[engine issue tracker](https://github.com/piluke/BasicEventEngine/issues/).

The software is in early alpha so do not expect any sort of stability. I'm
slowly adding more content to the wiki so be sure to check that out first but
if you still have any questions or comments, feel free to email me. Also feel
free to contribute to the engine code or make feature requests, preferably via
Github. And above all, report bugs! :)

## How to use

1. Install wxPython and optionally watchdog:

        sudo pip install wxpython watchdog

2. Download the BEE submodule:

        git submodule update --init --recursive

3. Open BEEF and add resources as needed (or try out an example):

        ./beef.py

4. Compile the project by selecting Build>Run

This project is under the MIT License so feel free to do basically whatever you
want with the code.
