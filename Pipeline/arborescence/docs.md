## How to Create a Config File for tree_generator.py

This guide explains how to make a config file for the tree generator script. It helps you automatically create organized folders and files for your project.

### 1. What is the config file?
The config file is a JSON file that tells the script:
- Where to create the folders/files (`root_path`)
- What folder structure to create (`tree`)
- How to handle entry types and variants (`settings`)

### 2. Basic structure
Here’s a simple example:

```json
{
	"settings": {
		"entry_type_aliases": {
			"characters": ["characters", "char"],
			"props": ["props", "prop"]
		},
		"has_variants": true
	},
	"root_path": "%project%/assets",
	"tree": {
		"%entry_id%_%entry_variant%": {
			"modeling": {
				"work": {},
				"exports": {}
			},
			"description.txt": "Asset created at %CREATION_TIME%"
		}
	}
}
```

### 3. Key parts explained
- **settings.entry_type_aliases**: Maps entry types to possible names. E.g., "char" and "characters" are treated the same.
- **root_path**: Where the tree will be created. You can use environment variables like `%project%`.
- **tree**: The folder/file structure. Use placeholders like `%entry_id%` and `%entry_variant%` to customize names.

### 4. How to use
1. Save your config as `configs.json`.
2. Run the script in terminal:
	 ```
	 python tree_generator.py configs.json characters_John_base
	 ```
	 This creates a folder structure for a character named "John" with the "base" variant.

### 5. Customizing
- Add more entry types in `entry_type_aliases`.
- Change the folder structure in `tree` to fit your needs.
- Add files with custom content using placeholders (e.g., `%CREATION_TIME%`).

#### About Placeholders and Environment Variables

**Placeholders** like `%entry_id%`, `%entry_variant%`, `%CREATION_TIME%`, and `%project%` are special keywords in the config file. When the script runs, it replaces them with real values (like the entry name, variant, or current time).

**Why use them?**
- They make your folder and file names dynamic and personalized for each asset.
- You don’t need to manually edit the config for every new entry.

**Environment variables** (like `%project%`) let you use system-wide values. For example, if you set `project=MyProject` in your environment, `%project%` will be replaced with `MyProject`.

**Benefits:**
- Reuse the same config for different projects or users.
- Automatically fill in details like dates, user names, or project names.

**Tip:** You can set environment variables in your system or terminal before running the script, so the config adapts to your setup.

### 6. Example output
For the above config and entry `characters_John_base`, you’ll get:

```
assets/
	characters/
		John_base/
			modeling/
				work/
				exports/
			description.txt
```

### Summary
- Edit `configs.json` to define your structure.
- Use placeholders for dynamic names.
- Run the script with your config and entry name.

This makes it easy for anyone to generate organized project folders automatically!
