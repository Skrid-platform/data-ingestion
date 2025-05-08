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
                # try:
                res = converter.to_file(dump_fn, args.no_confirmation)
                # except:
                #     print(f"Something went wrong for {f}")

                if res:
                    log('info', f'File "{f}" has been converted to cypher in file "{dump_fn}" ! {round((k + 1) / len(args.files) * 100)}% done !')
                    dump_files.append(dump_fn)

                else:
                    log('info', f'Conversion for the file "{f}" has been canceled ! {round((k + 1) / len(args.files) * 100)}% done !')
        
        if args.cql != None:
            if len(dump_files) == 0:
                log('warn', f'Generation of {args.cql} canceled as no file was generated !')
                return

            self._make_cql_file(dump_files, args.cql, 100, args.no_confirmation, args.verbose)

    def _make_cql_file(self, dump_files: list[str], output_dir: str, dump_per_file: int = 0, no_confirmation: bool = False, verbose: bool = False):
        '''
        Creates .cql files that are used to load dump files into the database.

        - dump_files      : the list of the .cypher filenames;
        - output_dir      : the output directory to save the .cql files;
        - dump_per_file   : the number of dump files per .cql file (0 means all in one file);
        - no_confirmation : if True, do not ask for confirmation to overwrite files if they already exist;
        - verbose         : if True, log errors and warnings.
        '''

        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Helper function to write CQL content to a file
        def write_cql_file(file_list, file_index):
            cql_filename = f'output_{file_index + 1}.cql'
            cql_filepath = join(output_dir, cql_filename)

            if not write_file(cql_filepath, '', no_confirmation, verbose):
                return

            with open(cql_filepath, 'w') as f:
                f.write('CALL apoc.cypher.runFiles([')
                for i, dump_file in enumerate(file_list):
                    abs_path = abspath(dump_file)
                    f.write(f"'{abs_path}'")
                    if i != len(file_list) - 1:
                        f.write(', ')
                f.write('], {statistics: false});')

            log('info', f'File "{cql_filepath}" written!')

        if dump_per_file > 0:
            # Split the dump files into chunks
            for i in range(0, len(dump_files), dump_per_file):
                chunk = dump_files[i:i + dump_per_file]
                write_cql_file(chunk, i // dump_per_file)
        else:
            # Create a single file for all dump files
            write_cql_file(dump_files, 0)



    class Version(argparse.Action):
        '''Class used to show version.'''

        def __call__(self, parser, namespace, values, option_string):

            print(f'Musypher v{version}')
            parser.exit()

