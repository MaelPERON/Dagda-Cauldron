import bpy
import re

coll_pattern = r"(LGT-)?(.*)$"
auto_light_linking = {
	"rim_bdt": ["CHARACTERS"],
	"rim_chara": ["CHARACTERS"],
	"rim_patron": ["Patron"],
	"rim_bdt_props": ["CHARACTERS","PROPS"],
	"rim_props": ["PROPS"],
	"rim_extras": ["LAYOUT_EXTRAS"],
	"rim_setdress": ["SETDRESSING"],
	"rim_set": ["Batiment"],
	"rim_four": ["Four"],
	"rim_reservoir": ["Reservoir"],
	"rim_carts": ["Carts"],
	"rim_vestiaire": ["Vestiaire", "Bloc plafond vestiaire"]
}

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
	LIGHTING_OT_name_automation,
	LIGHTING_OT_auto_light_linking,
)

def register():
	for cls in classes:
		bpy.utils.register_class(cls)

def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)

if __name__ == "__main__":
	register()