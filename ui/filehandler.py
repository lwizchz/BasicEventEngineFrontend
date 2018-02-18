# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	from watchdog.observers import Observer
	from watchdog.events import FileSystemEventHandler
except ImportError:
	raise ImportError("The watchdog module is required to run this program")

class BEEFFileHandler(FileSystemEventHandler):
	def __init__(self, top):
		FileSystemEventHandler.__init__(self)
		self.top = top
	def on_modified(self, event):
		if not self.top.ready:
			return

		p = event.src_path[len(self.top.rootDir):]
		r = self.top.getResourceFromPath(p)
		if r:
			if r.name in self.top.gameCfg["open_resources"]:
				#r.update()
				self.top.enqueue(lambda: r.update())
				#pass
