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

##-Main
class Fact:
    '''Represent a `Fact` node (note)'''

    def __init__(self, source: str, id_: str, type_: str, class_: str|None, octave: int|None, duration: int, accid: str|None = None, accid_ges: str|None = None, syllable: str|None = None, instrument: str|None = None):
        '''
        Initate Fact.

        - source     : the name of the source file ;
        - id_        : the id of the fact ;
        - type_      : the type of the fact. Can be 'note', 'rest' ;
        - class_     : the class of the note (e.g 'c', 'd', ...). Set it to None for a rest ;
        - octave     : the octave of the note ;
        - duration   : the duration of the note (1 for whole, 2 for half, 4 for fourth, ...) ;
        - accid      : None if no accidental on the note, 's' for sharp, and 'f' for flat ;
        - accid_ges  : same as above, but represent an accidental on the staff, not on the note ;
        - syllable   : the potential syllable pronounced on this note (None if none) ;
        - instrument : the instrument.
        '''

        self.source = source
        self.id_ = id_
        self.type_ = type_
        self.class_ = class_
        self.octave = octave
        self.dur = duration
        self.accid = accid
        self.accid_ges = accid_ges
        self.syllable = syllable
        self.instrument = instrument

        self._check();
        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.input_file = self.source.replace('.', '_').replace('-', '_').replace('/', '_')
        self.cypher_id = self.id_ + '_' + self.input_file

        if self.class_ != None:
            self.name = self.class_.upper() + str(self.octave)

        if self.type_ != 'END':
            self.duration = 1 / self.dur

        #TODO: calculate frequency, half_tones_from_a4, half_tones_diatonic_from_a4, alteration_in_tones, alteration_in_half_tones.

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

        if type(self.octave) != int or self.octave < 0 or self.octave > 9: #TODO: I am not certain of the boundaries
            raise ValueError(f'Fact: `octave` attribute has to be an int, but not "{self.octave} !"')

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

