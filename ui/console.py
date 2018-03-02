# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

try:
	import wx
except ImportError:
	raise ImportError("The wxPython module is required to run this program")

import sys
import subprocess
import threading
import queue

from ui.editor import BEEFEditor

class BashThread(threading.Thread):
	def __init__(self, readline):
		threading.Thread.__init__(self)

		self.readline = readline
		self.output = queue.Queue()

		self.stop_event = threading.Event()
		self.setDaemon(True)
	def run(self):
		while not self.stopped():
			line = self.readline()
			self.output.put(line)
	def stop(self):
		self.stop_event.set()
	def stopped(self):
		return self.stop_event.is_set()
	def getOutput(self):
		lines = []
		while True:
			try:
				line = self.output.get_nowait()
				lines.append(line.decode())
			except queue.Empty:
				break
		return "".join(lines)

class BashInterpreter:
	def __init__(self, output, wd, command=None):
		self.output = output

		self.wd = wd

		cmd = ["bash"]
		if command:
			cmd = command
			self.output.writeOut("> " + " ".join(command) + "\n")
		self.bash = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.wd)

		self.outThread = BashThread(self.bash.stdout.readline)
		self.outThread.start()

		self.errorThread = BashThread(self.bash.stderr.readline)
		self.errorThread.start()
	def run(self, command):
		if command.strip():
			self.bash.stdin.write((command+"\n").encode())
			self.bash.stdin.flush()
			self.output.writeOut("> " + command + "\n")

		while self.bash.poll() is None:
			self.output.writeOut(self.outThread.getOutput())
			self.output.writeErr(self.errorThread.getOutput())

		return self.bash.returncode
	def cleanup(self):
		self.outThread.stop()
		self.errorThread.stop()

		self.outThread.join()
		self.errorThread.join()

class BEEFConsole(wx.Dialog):
	def __init__(self, top, parent, wd):
		wx.Dialog.__init__(self)
		self.top = top
		self.wd = wd
		self.isShown = False

		display = wx.GetDisplaySize().Get()
		size = (850, 400)

		self.Create(parent, -1, "Compile Log", (display[0]-size[0], display[1]-size[1]), size)

		sizer = wx.BoxSizer(wx.VERTICAL)

		self.log = BEEFEditor(self, size=size)
		self.log.SetMarginType(1, 0)
		self.log.SetMarginWidth(1, 0)
		self.log.SetEdgeMode(wx.stc.STC_EDGE_NONE)
		sizer.Add(self.log, 0, wx.ALL, 5)

		self.SetSizer(sizer)
		sizer.Fit(self)

		self.Bind(wx.EVT_CLOSE, self.toggle)

	def clear(self):
		self.log.SetText("")
	def show(self, s=True):
		self.isShown = s
		self.Show(self.isShown)
		self.top.toolbar.ToggleTool(70, self.isShown)
	def toggle(self, event=None):
		self.isShown = not self.isShown
		self.Show(self.isShown)
		self.top.toolbar.ToggleTool(70, self.isShown)

	def update(self):
		self.log.DocumentEnd()
		self.log.SetMarginType(1, 0)
		self.log.SetMarginWidth(1, 0)

		self.Refresh()
		self.Update()
	def writeOut(self, s):
		if s:
			self.log.AppendText(s)
			self.update()
	def writeErr(self, s):
		if s:
			self.log.AppendText(s)
			self.update()

	def call(self, cmd):
		shell = BashInterpreter(self, self.wd, cmd)
		r = shell.run("")
		shell.cleanup()
		return r
