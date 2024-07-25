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
from sys import stderr

from datetime import datetime as dt

#---Project
#TODO


##-Init
version = '0.1.0'


##-Util
def log(msg, lvl='warn', use_stderr=True):
    '''
    Write msg as a log, in the following format :
        [date time] - Musypher: [level]: [message]

    - msg (str)         : the message to log ;
    - lvl (str)         : the level of the message (usually 'info', 'warn', 'error') ;
    - use_stderr (bool) : if True, write to stderr. Otherwise write to stdout.
    '''

    p = f'{dt.now()} - Musypher: {lvl}: {msg}'

    if use_stderr:
        print(p, file=stderr)
    else:
        print(p)


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
            '-v', '--version',
            help='show version and exit',
            nargs=0,
            action=self.Version
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
                log(f'"{f}" is not a file !', 'warn')

            else:
                print(f) #TODO


    class Version(argparse.Action):
        '''Class used to show version.'''

        def __call__(self, parser, namespace, values, option_string):

            print(f'Musypher v{version}')
            parser.exit()


##-Run
if __name__ == '__main__':
    app = ParserUi()
    app.parse()
