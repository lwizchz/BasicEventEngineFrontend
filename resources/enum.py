# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

class ELight:
	AMBIENT = 1
	DIFFUSE = 2
	POINT = 3
	SPOT = 4

class ECompile:
	DEBUG = 0
	RELEASE = 1

class EEvent:
	_events = [
		"Update",
		"Create",
		"Destroy",
		"Alarm",
		"Step Begin",
		"Step Mid",
		"Step End",
		"Keyboard Press",
		"Mouse Press",
		"Keyboard Input",
		"Mouse Input",
		"Keyboard Release",
		"Mouse Release",
		"Controller Axis",
		"Controller Press",
		"Controller Release",
		"Controller Modify",
		"Commandline Input",
		"Path End",
		"Outside Room",
		"Intersect Boundary",
		"Collision",
		"Check Collision Filter",
		"Draw",
		"Animation End",
		"Room Start",
		"Room End",
		"Game Start",
		"Game End",
		"Window",
		"Network"
	]
	@staticmethod
	def get(index):
		return EEvent._events[index]
	@staticmethod
	def getIndex(event):
		return EEvent._events.index(event)
	@staticmethod
	def getParams(event):
		if event == "Update":
			return "bee::Instance* self"
		elif event == "Create":
			return "bee::Instance* self"
		elif event == "Destroy":
			return "bee::Instance* self"
		elif event == "Alarm":
			return "bee::Instance* self, size_t alarm"
		elif event == "Step Begin":
			return "bee::Instance* self"
		elif event == "Step Mid":
			return "bee::Instance* self"
		elif event == "Step End":
			return "bee::Instance* self"
		elif event == "Keyboard Press":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Mouse Press":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Keyboard Input":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Mouse Input":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Keyboard Release":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Mouse Release":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Controller Axis":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Controller Press":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Controller Release":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Controller Modify":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Commandline Input":
			return "bee::Instance* self, const std::string& input"
		elif event == "Path End":
			return "bee::Instance* self"
		elif event == "Outside Room":
			return "bee::Instance* self"
		elif event == "Intersect Boundary":
			return "bee::Instance* self"
		elif event == "Collision":
			return "bee::Instance* self, bee::Instance* other"
		elif event == "Check Collision Filter":
			return "const bee::Instance* self, const bee::Instance* other"
		elif event == "Draw":
			return "bee::Instance* self"
		elif event == "Animation End":
			return "bee::Instance* self"
		elif event == "Room Start":
			return "bee::Instance* self"
		elif event == "Room End":
			return "bee::Instance* self"
		elif event == "Game Start":
			return "bee::Instance* self"
		elif event == "Game End":
			return "bee::Instance* self"
		elif event == "Window":
			return "bee::Instance* self, SDL_Event* e"
		elif event == "Network":
			return "bee::Instance* self, const NetworkEvent& e"
	@staticmethod
	def getParamTypes(event):
		params = EEvent.getParams(event)
		params = params.split(",")
		return ", ".join([p.rpartition(" ")[0] for p in params])
