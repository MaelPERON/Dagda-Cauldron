from pathlib import Path
import os
import json
import datetime
import re

SCRIPT_FOLDER = Path(__file__).parent
ASSET_TYPES = {
	"Characters": ["char","chars","character"],
	"Props": ["prop","props"],
	"Sets": ["set","setdress"],
	"Parts": ["part","parts"],
	"Vehicles": ["veh","vehicle"],
}
CONFIG_PATH = None
ROOT_PATH = None

def fetch_resource_path(resource: str | Path) -> Path:
	path = Path(os.path.expandvars(resource))

	if not path.is_absolute():
		path = SCRIPT_FOLDER / path

	return path

def create_tree_file(path: Path, content: str = ""):
	content = os.path.expandvars(content)
	path.parent.mkdir(parents=True, exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)

def create_tree_from_dict(base_path: Path, tree: dict|str):
	if isinstance(tree, dict):
		for key, value in tree.items():
			key_expanded = os.path.expandvars(key)
			item_path = base_path / key_expanded
			if isinstance(value, dict):
				item_path.mkdir(exist_ok=True, parents=True)
				create_tree_from_dict(item_path, value)
			else:
				create_tree_file(item_path, value)
	else:
		# Here "tree" is the content of the file to create at base_path
		create_tree_file(base_path, tree)

def generate_asset_tree(asset_name: str, tree: dict[dict|str]) -> Path:
	parts = asset_name.split("_")
	length = len(parts)
	if length < 2:
		raise ValueError(f"Asset name must be in the format <type>_<id>[_<variant>], got: {asset_name}")
	elif length == 2:
		asset_type = parts[0]
		asset_id = parts[1]
		asset_variant = "base"
	else:
		asset_type = parts[0]
		asset_variant = parts[-1]
		asset_id = "_".join(parts[1:-1])

	# Verify asset_type is a valid alias in ASSET_TYPES
	for key, aliases in ASSET_TYPES.items():
		if asset_type in aliases:
			asset_type = key
			break
	else:
		raise ValueError(f"Invalid asset type alias: {asset_type}\nValid types are: {ASSET_TYPES}")

	asset_prefix = ASSET_TYPES[asset_type][0]

	base_folder = ROOT_PATH / asset_prefix
	base_folder.mkdir(parents=True, exist_ok=True)

	env = {
		"ASSET_TYPE": asset_type,
		"ASSET_ID": asset_id,
		"ASSET_NAME": asset_name,
		"ASSET_VARIANT": asset_variant,
		"ASSET_PREFIX": asset_prefix,
		"CREATION_TIME": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
	}

	for key, value in env.items():
		os.environ[key] = value

	create_tree_from_dict(base_folder, tree)

if __name__ == "__main__":
	root = r"G:\Mon Drive\ENSI\01_E4\Exos\taste_of_guerilla" # first argument
	config = r"D:\Documents\Github\Dagda-Cauldron\Pipeline\arborescence\assets.json" # second argument
	asset_name = "char_hero" # third argument
	ROOT_PATH = fetch_resource_path("%projet%/assets/")
	CONFIG_PATH = fetch_resource_path("./assets.json")

	if not CONFIG_PATH.exists():
		raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")

	if not CONFIG_PATH.is_file() or CONFIG_PATH.suffix != ".json":
		raise ValueError(f"Invalid configuration file: {CONFIG_PATH}")

	aborescence = json.load(open(CONFIG_PATH))

	generate_asset_tree(asset_name, aborescence)