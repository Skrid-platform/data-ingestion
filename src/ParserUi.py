#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.25
# Version           : v1.0.0
#
#--------------------------------

'''File defining the user interface using argparse.'''

##-Imports
#---General
import argparse
from os.path import isfile

#---Project
from src.MeiToGraph import MeiToGraph
from src.utils import log


##-Init
version = '0.1.0'


##-Ui parser
class ParserUi:
    '''Defines an argument parser'''

    def __init__(self):
        '''Initiate Parser'''

        #------Main parser
        #---Init
        self.parser = argparse.ArgumentParser(
            prog='Musypher',
            description='Compiles fuzzy queries to cypher queries',
            # epilog='Examples :\n\tSearchWord word\n\tSearchWord "example of string" -e .py;.txt\n\tSearchWord someword -x .pyc -sn', #TODO: add examples
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        #---Add arguments
        self.parser.add_argument(
            '-V', '--version',
            help='show version and exit',
            nargs=0,
            action=self.Version
        )
        self.parser.add_argument(
            '-v', '--verbose',
            action='store_true',
            help='print logs when a file is converted',
        )

        # self.parser.add_argument(
        #     '-U', '--URI',
        #     default='bolt://localhost:7687',
        #     help='the uri to the neo4j database'
        # )
        # self.parser.add_argument(
        #     '-u', '--user',
        #     default='neo4j',
        #     help='the username to access the database'
        # )
        # self.parser.add_argument(
        #     '-p', '--password',
        #     default='12345678',
        #     help='the password to access the database'
        # )

        self.parser.add_argument(
            'files',
            nargs='*',
            help='the MEI files to convert. For each file, it adds "_dump.cypher" to the basename of the file.' #TODO: check that it is still acurate
        )

    def parse(self):
        '''Parse the args'''

        #---Get arguments
        args = self.parser.parse_args()

        for f in args.files:
            if not isfile(f):
                log('warn', f'"{f}" is not a file !')

            else:
                print(f) #TODO

                # if args.verbose:
                #     log('info', f'File "{f}" has been converted to cypher in file "{TODO}"')


    class Version(argparse.Action):
        '''Class used to show version.'''

        def __call__(self, parser, namespace, values, option_string):

            print(f'Musypher v{version}')
            parser.exit()

