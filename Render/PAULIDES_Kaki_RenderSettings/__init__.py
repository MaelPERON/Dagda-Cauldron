# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Set_render_settings",
    "author": "MaelPERON",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

import bpy
import re
from mathutils import *

class PROD_PT_FOM_Panel(bpy.types.Panel):
    bl_label = "Prod FOM"
    bl_idname = "PROD_PT_FOM_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Prod FOM"

    def draw(self, context):
        layout = self.layout
        for setting in ["RENDER", "COMPO"]:
            row = layout.row(align=True)
            op = row.operator("dagda.set_scene_properties", text=f"{setting} Settings")
            op.mode = setting
			
        layout.separator()
        row = layout.row(align=True)
        row.operator("lighting.name_automation", text="Name Automation")
        row.operator("lighting.auto_light_linking", text="Auto Light Linking")

class SetSceneProperties(bpy.types.Operator):
    bl_idname = "dagda.set_scene_properties"
    bl_label = "Set Scene Properties"
    bl_description = "Set the scene properties based on the current file name"
    bl_options = {"REGISTER"}

    mode: bpy.props.EnumProperty(items=[
        ("RENDER", "Render", "Set render settings"),
        ("COMPO", "Compo", "Set compo settings"),
    ], default="RENDER",name="Mode",description="Select the mode to set the scene properties")

    @classmethod
    def poll(self, context):
        return True

    def execute(self, context):

        # Render settings
        scene = context.scene
        scene.render.resolution_x = 1920
        scene.render.resolution_y = 1080
        scene.render.resolution_percentage = 25 if self.mode == "LOW" else 100
        scene.cycles.adaptive_threshold = 0.05 if self.mode == "LOW" else 0.02
        scene.render.film_transparent = True
        scene.cycles.samples = 128 if self.mode == "LOW" else 1024
        scene.cycles.use_denoising = self.mode == "RENDER"
        scene.cycles.use_auto_tile = True
        scene.render.use_persistent_data = True
        scene.cycles.tile_size = 512
        scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER" if self.mode == "COMPO" else "OPEN_EXR"
        scene.render.image_settings.exr_codec = "DWAA"
        scene.render.image_settings.color_depth = "16"
        scene.render.use_compositing = not self.mode == "RENDER"
        scene.render.compositor_device = "GPU"
        scene.render.use_sequencer = False
        if self.mode == "HIGH":
            scene.render.use_simplify = self.mode == False

        return {'FINISHED'}
    
def get_ll_name(ll_group: str): return f"LL {ll_group.upper()}"

def get_ll_collection(ll_group: str):
	return bpy.context.blend_data.collections.get(get_ll_name(ll_group), None)

def find_collections(lighting_collection : bpy.types.Collection):
	collections : list[bpy.types.Collection] = lighting_collection.children_recursive
	print(f"Processing {len(collections)} collections in {lighting_collection.name}...")
	for coll in collections:
		print(f"Checking collection: {coll.name}")
		if (search := re.search(coll_pattern, coll.name)) is not None:
			LL_group = search.group(2) # Lighting Linking Group Name
			print(f"Pattern matched. LL_group: {LL_group}")
			LL_coll = get_ll_collection(LL_group)

			collections : bpy.types.BlendDataCollections = bpy.context.blend_data.collections

			if LL_coll is None: # Création groupe light linking
				print(f"{LL_group} group not found. Creating new group...")
				LL_coll = collections.new(name=get_ll_name(LL_group))
				print(f"\tCreated {LL_coll.name}.")
				if (coll_list := auto_light_linking.get(LL_group.lower(), None)):
					for coll_child_name in coll_list:
						print(f"\tLooking for child collection: {coll_child_name}")
						coll_child : bpy.types.Collection = collections.get(coll_child_name, None)
						if not coll_child:
							print(f"\t\t{coll_child_name} not found!")	
							continue
						LL_coll.children.link(coll_child)
						print(f"\t\tAdded {coll_child.name}")
				else:
					print(f"{LL_group} not in auto light linking's list.")
					continue

			# Setting link states
			print(f"Setting link states for {LL_coll.name}...")
			for light_child in [coll.light_linking for coll in LL_coll.collection_children]:
				light_child.link_state = "INCLUDE"

			# Attribution groupe light linking
			print(f"{LL_group}: Applying light linking to objects...")
			for obj in coll.objects:
				print(f"\tApplying light linking to object: {obj.name}")
				LL_obj = obj.light_linking
				LL_obj.blocker_collection = LL_coll
				LL_obj.receiver_collection = LL_coll
	
		else:
			print(f"No pattern match for {coll.name}")

class LIGHTING_OT_name_automation(bpy.types.Operator):
	bl_idname = "lighting.name_automation"
	bl_label = "Lighting Name Automation"
	bl_description = "Automate naming of lighting objects"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		light_collection : bpy.types.Collection = context.blend_data.collections.get("LIGHTING")

		if not light_collection:
			self.report({"ERROR"}, "No Light collection found")
			return {"CANCELLED"}
		
		collections : list[bpy.types.Collection] = light_collection.children_recursive

		for coll in collections:
			coll_name = "LGT-" + re.sub(coll_pattern, r"\2", coll.name)
			coll.name = coll_name

			for obj in coll.objects:
				if obj.type == "LIGHT":
					light_group = coll_name.upper().replace("LGT-", "")
					obj.lightgroup = light_group

					if context.view_layer.lightgroups.get(light_group) is None:
						context.view_layer.lightgroups.add(name=light_group)

		return {'FINISHED'}
	
class LIGHTING_OT_auto_light_linking(bpy.types.Operator):
	bl_idname = "lighting.auto_light_linking"
	bl_label = "Auto Light Linking"
	bl_description = "Automatically set up light linking for lighting collections"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		light_collection: bpy.types.Collection = context.blend_data.collections.get("LIGHTING")

		if not light_collection:
			self.report({"ERROR"}, "No LIGHTING collection found")
			return {"CANCELLED"}

		find_collections(light_collection)

		return {'FINISHED'}
    
classes = (
	SetSceneProperties,
    LIGHTING_OT_name_automation,
	LIGHTING_OT_auto_light_linking,
	PROD_PT_FOM_Panel
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)