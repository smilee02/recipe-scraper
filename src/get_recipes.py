import json
import os
import time
from urllib import request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

import sys
from os import path
import argparse
from multiprocessing import Pool, cpu_count


from foodnetwork import FoodNetwork

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
}


def get_fn_urls(recipe_types):
    # Get urls from FoodNetwork
    base_url = 'https://foodnetwork.co.uk'
    collections_url_string = 'collections'
    last_page = 1000
    lag0 = 0
    for recipe in recipe_types:
        output_folder = os.path.join(os.path.dirname(__file__), '..', 'output')
        page_number = 1
        # Create the output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)

        file_name = os.path.join(
            output_folder, f'{recipe}_urls.txt')
        while True:
            print(recipe + " Page:" + str(page_number))
            if page_number >= last_page:
                break
            url = ('{}/{}/{}?recipes={}'.format(base_url,
                   collections_url_string, recipe, page_number))

            t0 = time.time()
            try:
                soup = BeautifulSoup(request.urlopen(
                    request.Request(url, headers=HEADERS)).read(), "html.parser")
                data_page_attr = soup.find('div')['data-page']
                decoded_json_str = data_page_attr.replace('&quot;', '"')
                parsed_json = json.loads(decoded_json_str)
                props = parsed_json['props']
                resource = props['resource']
                all_recipes = (resource['all_recipes'])
                if page_number <= last_page:
                    helper = ((all_recipes['paginate'])['resource'])
                    recipes = helper['data']
                    for r in recipes:
                        aux = r['breadcrumbs'][2]
                        recipe_url = aux['url']
                        with open(file_name, 'a') as file:
                            file.write(recipe_url)
                            file.write('\n')
                    last_page = helper['last_page']

                if page_number == last_page:
                    page_number = 1
                lag1 = time.time() - t0
                time.sleep(lag1 * 1 + lag0 * 1)
                lag0 = lag1
                page_number += 1
            except (HTTPError, URLError, json.decoder.JSONDecodeError):
                print('Could not parse page {}'.format(url))


def get_fn_recipes():

    file_name = 'output.txt'
    recipes_file = 'recipes.json'
    lag0 = 0
    # Read URLs from file
    scraped_data = []  # List to store scraped data
    with open(file_name, 'r') as file:
        for url in file:
            t0 = time.time()
            obj = scrape_fn(url)
            lag1 = time.time() - t0
            time.sleep(lag1 * 1 + lag0 * 1)
            lag0 = lag1
            scraped_data.append(obj)  # Append scraped data to the list
            print(obj['title'])
    save_recipes(recipes_file, scraped_data)


def scrape_fn(url):
    scraper = FoodNetwork(url)
    title = scraper.title()
    description = scraper.description()
    slug = scraper.slug()
    total_time = scraper.total_time()
    cook_time = scraper.cook_time()
    difficulty = scraper.difficulty()
    servings = scraper.servings()
    terms = scraper.terms()
    ingredients = scraper.ingredients()
    instructions = scraper.instructions()
    image = scraper.image()

    return {
        'title': title,
        'description': description,
        'slug': slug,
        'total_time': total_time,
        'cook_time': cook_time,
        'difficulty': difficulty,
        'servings': servings,
        'terms': terms,
        'ingredients': ingredients,
        'instructions': instructions,
        'image': image,
        'url': url

    }


'''def quick_load(site_str):
    return load_recipes(path.join(
        config.path_data, 'recipes_raw_{}.json'.format(site_str)))

def load_recipes(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def quick_save(site_str, recipes):
    save_recipes(
        path.join(config.path_data, 'recipes_raw_{}.json'.format(site_str)),
        recipes)
'''


def save_recipes(filename, recipes):
    with open(filename, 'w') as f:
        json.dump(recipes, f, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--multi', action='store_true', help='Multi threading')
    parser.add_argument('--append', action='store_true',
                        help='Append scrapping run to existing JSON doc')
    parser.add_argument('--status', type=int, default=50,
                        help='Print status interval')
    parser.add_argument('--start', type=int, default=1, help='Start page')
    parser.add_argument('--pages', type=int, default=3000,
                        help='Number of pages to scrape')
    parser.add_argument('--sleep', type=int, default=0,
                        help='Seconds to wait before scraping next page')

    # Food Network
    parser.add_argument('--fn', action='store_true', help='Food Network')
    parser.add_argument('--fnurls', action='store_true',
                        help='Food Network RecipesURLs')
    # All recipe types
    parser.add_argument('--all', action='store_true',
                        help='Scrape all recipe types')

    # Define arguments for recipe types
    parser.add_argument('--starter', action='store_true',
                        help='Scrape starter dishes')
    parser.add_argument('--main', action='store_true',
                        help='Scrape main course')
    parser.add_argument('--dessert', action='store_true',
                        help='Scrape dessert dishes')
    parser.add_argument('--side', action='store_true',
                        help='Scrape side dishes')
    parser.add_argument('--snack', action='store_true',
                        help='Scrape snack dishes')
    parser.add_argument('--vegetarian', action='store_true',
                        help='Scrape vegetarian dishes')
    parser.add_argument('--vegan', action='store_true',
                        help='Scrape vegan dishes')
    parser.add_argument('--gluten-free', action='store_true',
                        help='Scrape gluten-free dishes')
    parser.add_argument('--dairy-free', action='store_true',
                        help='Scrape dairy-free dishes')
    parser.add_argument('--healthy', action='store_true',
                        help='Scrape healthy dishes')
    parser.add_argument('--chicken', action='store_true',
                        help='Scrape chicken dishes')
    parser.add_argument('--beef', action='store_true',
                        help='Scrape beef dishes')
    parser.add_argument('--pork', action='store_true',
                        help='Scrape pork dishes')
    parser.add_argument('--seafood', action='store_true',
                        help='Scrape seafood dishes')
    parser.add_argument('--egg', action='store_true', help='Scrape egg dishes')
    parser.add_argument('--cheese', action='store_true',
                        help='Scrape cheese dishes')
    parser.add_argument('--thanksgiving', action='store_true',
                        help='Scrape Thanksgiving dishes')
    parser.add_argument('--christmas', action='store_true',
                        help='Scrape Christmas dishes')
    parser.add_argument('--halloween', action='store_true',
                        help='Scrape Halloween dishes')
    parser.add_argument('--breakfast', action='store_true',
                        help='Scrape breakfast dishes')
    parser.add_argument('--brunch', action='store_true',
                        help='Scrape brunch dishes')
    parser.add_argument('--lunch', action='store_true',
                        help='Scrape lunch dishes')
    parser.add_argument('--dinner', action='store_true',
                        help='Scrape dinner dishes')

    args = parser.parse_args()

    # Check if the --all argument is specified to scrape all recipe types
    if args.all:
        args.starter = args.main = args.dessert = args.side = args.snack = args.vegetarian = args.vegan = \
            args.gluten_free = args.dairy_free = args.healthy = args.chicken = args.beef = args.pork = \
            args.seafood = args.egg = args.cheese = args.thanksgiving = args.christmas = args.halloween = \
            args.breakfast = args.brunch = args.lunch = args.dinner = True

    # Check for individual recipe types
    if args.fnurls:
        selected_recipe_types = []

        if args.starter:
            selected_recipe_types.append('starter-recipes')
        if args.main:
            selected_recipe_types.append('main-course-recipes')
        if args.dessert:
            selected_recipe_types.append('dessert-recipes')
        if args.side:
            selected_recipe_types.append('side-dish-recipes')
        if args.snack:
            selected_recipe_types.append('snack-recipes')
        if args.vegetarian:
            selected_recipe_types.append('vegetarian-recipes')
        if args.vegan:
            selected_recipe_types.append('vegan-recipes')
        if args.gluten_free:
            selected_recipe_types.append('gluten-free-recipes')
        if args.dairy_free:
            selected_recipe_types.append('dairy-free-recipes')
        if args.healthy:
            selected_recipe_types.append('healthy-recipes')
        if args.chicken:
            selected_recipe_types.append('chicken-recipes')
        if args.beef:
            selected_recipe_types.append('beef-recipes')
        if args.pork:
            selected_recipe_types.append('pork-recipes')
        if args.seafood:
            selected_recipe_types.append('seafood-recipes')
        if args.egg:
            selected_recipe_types.append('egg-recipes')
        if args.cheese:
            selected_recipe_types.append('cheese-recipes')
        if args.thanksgiving:
            selected_recipe_types.append('thanksgiving-recipes')
        if args.christmas:
            selected_recipe_types.append('christmas-recipes')
        if args.halloween:
            selected_recipe_types.append('halloween-recipes')
        if args.breakfast:
            selected_recipe_types.append('breakfast-recipes')
        if args.brunch:
            selected_recipe_types.append('brunch-recipes-1')
        if args.lunch:
            selected_recipe_types.append('lunch-recipes')
        if args.dinner:
            selected_recipe_types.append('dinner-recipes')
        if args.snack:
            selected_recipe_types.append('snack-recipes')

        get_fn_urls(selected_recipe_types)
    if args.fn:
        recipe_links_dict = get_fn_recipes()
