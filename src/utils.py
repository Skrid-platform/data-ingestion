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

# from src.graph.Fact import Fact

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
notes_semitones = ('c', 'c#', 'd', 'd#', 'e', 'f', 'f#', 'g', 'g#', 'a', 'a#', 'b')
accid_semitones = {
    's': 1,
    '#': 1,
    'b': -1,
    'n': 0,
    'x': 2,
    'bb': -2
}

def convert_note_to_sharp(class_and_accid: str, octave: int) -> tuple[str, int]:
    '''
    Convert a note to it enharmonically equivalent with a sharp accidental (represented as `#`).
    If the note has no accidental, no conversion is made.

    In:
        - class_and_accid: the class of the note, with a potential accidental (e.g `c`, `c#`)
        - octave: the octave of the note
    Out:
        (class, octave): the note, converted with a sharp notation
    '''

    if len(class_and_accid) == 1: # No accidental
        return class_and_accid, octave

    class_ = class_and_accid[0]
    accid = class_and_accid[1:]

    new_semitones = notes_semitones.index(class_) + accid_semitones[accid]
    new_class = notes_semitones[new_semitones % len(notes_semitones)]
    new_oct = octave + new_semitones // len(notes_semitones)

    return new_class, new_oct

def calculate_note_interval(class_1: str, octave_1: int, class_2: str, octave_2: int) -> int:
    '''
    Calculates the distance between (`class_1`, `octave_1`) and (`class_2`, `octave_2`), in *semitones*.

    - class_1  : the note class of the first note (e.g 'c', 'cs', 'c#', ...) ;
    - octave_1 : the octave of the first note ;
    - class_2  : the note class of the second note ;
    - octave_2 : the octave of the second note.

    Output : *signed semitone* distance between the two notes.
    '''

    #---Convert to sharp
    c1, o1 = convert_note_to_sharp(class_1, octave_1)
    c2, o2 = convert_note_to_sharp(class_2, octave_2)

    #---Calculate interval
    return 12 * (o2 - o1) + notes_semitones.index(c2) - notes_semitones.index(c1)

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

def get_lowest_fact(facts: list['Fact']) -> 'Fact':
    '''
    Returns the fact with the lowest pitch.
    If there is only one fact, it is returned.

    In:
        - facts: the list of facts
    Out:
        the fact with the lowest pitch
    '''

    if len(facts) == 1:
        return facts[0]

    frequencies: dict[float, Fact] = {}
    for f in facts:
        if f.class_ != None and f.octave != None:
            freq = get_frequency(f.class_, f.octave)
            frequencies[freq] = f

    return frequencies[min(frequencies.keys())]
