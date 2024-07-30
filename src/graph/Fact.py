#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.26
# Version           : v1.0.0
#
#--------------------------------

'''Represent the Fact nodes in the graph (notes)'''

##-Import
from src.graph.utils_graph import make_create_string, make_create_link_string
from src.utils import calculate_note_interval, get_frequency

##-Main
class Fact:
    '''Represent a `Fact` node (note)'''

    def __init__(self, source: str, id_: str, type_: str, class_: str|None, octave: int|None, duration: int, dots: int = 0, accid: str|None = None, accid_ges: str|None = None, syllable: str|None = None, grace: str|None = None, instrument: str|None = None):
        '''
        Initate Fact.

        - source     : the name of the source file ;
        - id_        : the id of the fact ;
        - type_      : the type of the fact. Can be 'note', 'rest' ;
        - class_     : the class of the note (e.g 'c', 'd', ...). Set it to None for a rest ;
        - octave     : the octave of the note ;
        - duration   : the duration of the note (1 for whole, 2 for half, 4 for fourth, ...) ;
        - dots       : the number of dots on the note ;
        - accid      : None if no accidental on the note, 's' for sharp, and 'f' for flat ;
        - accid_ges  : same as above, but represent an accidental on the staff, not on the note ;
        - syllable   : the potential syllable pronounced on this note (None if none) ;
        - grace      : if not None, indicate that the note is a grace note, and give its type (often 'acc') ;
        - instrument : the instrument.
        '''

        self.source = source
        self.id_ = id_
        self.type_ = type_
        self.class_ = class_
        self.octave = octave
        self.dur = duration # self.dur is 1, 2, 4, ... and self.duration will 1, .5, .25, ... (latter calculated later in _calculate_other_values).
        self.dots = dots
        self.accid = accid
        self.accid_ges = accid_ges
        self.syllable = syllable
        self.grace = grace
        self.instrument = instrument

        self._check();
        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.inputfile = self.source.replace('.', '_').replace('-', '_').replace('/', '_')
        self.cypher_id = self.id_ + '_' + self.inputfile

        if self.class_ != None:
            self.name = self.class_.upper() + str(self.octave)

        if self.type_ != 'END':
            self.duration = 1 / self.dur

            # Adding the duration of the dots to `self.duration`
            for k in range(self.dots):
                self.duration += 1 / (self.dur * pow(2, k + 1))

        if self.type_ == 'note' and self.class_ != None and self.octave != None:
            self.frequency = get_frequency(self.class_, self.octave)
            self.halfTonesFromA4 = calculate_note_interval('a', 4, self.class_, self.octave) # But is this useful ?

    def _check(self):
        '''
        Ensures that the given attributes make sense.
        Raise a ValueError otherwise.
        '''
    
        if self.type_ not in ('note', 'rest', 'END'):
            raise ValueError(f'Fact: `type_` attribute has to be "note", "rest", or "END", but not "{self.type_}" !')

        if type(self.dur) != int or self.dur < 0:
            raise ValueError(f'Fact: `duration` attribute has to be a float, but not "{self.duration}" !')

        if self.type_ == 'rest':
            return # None of the following tests are relevent for a rest note

        if self.class_ == None or (self.type_ == 'note' and self.class_ not in 'abcdefg'):
            raise ValueError(f'Fact: `class_` attribute has to be in (a, b, c, d, e, f, g), but not "{self.class_}" !')

        if type(self.octave) != int or self.octave < 0 or self.octave > 9:
            raise ValueError(f'Fact: `octave` attribute has to be an int, but not "{self.octave} !"')

        if type(self.dots) != int or self.dots < 0:
            raise ValueError(f'Fact: `dots` should be a positive int, but "{self.dots}" found !')

        if self.accid not in (None, 's', 'f'):
            raise ValueError(f'Fact: `accid` attribute has to be in (None, "s", "f"), but "{self.accid}" was found !')

        if self.accid_ges not in (None, 's', 'f'):
            raise ValueError(f'Fact: `accid_ges` attribute has to be in (None, "s", "f"), but "{self.accid_ges}" was found !')

    def to_cypher(self, parent_cypher_id: str) -> str:
        '''Returns the CREATE cypher clause that creates the Fact node and the link from its Event parent.'''
    
        # Create Fact node
        c = make_create_string(self.cypher_id, 'Fact', self.__dict__)

        # Create link from parent (Event)
        c += '\n' + make_create_link_string(parent_cypher_id, self.cypher_id, 'IS')

        return c

