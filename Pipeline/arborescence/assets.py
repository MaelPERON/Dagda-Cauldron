from pathlib import Path
import os
import json
import datetime
import re

SCRIPT_FOLDER = Path(__file__).parent
CONFIG = None

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

def generate_asset_tree(asset_name: str, tree: dict[dict|str], aliases_list: dict[str, list[str]]) -> Path:
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

	# Verify asset_type is a valid alias in aliases_list
	for key, aliases in aliases_list.items():
		if asset_type.lower() in aliases:
			asset_type = key
			break
	else:
		raise ValueError(f"Invalid asset type alias: {asset_type}\nValid types are: {aliases_list}")

	asset_prefix = aliases_list[asset_type][0]

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
	config_path = r"D:\Documents\Github\Dagda-Cauldron\Pipeline\arborescence\configs.json"
	old_config_path = config_path
	config_path = fetch_resource_path(config_path)
	asset_name = "char_hero_hurt"

	if not config_path.exists():
		raise FileNotFoundError(f"Configuration file not found: {old_config_path}")

	if not config_path.is_file() or config_path.suffix != ".json":
		raise ValueError(f"Invalid configuration file: {old_config_path}")

	CONFIG = json.load(open(config_path))

	root_path = CONFIG.get("root_path", None)
	if not root_path:
		raise ValueError(f"'root_path' not defined in configuration file: {old_config_path}")
	ROOT_PATH = fetch_resource_path(root_path)

	TREE = CONFIG.get("tree", None)
	if not TREE:
		raise ValueError(f"'tree' not defined in configuration file: {old_config_path}")
	
	TYPE_ALIASES = CONFIG.get("type_aliases", None)
	if not TYPE_ALIASES:
		raise ValueError(f"'type_aliases' not defined in configuration file: {old_config_path}")

	generate_asset_tree(asset_name, TREE, TYPE_ALIASES)