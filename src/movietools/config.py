"""
Configuration class for loading and storig the config data.
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
import sys
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString
from dicttoxml import dicttoxml


class Configuration:
    """Configuration class

    Class for serving configuation information to this module
    """

    def __init__(self):
        """Constructor

        Defines the default values and tryes to load a configuration file
        """

        self.lib_path = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
        self.config_path = os.path.dirname(self.lib_path) + '/config'

        if not os.path.isdir(self.config_path):
            os.makedirs(self.config_path)

        self.api_key = None
        self.movie_extensions = ['mkv', 'avi', 'mp4']
        self.verbose = False
        self.patterns = [' 3D ', '.3D.', ' m1080p ', '.m1080p.',
                         ' m720p ', '.m720p.', ' www.', '.www.', ' (']
        self.patterns_3d = [' 3D ', '.3D.', 'H-TAB', 'H-SBS']

        self.load()

    def __str__(self):
        """Converts this class to string

        To be used into the print function
        """

        return 'Configuration:\n' + \
        '  - api_key = {}\n'.format(self.api_key) + \
        '  - movie_extensions = {}\n'.format(self.movie_extensions) + \
        '  - verbose = {}\n'.format(self.verbose) + \
        '  - patterns = {}\n'.format(self.patterns) + \
        '  - patterns_3d = {}\n'.format(self.patterns_3d)

    def save(self):
        """Save the data to disk

        The format used is XML
        """

        config = {}
        config['verbose'] = self.verbose
        config['api_key'] = self.api_key
        config['movie_extensions'] = self.movie_extensions
        config['patterns'] = self.patterns
        config['patterns_3d'] = self.patterns_3d

        xml_config = dicttoxml(config, root=True, custom_root='config')
        doc_config = parseString(xml_config)

        with open("{}/config.xml".format(self.config_path), "w") as f:
            if sys.version_info >= (3,):
                f.write(doc_config.toprettyxml(indent="  "))
            else:
                f.write(doc_config.toprettyxml(indent="  ").encode('utf-8'))

    def load(self):
        """Loads the data from disk

        If do not exists keeps the class as it is
        """

        if not os.path.isfile(self.config_path + '/config.xml'):
            return
        tree = ET.parse(self.config_path + '/config.xml')
        root = tree.getroot()

        self.api_key = root.find('./api_key').text

        self.movie_extensions = []
        for ext in root.findall('./movie_extensions/item'):
            self.movie_extensions.append(ext.text)

        if root.find('./verbose').text == 'False':
            self.verbose = False
        else:
            self.verbose = True

        self.patterns = []
        for pattern in root.findall('./patterns/item'):
            self.patterns.append(pattern.text)

        self.patterns_3d = []
        for pattern in root.findall('./patterns_3d/item'):
            self.patterns_3d.append(pattern.text)

if __name__ == '__main__':
    CONF = Configuration()
    print(CONF)
