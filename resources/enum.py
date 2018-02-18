# Copyright (c) 2017-18 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEEF.
# BEEF is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

class EResource:
	TEXTURE = 0
	SOUND = 1
	FONT = 2
	PATH = 3
	TIMELINE = 4
	MESH = 5
	LIGHT = 6
	OBJECT = 7
	ROOM = 8
	_MAX = 9

	@staticmethod
	def get(type):
		if type == EResource.TEXTURE:
			return "Texture"
		elif type == EResource.SOUND:
			return "Sound"
		elif type == EResource.FONT:
			return "Font"
		elif type == EResource.PATH:
			return "Path"
		elif type == EResource.TIMELINE:
			return "Timeline"
		elif type == EResource.MESH:
			return "Mesh"
		elif type == EResource.LIGHT:
			return "Light"
		elif type == EResource.OBJECT:
			return "Object"
		elif type == EResource.ROOM:
			return "Room"
	@staticmethod
	def getPlural(type):
		if type == EResource.MESH:
			return "Meshes"
		else:
			return EResource.get(type) + "s"
	@staticmethod
	def getAll():
		return range(0, EResource._MAX)

class EFontStyle:
	NORMAL = 0
	BOLD = 1
	ITALIC = 2
	UNDERLINE = 3
	STRIKETHROUGH = 4
	_MAX = 5

	@staticmethod
	def str(type):
		if type == EFontStyle.NORMAL:
			return "NORMAL"
		elif type == EFontStyle.BOLD:
			return "BOLD"
		elif type == EFontStyle.ITALIC:
			return "ITALIC"
		elif type == EFontStyle.UNDERLINE:
			return "UNDERLINE"
		elif type == EFontStyle.STRIKETHROUGH:
			return "STRIKETHROUGH"
		return "NONE"

class ELight:
	AMBIENT = 1
	DIFFUSE = 2
	POINT = 3
	SPOT = 4
	_MAX = 5

	@staticmethod
	def str(type):
		if type == ELight.AMBIENT:
			return "AMBIENT"
		elif type == ELight.DIFFUSE:
			return "DIFFUSE"
		elif type == ELight.POINT:
			return "POINT"
		elif type == ELight.SPOT:
			return "SPOT"
		return "NONE"

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
