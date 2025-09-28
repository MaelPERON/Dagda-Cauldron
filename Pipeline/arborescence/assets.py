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

class TreeGenerator:
	def __init__(self, config_path: str | Path):
		path = fetch_resource_path(config_path)
		if not path.exists():
			raise FileNotFoundError(f"Configuration file not found: {config_path}")

		if not path.is_file() or path.suffix != ".json":
			raise ValueError(f"Invalid configuration file: {config_path}")

		self.config : dict = json.load(open(path))
		self.root_path = self.config.get("root_path", None)
		self.tree = self.config.get("tree", None)
		self.settings = self.config.get("settings", {
			"entry_type_aliases": None,
			"has_variants": True
		})
		# self.env

	def parse_entry(self, entry_name: str) -> Path:
		parts = entry_name.split("_")
		length = len(parts)
		if length < 2:
			raise ValueError(f"Entry name must be in the format <type>_<id>[_<variant>], got: {entry_name}")
		elif length == 2:
			entry_type = parts[0]
			entry_id = parts[1]
			entry_variant = "base"
		else:
			entry_type = parts[0]
			entry_variant = parts[-1]
			entry_id = "_".join(parts[1:-1])

		aliases_list = self.settings.get("entry_type_aliases", None)
		if not aliases_list:
			raise ValueError(f"'entry_type_aliases' not defined in configuration file: {self.config}")
		
		# Verify entry_type is a valid alias in aliases_list
		for key, aliases in aliases_list.items():
			if entry_type.lower() in aliases:
				entry_type = key
				break
		else:
			raise ValueError(f"Invalid entry type alias: {entry_type}\nValid types are: {aliases_list}")
		
		entry_prefix = aliases_list[entry_type][0]
		root_path = fetch_resource_path(self.root_path)
		if not root_path.exists():
			raise FileNotFoundError(f"Root path not found: {self.root_path}")
		base_folder = root_path / entry_prefix
		base_folder.mkdir(parents=True, exist_ok=True)

		env = {
			"ENTRY_TYPE": entry_type,
			"ENTRY_ID": entry_id,
			"ENTRY_NAME": entry_name,
			"ENTRY_VARIANT": entry_variant,
			"ENTRY_PREFIX": entry_prefix,
			"CREATION_TIME": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
		}

		for key, value in env.items():
			os.environ[key] = value

		return base_folder

	def add_entry(self, entry_name: str):
		base_folder = self.parse_entry(entry_name)

		create_tree_from_dict(base_folder, self.tree)

if __name__ == "__main__":
	path = r"D:\Documents\Github\Dagda-Cauldron\Pipeline\arborescence\configs.json"
	generator = TreeGenerator(path)

	CONFIG : dict = json.load(open(config_path))

	root_path = CONFIG.get("root_path", None)
	if not root_path:
		raise ValueError(f"'root_path' not defined in configuration file: {path}")
	ROOT_PATH = fetch_resource_path(root_path)

	TREE = CONFIG.get("tree", None)
	if not TREE:
		raise ValueError(f"'tree' not defined in configuration file: {path}")
	
	TYPE_ALIASES = CONFIG.get("type_aliases", None)
	if not TYPE_ALIASES:
		raise ValueError(f"'type_aliases' not defined in configuration file: {path}")

	generate_asset_tree(asset_name, TREE, TYPE_ALIASES)