/*
* Copyright (c) 2015-18 Luke Montalvo <lukemontalvo@gmail.com>
*
* This file is part of BEE.
* BEE is free software and comes with ABSOLUTELY NO WARANTY.
* See LICENSE for more details.
*/

#ifndef RES
#define RES 1

#include "resources.hpp"

// BEEF auto-generated the below code and will overwrite all changes

// Define textures
bee::Texture* spr_none = nullptr;

{textureDefines}

// Define sounds
{soundDefines}

// Define fonts
{fontDefines}

// Define paths
{pathDefines}

// Define timelines
{timelineDefines}

// Define meshes
{meshDefines}

// Define lights
{lightDefines}

// Define objects
{objectDefines}

// Define rooms
{roomDefines}

// Include objects
{objectIncludes}

// Include rooms
{roomIncludes}

/*
* bee::init_resources() - Initialize all game resources
* ! Note that loading is not required at this stage, just initialization
*/
int bee::init_resources() {{
	try {{ // Catch any exceptions so that the engine can properly clean up
		// Init textures
		spr_none = new Texture("spr_none", "none.png");
			spr_none->load();

		{textureInits}

		// Init sounds
		{soundInits}

		// Init fonts
		{fontInits}

		// Init paths
		{pathInits}

		// Init timelines
		{timelineInits}

		// Init meshes
		{meshInits}

		// Init lights
		{lightInits}

		// Init objects
		{objectInits}

		// Init rooms
		{roomInits}

		is_initialized = true; // Set the engine initialization flag
	}} catch (...) {{
		return 1; // Return 1 if any errors are encountered
	}}

	return 0; // Return 0 on success
}}

#define DEL(x) if (x!=nullptr) {{delete x; x=nullptr;}}
/*
* bee::close_resources() - Destroy all game resources
*/
int bee::close_resources() {{
	// Destroy textures
	{textureDeletes}

	// Destroy sounds
	{soundDeletes}

	// Destroy fonts
	{fontDeletes}

	// Destroy paths
	{pathDeletes}

	// Destroy timelines
	{timelineDeletes}

	// Destroy meshes
	{meshDeletes}

	// Destroy lights
	{lightDeletes}

	// Destroy objects
	{objectDeletes}

	// Destroy rooms
	{roomDeletes}

	is_initialized = false; // Unset the engine initialization flag

	return 0; // Return 0 on success
}}
#undef DEL

#endif // RES
