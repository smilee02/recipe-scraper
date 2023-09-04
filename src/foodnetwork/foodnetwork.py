from urllib import request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup
import json
import re
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
}


class FoodNetwork:
    def __init__(self, url):
        self.url = url
        self.soup = self._get_soup()

    def _get_soup(self):
        try:
            soup = BeautifulSoup(request.urlopen(
                request.Request(self.url, headers=HEADERS)).read(), "html.parser")
            data_page_attr = soup.find('div')['data-page']
            decoded_json_str = data_page_attr.replace('&quot;', '"')
            r = json.loads(decoded_json_str)
            return (r['props'])['resource']
        except json.decoder.JSONDecodeError:
            print('Wasn\'t possible to scrape Recipe')
            return None

    def title(self):
        return self.soup['title']

    def total_time(self):
        return self.soup['total_time']

    def cook_time(self):
        return self.soup['cook_time']

    def description(self):
        return self.soup['description']

    # Helps search by name
    def slug(self):
        return self.soup['slug']

    def difficulty(self):
        return self.soup['difficulty']

    def servings(self):
        return self.soup['servings']

    def terms(self):
        titles = [item["title"] for item in self.soup["terms"]]
        return titles

    def ingredients(self):
        ingredients = self.soup["instructions"]["ingredients"]
        titles = [item["title"] for item in ingredients]
        return titles

    def instructions(self):
        legacy = self.soup["instructions"]["method_legacy"]
        legacy = re.sub(r'<[^>]+>', '\n', legacy)
        # Replace &nbsp; with spaces
        legacy = legacy.replace('&nbsp;', ' ')
        # Remove extra spaces and newlines
        legacy = re.sub(r'\n\s+', '\n', legacy)
        # Remove leading/trailing spaces
        legacy = legacy.strip()

        # Find all <li> elements and replace with numbered steps
        legacy = re.sub(r'<li>', '\n', legacy)
        legacy = re.sub(r'</li>', '', legacy)

        # Remove extra newlines
        legacy = re.sub(r'\n\s+', '\n', legacy)
        legacy = legacy.strip()
        return legacy

    def image(self):
        return (self.soup['meta']['image'])
