#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.26
# Version           : v1.0.0
#
#--------------------------------

'''Represent the Event nodes in the graph'''

##-Imports
from src.graph.Fact import Fact
from src.graph.utils_graph import make_create_string, make_create_link_string

from src.utils import calculate_note_interval, log

##-Main
class Event:
    '''Represent an `Event` node'''

    def __init__(self, source: str, id_: str, type_: str, duration: int, dots: int, pos: float, start: float, end: float, facts: list[Fact] = [], voice_nb: int = 1, instrument: str|None = None):
        '''
        Initate Event.

        - source     : the name of the source file ;
        - id_        : the mei id of the Event node ;
        - type_      : the type of the fact. Can be 'note', 'rest' ;
        - duration   : the duration of the note (1 for whole, 2 for half, 4 for fourth, ...) ;
        - dots       : the number of dots on the note ;
        - pos        : ? seems to correspond to `start` ; TODO
        - start      : the start time of the event (1 correspond to a whole, 0.5 to a half note, ...) ;
        - end        : same but for the end of the event ;
        - facts      : the list of facts (notes) ;
        - voice_nb   : the number of the voice in which the event takes place (starts from 1, not from 0) ;
        - instrument : the instrument.
        '''

        self.source = source
        self.id_ = id_
        self.type_ = type_
        self.dur = duration # self.dur is 1, 2, 4, ... and self.duration will 1, .5, .25, ... (latter calculated later in _calculate_other_values).
        self.dots = dots
        self.pos = pos
        self.start = start
        self.end = end
        self.facts = facts
        self.instrument = instrument
        self.voice_nb = voice_nb

        self._check();
        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.inputfile = self.source.replace('.', '_').replace('-', '_').replace('/', '_')
        self.cypher_id = self.id_ + '_' + self.inputfile

        if self.type_ != 'END':
            self.duration = 1 / self.dur

            # Adding the duration of the dots to `self.duration`
            for k in range(self.dots):
                self.duration += 1 / (self.dur * pow(2, k + 1))

    def _check(self):
        '''
        Ensures that the given attributes make sense.
        Raise a ValueError otherwise.
        '''
    
        if self.type_ not in ('note', 'rest', 'END'):
            raise ValueError(f'Fact: `type_` attribute has to be "note", "rest" or "END", but not "{self.type_}" !')

        if type(self.dur) != int or self.dur < 0:
            raise ValueError(f'Fact: `duration` attribute has to be a float, but not "{self.duration}" !')

        if type(self.dots) != int or self.dots < 0:
            raise ValueError(f'Fact: `dots` should be a positive int, but "{self.dots}" found !')

    def add_fact(self, f: Fact):
        '''
        Adds a fact to the fact list.

        - f : a `Fact` to add.
        '''
    
        self.facts.append(f)

    def to_cypher(self, parent_cypher_id: str, previous_Event=None) -> str:
        '''
        Returns the CREATE cypher clauses, that creates the Event node, the child Fact nodes,
        the links to those Fact nodes and the link from the previous Event (if it exists).

        Input:
            - parent_cypher_id : the cypher id of the parent (a `Measure`) ;
            - previous_Event   : the previous Event. If this is the first Event, pass None instead (it is Voice that will link here, and it will be done in Voice).

        Order of creation :
            - Event ;
            - Link from parent (Measure) to this Event (:HAS) ;
            - Facts (see `Facts.to_cypher` for more details) ;
            - Link from previous Event (:NEXT).
        '''

        # Create the Event node
        c = make_create_string(self.cypher_id, 'Event', self.__dict__)

        # Create the link from parent (Measure) to this node (Event)
        c += '\n' + make_create_link_string(parent_cypher_id, self.cypher_id, 'HAS')

        # Create the facts
        for f in self.facts:
            c += '\n' + f.to_cypher(self.cypher_id)

        # Create link to previous Event
        if previous_Event != None:
            data = {'duration': previous_Event.duration}

            # Calculate interval
            if len(previous_Event.facts) > 0 and len(self.facts) > 0:
                f1 = previous_Event.facts[0]
                f2 = self.facts[0]

                if f1.type_ == 'note' and f2.type_ == 'note':
                    interval = calculate_note_interval(f1.class_, f1.octave, f2.class_, f2.octave) / 2
                    data['interval'] = interval

                if f2.duration != 0:
                    data['duration_ratio'] = f2.duration / f1.duration
                elif self.verbose:
                    log('warn', f'Event.to_cypher: f2.duration is zero for event {self.id}, cannot compute duration_ratio.')

            c += '\n' + make_create_link_string(previous_Event.cypher_id, self.cypher_id, 'NEXT', data)
    
        return c
