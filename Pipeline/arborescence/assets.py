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
	path = Path(resource)

	if not path.is_absolute():
		path = SCRIPT_FOLDER / path

	return path

def create_tree_file(path: Path, content: str = ""):
	content = os.path.expandvars(content)
	path.parent.mkdir(parents=True, exist_ok=True)
	with open(path, "w", encoding="utf-8") as f:
		f.write(content)
if __name__ == "__main__":
	root = r"G:\Mon Drive\ENSI\01_E4\Exos\taste_of_guerilla" # first argument
	config = r"D:\Documents\Github\Dagda-Cauldron\Pipeline\arborescence\assets.json" # second argument
	ROOT_PATH = fetch_resource_path(os.path.expandvars("%projet%/assets/"))
	CONFIG_PATH = fetch_resource_path(os.path.expandvars("./assets.json"))

	if not CONFIG_PATH.exists():
		raise FileNotFoundError(f"Configuration file not found: {CONFIG_PATH}")

	if not CONFIG_PATH.is_file() or CONFIG_PATH.suffix != ".json":
		raise ValueError(f"Invalid configuration file: {CONFIG_PATH}")

	aborescence = json.load(open(CONFIG_PATH))

	generate_asset_tree("char_hero_v1", aborescence)