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
from datetime import datetime as dt


##-Main
def log(lvl: str, msg: str, use_stderr: bool = True):
    '''
    Write msg as a log, in the following format :
        [date time] - Musypher: [level]: [message]

    - lvl (str)         : the level of the message (usually 'info', 'warn', 'error') ;
    - msg (str)         : the message to log ;
    - use_stderr (bool) : if True, write to stderr. Otherwise write to stdout.
    '''

    p = f'{dt.now()} - Musypher: {lvl}: {msg}'

    if use_stderr:
        print(p, file=stderr)
    else:
        print(p)
