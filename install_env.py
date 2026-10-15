# Source - https://stackoverflow.com/a/73527968
# Posted by Ahmed
# Retrieved 2026-08-13, License - CC BY-SA 4.0

import os
import yaml

with open("environment.yaml") as file_handle:
    environment_data = yaml.safe_load(file_handle)

for dependency in environment_data["dependencies"]:
    if isinstance(dependency, dict):
      for lib in dependency['pip']:
        os.system(f"pip install {lib}")
