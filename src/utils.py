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
import unicodedata
import re

##-IO
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
    Calculates the basename of the file f (removes path and extension),
    and normalizes it to be safe for filenames (ASCII only).

    - f : the path to the file
    '''

    if f[-1] == '/':
        f = f[:-1]  # Removing last '/'

    fn = f.split('/')[-1]

    if '.' in fn:
        # find index of the last . :
        index = len(fn) - 1
        for k in range(len(fn) - 1, -1, -1):
            if fn[k] == '.':
                index = k
                break
        fn = fn[:index]  # Remove extension

    # 🔽 Normalize filename to ASCII-safe
    nfkd_form = unicodedata.normalize('NFKD', fn)
    ascii_encoded = nfkd_form.encode('ASCII', 'ignore').decode('ASCII')
    safe = re.sub(r'[^a-zA-Z0-9_\-\.]', '_', ascii_encoded)

    return safe

##-Music
def convert_note_to_sharp(note: str) -> str:
    '''
    Convert a note to its equivalent in sharp (if it is a flat).
    If the note has no accidental, it is not modified.

    - note : a string of length 1 or 2 representing a musical note class (no octave).
             Sharp can be represented either with 's' or '#'.
             Flat can be represented either with 'f' of 'b'.

    Output: `note` with sharp represented as '#', or `note` unchanged if there was no accidental.
    '''

    notes = 'abcdefg'

    note = note.replace('s', '#')
    if len(note) == 2 and note[1] in ('f', 'b'):
        note = notes[(notes.index(note[0]) - 1) % len(notes)] + '#' # Convert flat to sharp

    return note

def calculate_note_interval(class_1: str, octave_1: int, class_2: str, octave_2: int) -> int:
    '''
    Calculates the distance between (`class_1`, `octave_1`) and (`class_2`, `octave_2`), in semitones.

    - class_1  : the note class of the first note (e.g 'c', 'cs', 'c#', ...) ;
    - octave_1 : the octave of the first note ;
    - class_2  : the note class of the second note ;
    - octave_2 : the octave of the second note.

    Output : signed semitone distance between the two notes.
    '''

    #---Init
    notes = ['c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b']

    #---Convert to sharp
    c1 = convert_note_to_sharp(class_1)
    c2 = convert_note_to_sharp(class_2)

    #---Calculate interval
    return 12 * (octave_2 - octave_1) + notes.index(c2) - notes.index(c1)

def get_frequency(class_: str, octave: int) -> float:
    '''
    Return the frequency of the given note (in Hz).

    - class_ : the note class (e.g 'c', 'cs', 'c#', ...) ;
    - octave : the octave of the note.
    '''

    #---Init
    #-Constants
    base_freq = 440
    base_note = 'a'
    base_octave = 4

    #-Note to frequency
    f = lambda f0, n: f0 * pow(2, n / 12) # with f0 the frequency of the note p, f(f0, n) is the frequency of the note n semitones above p.

    #---Calculate frequency
    n = calculate_note_interval(base_note, base_octave, class_, octave)
    return f(base_freq, n)
