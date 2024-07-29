#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.26
# Version           : v1.0.0
#
#--------------------------------


##-Imports
from sys import stderr
from os.path import isfile
from datetime import datetime as dt


##-Main
def log(lvl: str, msg: str, use_stderr: bool = False):
    '''
    Write msg as a log, in the following format :
        [date time] - Musypher: [level]: [message]

    - lvl        : the level of the message (usually 'info', 'warn', 'error') ;
    - msg        : the message to log ;
    - use_stderr : if True, write to stderr. Otherwise write to stdout. Default is False.
    '''

    p = f'{dt.now()} - Musypher: {lvl}: {msg}'

    if use_stderr:
        print(p, file=stderr)
    else:
        print(p)

def write_file(fn: str, content: str, no_confirmation: bool = False, verbose: bool = False) -> bool:
    '''
    Writes `content` inside `fn`, and ask confirmation to overwrite, unless if `no_confirmation` is True.

    - fn              : the filename ;
    - content         : the content to write in the file
    - no_confirmation : if True, do not ask for confirmation to overwrite the file if it already exists ;
    - verbose         : if True, log when overwriting a file without confirmation.

    Return:
        - True  if the file has been written ;
        - False otherwise (canceled by the user).
    '''

    if (not no_confirmation) and isfile(fn):
        if input(f'Do you want to overwrite file "{fn}" (y/n) ? (rerun with -n to avoid those prompts)\n>').lower() not in ('y', 'yes'):
            return False

    elif verbose and no_confirmation and isfile(fn):
        log('info', f'Overwriting file "{fn}".')

    with open(fn, 'w') as f:
        f.write(content)

    return True


def basename(f):
    '''
    Calculates the basename of the file f (removes path and extension).

    - f : the path to the file
    '''

    if f[-1] == '/':
        f = f[:-1] # Removing last '/'

    fn = f.split('/')[-1]

    if '.' in fn:
        # find index of the last . :
        index = len(fn) - 1
        for k in range(len(fn) - 1, -1, -1):
            if fn[k] == '.':
                index = k
                break

        # Remove extension
        fn = fn[:index]

    return fn
