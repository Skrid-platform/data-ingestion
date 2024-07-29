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
from os.path import isfile, isdir

#---Project
from src.MeiToGraph import MeiToGraph
from src.utils import log, basename


##-Init
version = '0.1.0'


##-Types
def folder_arg(f: str):
    '''
    Raises an argument parser error if `f` is not a folder.

    - f : the path to a folder, or not.
    '''

    if not isdir(f):
        raise argparse.ArgumentTypeError(f'"{f}" is not a folder')

    else:
        return f


##-Utils
def make_dump_fn(input_file: str, output_folder: str|None):
    '''
    Create the filename for the dump associated to the input file `input_file`.
    If `output_folder` is not None, it changes the path to this folder.

    - input_file    : the input mei filename ;
    - output_folder : the argparse `output_folder` option.
    '''

    b = basename(input_file) + '_dump.cypher'
    
    if output_folder == None:
        path = '/'.join(input_file.split('/')[:-1])
    else:
        if output_folder[-1] == '/':
            path = output_folder[:-1]
        else:
            path = output_folder

    return path + '/' + b


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
            help='print logs when a file is converted'
        )

        self.parser.add_argument(
            '-n', '--no-confirmation',
            action='store_true',
            help='Do not ask for confirmation before overwriting a file'
        )

        self.parser.add_argument(
            '-o', '--output-folder',
            type=folder_arg,
            help='save all dumps in the given folder'
        )

        #TODO: option to write .cql file

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
            nargs='+',
            help='the MEI files to convert. For each file, it adds "_dump.cypher" to the basename of the file.'
        )

    def parse(self):
        '''Parse the args'''

        #---Get arguments
        args = self.parser.parse_args()

        for k, f in enumerate(args.files):
            if not isfile(f):
                log('warn', f'"{f}" is not a file !')

            else:
                dump_fn = make_dump_fn(f, args.output_folder)

                if args.verbose:
                    log('info', f'Converting file "{f}" to "{dump_fn}" ...')

                converter = MeiToGraph(f, args.verbose)
                if converter.to_file(dump_fn, args.no_confirmation):
                    log('info', f'File "{f}" has been converted to cypher in file "{dump_fn}" ! {round((k + 1) / len(args.files) * 100)}% done !')
                else:
                    log('info', f'Conversion for the file "{f}" has been canceled ! {round((k + 1) / len(args.files) * 100)}% done !')


    class Version(argparse.Action):
        '''Class used to show version.'''

        def __call__(self, parser, namespace, values, option_string):

            print(f'Musypher v{version}')
            parser.exit()

