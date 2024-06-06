import requests

from app.log import logger
from plexapi.server import PlexServer


class Emby:
    api_key: str = ''
    server: str = ''

    def __init__(self, api_key: str, server: str):
        self.api_key = api_key
        self.server = server

    def is_valid(self):
        if self.api_key and self.server:
            return True
        return False

    def search(self, keyword):
        url = f"http://{self.server}/emby/Items"
        params = {
            'api_key': self.api_key,
            'SearchTerm': keyword,
            'IncludeItemTypes': 'Movie',
            'Recursive': 'true',
            'StartIndex': '0',
            'IncludeSearchTypes': 'false'
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            search_results = response.json()
            if search_results['Items']:
                movie = search_results['Items'][0]
                return movie
        else:
            logger.error(f"Error: {response.status_code}")


class Plex:
    server: PlexServer = None

    def __init__(self, url, token):
        if url and token:
            self.server = PlexServer(url, token)

    def is_valid(self):
        if self.server:
            return True
        return False

    def search(self, keyword):
        movies = self.server.search(keyword)
        if movies:
            return movies[0]
        return None


class Jellyfin:
    server: str = ''
    api_key: str = ''
    user: str = ''

    def __init__(self, server, api_key, user):
        self.server = server
        self.api_key = api_key
        self.user = user

    def is_valid(self):
        if self.server and self.api_key and self.user:
            return True
        return False

    def search(self, keyword):
        url = f"http://{self.server}/Users/{self.user}/Items"
        params = {
            'api_key': self.api_key,
            'searchTerm': keyword,
            'IncludeItemTypes': 'Movie',
            'Recursive': 'true'
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            search_results = response.json()
            if search_results['Items']:
                movie = search_results['Items'][0]
                return movie
        else:
            logger.error(f"Error: {response.status_code}")
