/*
* Copyright (c) 2015-17 Luke Montalvo <lukemontalvo@gmail.com>
*
* This file is part of BEE.
* BEE is free software and comes with ABSOLUTELY NO WARANTY.
* See LICENSE for more details.
*/

// BEEF auto-generated the below code and will overwrite all changes

#ifndef RES_{capname}
#define RES_{capname} 1

#include "../../bee/util.hpp"
#include "../../bee/all.hpp"

#include "../resources.hpp"

#include "{name}.hpp"

{roomname}::{roomname}() : Room("{roomname}", "{name}.hpp") {{}}
void {roomname}::init() {{
	Room::init();
	
	set_width({width});
	set_height({height});
	
	get_phys_world()->set_gravity(btVector3(0.0, {gravity}, 0.0));
	get_phys_world()->set_scale(100.0);
	
	if (get_instance_map().empty()) {{
		set_instance_map("resources/rooms/{name}.csv");
	}}
	load_instance_map();
}}
{events}

#endif // RES_{capname}_H
