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

from foodnetwork.foodnetwork import FoodNetwork
from utils import *


def get_fn_urls(recipe_types, header):
    # Get urls from FoodNetwork
    base_url = 'https://foodnetwork.co.uk'
    collections_url_string = 'collections'
    last_page = 1000
    lag0 = 0
    for recipe in recipe_types:
        output_folder = os.path.join(
            os.path.dirname(__file__), '..', '..', 'outputs')
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
                    request.Request(url, headers=header)).read(), "html.parser")
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


def get_fn_recipes(recipe_types):
    output_folder = os.path.join(
        os.path.dirname(__file__), '..', '..', 'outputs')
    # Create the output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    unscraped_urls_file = os.path.join(
        output_folder, f'unscraped_urls.txt')
    unscraped_urls = []
    for recipe in recipe_types:

        file_name = os.path.join(
            output_folder, f'{recipe}_urls.txt')
        recipes_file = os.path.join(output_folder, f'{recipe}.json')
        lag0 = 0
        # Read URLs from file
        scraped_data = []  # List to store scraped data
        with open(file_name, 'r') as file:
            for url in file:
                try:
                    t0 = time.time()
                    obj = scrape_fn(url)
                    lag1 = time.time() - t0
                    time.sleep(lag1 * 1 + lag0 * 1)
                    lag0 = lag1
                    scraped_data.append(obj)  # Append scraped data to the list
                    print(obj['title'])

                except TypeError as e:
                    print('Couldn\'t scrape '+url)
                    unscraped_urls.append(url)
            save_recipes(recipes_file, scraped_data)
    unscraped_recipes(unscraped_urls_file, str(unscraped_urls))


def scrape_fn(url):
    scraper = FoodNetwork(url)
    if scraper.soup != None:
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
            'url': url.strip()
        }
    else:
        return ''
