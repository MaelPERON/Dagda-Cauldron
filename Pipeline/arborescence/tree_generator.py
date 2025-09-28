from pathlib import Path
import os
import json
import datetime
import re
import argparse

SCRIPT_FOLDER = Path(__file__).parent
CONFIG = None

def fetch_resource_path(resource: str | Path) -> Path:
	if not resource:
		raise ValueError("Resource path cannot be empty or None")
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
		self.root_path = fetch_resource_path(self.config.get("root_path", None))
		self.tree = self.config.get("tree", None)
		self.settings = self.config.get("settings", {
			"entry_type_aliases": None,
			"has_variants": True
		})

	def split_entry(self, entry_name: str) -> list[str]:
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

		return [entry_type, entry_id, entry_variant]

	def fetch_alias(self, entry_type: str) -> str:
		aliases_list = self.settings.get("entry_type_aliases", None)
		if not aliases_list:
			raise ValueError(f"'entry_type_aliases' not defined in configuration file: {self.config}")
		
		# Verify entry_type is a valid alias in aliases_list
		for key, aliases in aliases_list.items():
			if entry_type.lower() in aliases:
				return key
		
		raise ValueError(f"Invalid entry type alias: {entry_type}\nValid types are: {aliases_list}")
	
	def parse_entry(self, entry_name: str) -> Path:
		entry_type, entry_id, entry_variant = self.split_entry(entry_name)

		entry_prefix = self.fetch_alias(entry_type)

		if not self.root_path.exists():
			raise FileNotFoundError(f"Root path not found: {self.root_path}")
		base_folder = self.root_path / entry_prefix
		base_folder.mkdir(parents=True, exist_ok=True)

		env = {
			"ENTRY_TYPE": entry_type,
			"ENTRY_ID": entry_id,
			"ENTRY_NAME": entry_name,
			"ENTRY_VARIANT": entry_variant,
			"ENTRY_PREFIX": entry_prefix
		}

		self.update_env(env)

		return base_folder
	
	def update_env(self, new_vars: dict):
		for key, value in new_vars.items():
			os.environ[key] = value

	def add_entry(self, entry_name: str):
		base_folder = self.parse_entry(entry_name)

		extra_env = {
			"CREATION_TIME": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		}
		self.update_env(extra_env)

		create_tree_from_dict(base_folder, self.tree)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description="Generate tree structure from config and entry name.")
	parser.add_argument("config", type=str, help="Path to the configuration JSON file.")
	parser.add_argument("entry", type=str, help="Entry name to add.")
	args = parser.parse_args()

	generator = TreeGenerator(args.config)
	generator.add_entry(args.entry)