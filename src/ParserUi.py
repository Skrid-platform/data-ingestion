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
from os.path import isfile, isdir, abspath, join
import os

#---Project
from src.MeiToGraph import MeiToGraph
from src.utils import log, basename, write_file
from src.neo4j_connection import connect_to_neo4j, run_query


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
        examples = 'Examples :'
        examples += '\n\tconvert `file.mei`                       : ./main.py file.mei'
        examples += '\n\tconvert all mei files in the mei/ folder : ./main.py mei/*.mei'
        examples += '\n\tconvert all mei files in the sub path    : ./main.py **/*.mei'
        examples += '\n\tconvert all, overwrite, save in cypher/,'
        examples += '\n\t generate .cql, show progression         : ./main.py -nv -q load_all.cql -o cypher/ **/*.mei'

        self.parser = argparse.ArgumentParser(
            prog='Musypher',
            description='Compiles fuzzy queries to cypher queries',
            epilog=examples,
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

        self.parser.add_argument(
            '-q', '--cql',
            help='If enabled, also create the .cql file (that is useful to load all the generated .cypher in the database)'
        )
        self.parser.add_argument(
            '--load',
            type=str,
            help='if set, load the given .cql file into the Neo4j database using apoc.cypher.runFile for each dump listed'
        )
        self.parser.add_argument(
            '--uri',
            type=str,
            default='bolt://localhost:7687',
            help='the URI of the Neo4j database (default: bolt://localhost:7687)'
        )
        self.parser.add_argument(
            '--user',
            type=str,
            default='neo4j',
            help='Neo4j username (default: neo4j)'
        )
        self.parser.add_argument(
            '--password',
            type=str,
            default='12345678',
            help='Neo4j password (default: 12345678)'
        )

        self.parser.add_argument(
            'files',
            nargs='+',
            help='the MEI files to convert. For each file, it adds "_dump.cypher" to the basename of the file.'
        )

    def parse(self):
        '''Parse the args'''

        #---Get arguments
        args = self.parser.parse_args()

        if args.load:
            if not isfile(args.load):
                log('error', f'Load file "{args.load}" not found.')
                return

            with open(args.load, 'r') as f:
                lines = f.readlines()

            driver = connect_to_neo4j(args.uri, args.user, args.password)

            for i, line in enumerate(lines):
                line = line.strip()
                if line == '':
                    continue
                log('info', f'Running query {i+1}/{len(lines)}: {line[:60]}...')
                try:
                    run_query(driver, line)
                except Exception as e:
                    log('error', f'Error running query {i+1}: {e}')
                    break

            log('info', f'Finished loading {args.load}.')

        else:
            dump_files = []

            for k, f in enumerate(args.files):
                if not isfile(f):
                    log('warn', f'"{f}" is not a file !')

                else:
                    dump_fn = make_dump_fn(f, args.output_folder)

                    if args.verbose:
                        log('info', f'Converting file "{f}" to "{dump_fn}" ...')

                    converter = MeiToGraph(f, args.verbose)

                    res = None
                    try:
                        res = converter.to_file(dump_fn, args.no_confirmation)
                    except Exception as err:
                        print(f'Something went wrong for "{f}": {err}')

                    if res:
                        log('info', f'File "{f}" has been converted to cypher in file "{dump_fn}" ! {round((k + 1) / len(args.files) * 100)}% of files done !')
                        dump_files.append(dump_fn)

                    else:
                        log('info', f'Conversion for the file "{f}" has been canceled ! {round((k) / len(args.files) * 100)}% of files done !')
            
            if args.cql != None:
                if len(dump_files) == 0:
                    log('warn', f'Generation of {args.cql} canceled as no file was generated !')
                    return

                self._make_cql_file(dump_files, args.cql, args.no_confirmation, args.verbose)

    def _make_cql_file(self, dump_files: list[str], output_file: str, no_confirmation: bool = False, verbose: bool = False):
        '''
        Creates a .cql file with one `CALL apoc.cypher.runFile(...)` per dump file.

        - dump_files      : the list of the .cypher filenames;
        - output_file     : the output .cql file;
        - no_confirmation : do not ask for confirmation before overwriting;
        - verbose         : log actions.
        '''

        if not write_file(output_file, '', no_confirmation, verbose):
            return

        with open(output_file, 'w') as f:
            for dump_file in dump_files:
                abs_path = abspath(dump_file)
                f.write(f"CALL apoc.cypher.runFile('{abs_path}', {{usePeriodicCommit: 1000, statistics: false}});\n")

        log('info', f'File "{output_file}" written!')

    class Version(argparse.Action):
        '''Class used to show version.'''

        def __call__(self, parser, namespace, values, option_string):

            print(f'Musypher v{version}')
            parser.exit()

