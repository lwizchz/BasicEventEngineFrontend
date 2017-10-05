# Copyright (c) 2017 Luke Montalvo <lukemontalvo@gmail.com>
#
# This file is part of BEE.
# BEE is free software and comes with ABSOLUTELY NO WARANTY.
# See LICENSE for more details.

import os
import errno

from resources.enum import ECompile

class Compiler:
	def __init__(self, top):
		self.top = top
		self.buildDir = "build"

	def compile(self, type):
		print("Generating {} resources...".format(self.top.gameCfg["game_name"]))
		self._createDir(self.buildDir)
		self._generate()

		if type == ECompile.DEBUG:
			print("Compiling {} in debug mode...".format(self.top.gameCfg["game_name"]))
		elif type == ECompile.RELEASE:
			print("Compiling {} in release mode...".format(self.top.gameCfg["game_name"]))
		else:
			print("Unknown compile type: {}".format(type))
	def run(self):
		print("Running {}...".format(self.top.gameCfg["game_name"]))
	def debug(self):
		print("Debugging {}...".format(self.top.gameCfg["game_name"]))
	def clean(self):
		print("Cleaning {}...".format(self.top.gameCfg["game_name"]))
	def package(self):
		print("Packaging {}...".format(self.top.gameCfg["game_name"]))

	def _createDir(self, path):
		try:
			os.makedirs(path)
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

	def _generate(self):
		self._generateObjects()
		self._generateRooms()
		self._generateResources()
		self._generateCMake()
	def _generateObjects(self):
		self._createDir(self.buildDir+"/objects")

		headerTemplate = ""
		with open("templates/object.hpp", "r") as headerTemplateFile:
			headerTemplate = headerTemplateFile.read()
		objTemplate = ""
		with open("templates/object.cpp", "r") as objTemplateFile:
			objTemplate = objTemplateFile.read()

		for o in self.top.objects:
			is_persistent = ""
			if o.properties["is_persistent"]:
				is_persistent = "this->set_is_persistent(true);"

			objHeader = headerTemplate.format(
				capname=o.name.upper(),
				objname=o.name.replace("_", " ").title().replace(" ", ""),
				events="\n\t\t".join(o.getEventHeaders())
			)
			obj = objTemplate.format(
				capname=o.name.upper(),
				name=o.name,
				objname=o.name.replace("_", " ").title().replace(" ", ""),
				implevents=",\n\t\t".join(o.getImplementedEvents()),
				is_persistent=is_persistent,
				events="\n".join(o.getEvents())
			)
			with open("{}/objects/{}.hpp".format(self.buildDir, o.name), "w") as objHeaderFile:
				objHeaderFile.write(objHeader)
			with open("{}/objects/{}.cpp".format(self.buildDir, o.name), "w") as objFile:
				objFile.write(obj)
	def _generateRooms(self):
		self._createDir(self.buildDir+"/rooms")

		headerTemplate = ""
		with open("templates/room.hpp", "r") as headerTemplateFile:
			headerTemplate = headerTemplateFile.read()
		roomTemplate = ""
		with open("templates/room.cpp", "r") as roomTemplateFile:
			roomTemplate = roomTemplateFile.read()

		for r in self.top.rooms:
			roomHeader = headerTemplate.format(
				capname=r.name.upper(),
				roomname=r.name.replace("_", " ").title().replace(" ", ""),
				events="\n\t\t".join(r.getEventHeaders())
			)
			room = roomTemplate.format(
				capname=r.name.upper(),
				name=r.name,
				roomname=r.name.replace("_", " ").title().replace(" ", ""),
				events="\n".join(r.getEvents())
			)
			with open("{}/rooms/{}.hpp".format(self.buildDir, r.name), "w") as roomHeaderFile:
				roomHeaderFile.write(roomHeader)
			with open("{}/rooms/{}.cpp".format(self.buildDir, r.name), "w") as roomFile:
				roomFile.write(room)
			with open("{}/rooms/{}.csv".format(self.buildDir, r.name), "w") as instanceFile:
				instanceFile.write("\n".join(r.getInstanceMap()))
	def _generateResources(self):
		resources = ""
		with open("templates/resources.hpp", "r") as resourcesTemplate:
			resources = resourcesTemplate.read()
		resources = resources.format(
			spriteDefines="\n".join(["bee::Sprite* {} = nullptr;".format(s.name) for s in self.top.sprites]),
			soundDefines="\n".join(["bee::Sound* {} = nullptr;".format(s.name) for s in self.top.sounds]),
			backgroundDefines="\n".join(["bee::Background* {} = nullptr;".format(b.name) for b in self.top.backgrounds]),
			fontDefines="\n".join(["bee::Font* {} = nullptr;".format(f.name) for f in self.top.fonts]),
			pathDefines="\n".join(["bee::Path* {} = nullptr;".format(p.name) for p in self.top.paths]),
			timelineDefines="\n".join(["bee::Timeline* {} = nullptr;".format(t.name) for t in self.top.timelines]),
			meshDefines="\n".join(["bee::Mesh* {} = nullptr;".format(m.name) for m in self.top.meshes]),
			lightDefines="\n".join(["bee::Light* {} = nullptr;".format(l.name) for l in self.top.lights]),
			objectDefines="\n".join(["bee::Object* {} = nullptr;".format(o.name) for o in self.top.objects]),
			roomDefines="\n".join(["bee::Room* {} = nullptr;".format(r.name) for r in self.top.rooms]),

			objectIncludes="\n".join(["#include \"objects/{}.hpp\"".format(o.name) for o in self.top.objects]),
			roomIncludes="\n".join(["#include \"rooms/{}.hpp\"".format(r.name) for r in self.top.rooms]),

			spriteInits="\n\t\t".join(["{name} = new Sprite(\"{name}\", \"{path}\");".format(name=s.name, path=s.name+".png") for s in self.top.sprites]),
			soundInits="\n\t\t".join(["{name} = new Sound(\"{name}\", \"{path}\", false);".format(name=s.name, path=s.name+".wav") for s in self.top.sounds]),
			backgroundInits="\n\t\t".join(["{name} = new Background(\"{name}\", \"{path}\");".format(name=b.name, path=b.name+".png") for b in self.top.backgrounds]),
			fontInits="\n\t\t".join(["{name} = new Font(\"{name}\", \"{path}\", {size}, false);".format(name=f.name, path=f.name+".ttf", size=f.properties["size"]) for f in self.top.fonts]),
			pathInits="\n\t\t".join(["{name} = new Path(\"{name}\", \"\");".format(name=p.name) for p in self.top.paths]),
			timelineInits="\n\t\t".join(["{name} = new Timeline(\"{name}\", \"\");".format(name=t.name) for t in self.top.timelines]),
			meshInits="\n\t\t".join(["{name} = new Mesh(\"{name}\", \"{path}\");".format(name=m.name, path=m.name+".obj") for m in self.top.meshes]),
			lightInits="\n\t\t".join(["{name} = new Light(\"{name}\", \"\");".format(name=l.name) for l in self.top.lights]),
			objectInits="\n\t\t".join(["{name} = new {objname}();".format(name=o.name, objname=o.name.replace("_", " ").title().replace(" ", "")) for o in self.top.objects]),
			roomInits="\n\t\t".join(["{name} = new {roomname}();".format(name=r.name, roomname=r.name.replace("_", " ").title().replace(" ", "")) for r in self.top.rooms]),

			spriteDeletes="\n\t".join(["DEL({});".format(s.name) for s in self.top.sprites]),
			soundDeletes="\n\t".join(["DEL({});".format(s.name) for s in self.top.sounds]),
			backgroundDeletes="\n\t".join(["DEL({});".format(b.name) for b in self.top.backgrounds]),
			fontDeletes="\n\t".join(["DEL({});".format(f.name) for f in self.top.fonts]),
			pathDeletes="\n\t".join(["DEL({});".format(p.name) for p in self.top.paths]),
			timelineDeletes="\n\t".join(["DEL({});".format(t.name) for t in self.top.timelines]),
			meshDeletes="\n\t".join(["DEL({});".format(m.name) for m in self.top.meshes]),
			lightDeletes="\n\t".join(["DEL({});".format(l.name) for l in self.top.lights]),
			objectDeletes="\n\t".join(["DEL({});".format(o.name) for o in self.top.objects]),
			roomDeletes="\n\t".join(["DEL({});".format(r.name) for r in self.top.rooms])
		)
		with open(self.buildDir+"/resources.hpp", "w") as resourcesFile:
			resourcesFile.write(resources)
	def _generateCMake(self):
		cmake = ""
		with open("templates/CMakeLists.txt", "r") as cmakeTemplate:
			cmake = cmakeTemplate.read()
		cmake = cmake.format(
			objects=" ".join(["objects/{}.cpp".format(obj.name) for obj in self.top.objects]),
			rooms=" ".join(["rooms/{}.cpp".format(room.name) for room in self.top.rooms])
		)
		with open(self.buildDir+"/CMakeLists.txt", "w") as cmakeFile:
			cmakeFile.write(cmake)
