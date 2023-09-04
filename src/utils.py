from distutils import config
import json
from os import path


def quick_load(site_str):
    return load_recipes(path.join(
        config.path_data, 'recipes_raw_{}.json'.format(site_str)))


def load_recipes(filename):
    with open(filename, 'r') as f:
        return json.load(f)


def quick_save(site_str, recipes):
    save_recipes(
        path.join(config.path_data, 'recipes_raw_{}.json'.format(site_str)),
        recipes)


def save_recipes(filename, recipes):
    with open(filename, 'w') as f:
        json.dump(recipes, f, indent=4)


def unscraped_recipes(filename, urls):
    with open(filename, 'w') as f:
        f.write(urls)
