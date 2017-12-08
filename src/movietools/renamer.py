"""
Script for renaming moive files to standard names used in programs like plex
"""

from __future__ import (division, absolute_import, print_function, unicode_literals)

__author__ = "Marc Vivet"
__copyright__ = "Copyright 2017 Marc Vivet."
__credits__ = ["Marc Vivet"]
__license__ = "GNU v3.0"
__version__ = "1.0.0"
__maintainer__ = "Marc Vivet"
__email__ = "marc.vivet@gmail.com"
__status__ = "Development"


import os
import glob
import ntpath
import argparse
import readchar
import tmdbsimple as tmdb
from config import Configuration


class MovieName:
    """Search names of video files
    """
    def __init__(self):
        self.config = Configuration()
        tmdb.API_KEY = self.config.api_key

    def is_video(self, path_name):
        for ext in self.config.movie_extensions:
            if ext in path_name[-3:]:
                return True

        return False

    def __is_3d(self, path):
        movie_name = ntpath.basename(path)

        for patt in self.config.patterns_3d:
            if patt in movie_name:
                return patt

        return None

    def get_candidates(self, path):
        movie_name = ntpath.basename(path)[:-4]
        extension = path[-3:]

        is3d = self.__is_3d(path)

        for pattern in self.config.patterns:
            if pattern in movie_name:
                movie_name = movie_name.split(pattern)[0]

        movie_name = movie_name.replace('. ', '<point>').replace('.', ' ').replace('<point>', '. ')

        search = tmdb.Search()

        response = search.movie(query=movie_name, language='es')

        if not search.results:
            response = search.movie(query=movie_name)

        options = []
        for result in search.results:
            year = result['release_date'].split('-')[0]
            title = result['title'].replace(':', ',').replace('/', ' ').replace('\\', ' ')

            if is3d:
                name = u'{} ({}) - {}.{}'.format(title, year, is3d, extension)
            else:
                name = u'{} ({}).{}'.format(title, year, extension)

            options.append(name)

        return options


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument("--verbose", help="Activates output verbosity",
                        action="store_true")
    PARSER.add_argument('-i', '--input', help='Input folder',
                        type=str, default='./')

    ARGS = PARSER.parse_args()

    if not os.path.exists(ARGS.input):
        print('Input path does not exist.')
        exit()

    MOVIE_NAME = MovieName()

    MOVIES = []
    if os.path.isdir(ARGS.input):
        for extension in MOVIE_NAME.config.movie_extensions:
            MOVIES.extend(glob.glob(os.path.join(ARGS.input, '*.' + extension)))
    else:
        if not MOVIE_NAME.is_video(ARGS.input):
            print('Input file is not supported.')
            exit()

        MOVIES.append(ARGS.input)

    for movie in MOVIES:
        candidates = MOVIE_NAME.get_candidates(movie)

        print('Renaming file {}'.format(movie))

        if not candidates:
            print('  No results found, skiping this movie ...')
            print()
            continue

        for index, candidate in enumerate(candidates):
            if index > 9:
                break

            print('  {} - {}'.format(index, candidate))

        print('  s - Skip this movie.')
        print('Select an option [default 0]: ')

        selection = readchar.readkey()

        index = 0
        if selection != '\r' and selection != '\n':
            if selection == 's':
                print('Skiping this movie ...')
                print()
                continue

            index = int(selection)

            if index >= len(candidates):
                print('Incorrect index ... skiping this movie.')
                print()
                continue

        print('The selected name is: {}'.format(candidates[index]))
        print()

        os.rename(movie, os.path.join(ARGS.input, candidates[index]))
