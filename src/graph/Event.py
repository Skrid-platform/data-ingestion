#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.25
# Version           : v1.0.0
#
#--------------------------------

'''Represent the Event nodes in the graph'''

##-Imports
from Fact import Fact
# from utils_graph import make_create_string, make_create_link_string
from src.graph.utils_graph import make_create_string, make_create_link_string

##-Main
class Event:
    '''Represent an `Event` node'''

    def __init__(self, source, id_, type_, duration, pos, start, end, facts=[], instrument=None):
        '''
        Initate Event.

        - source     : the name of the source file ;
        - id_        : the id of the fact ;
        - type_      : the type of the fact. Can be 'note', 'rest' ;
        - duration   : the duration of the note (1 for whole, 2 for half, 4 for fourth, ...) ;
        - pos        : ? seems to correspond to `start` ; TODO
        - start      : the start time of the event (1 correspond to a whole, 0.5 to a half note, ...) ;
        - end        : same but for the end of the event ;
        - facts      : the list of facts (notes) ;
        - instrument : the instrument.
        '''

        self.source = source
        self.id_ = id_
        self.type_ = type_
        self.dur = duration
        self.pos = pos
        self.start = start
        self.end = end
        self.facts = facts
        self.instrument = instrument

        self._check();
        self._calculate_other_values();

    def add_fact(self, f: Fact):
        '''
        Adds a fact to the fact list.

        - f : a `Fact` to add.
        '''
    
        self.facts.append(f)

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.input_file = self.source.replace('.mei', '_mei')
        self.cypher_id = self.id_ + '_' + self.input_file

        self.duration = 1 / self.dur

    def _check(self):
        '''
        Ensures that the given attributes make sense.
        Raise a ValueError otherwise.
        '''
    
        if self.type_ not in ('note', 'rest'):
            raise ValueError(f'Fact: `type_` attribute has to be "note" or "rest", but not "{self.type_} !"')

        if type(self.duration) not in (int, float) or self.duration < 0:
            raise ValueError(f'Fact: `duration` attribute has to be a float, but not "{self.duration} !"')

    def to_cypher(self, previous_Event) -> str:
        '''
        Returns the CREATE cypher clauses, with the ones for the facts and the links

        Input:
            - previous_Event: the previous Event. If this is the first Event, pass None instead (it is Voice that will link here, and it will be done in Voice).

        Order of creation :
            - Event ;
            - Fact ... ;
            - Links to Facts (:IS) ;
            - Link to previous Event (:NEXT) (from previous to current).

        There is a link missing (:HAS) : from Measure to Event. But it will be created by `Measure`.
        '''

        # Create the Event node
        c = make_create_string(self.cypher_id, 'Event', self.__dict__)

        # Create the facts
        for f in self.facts:
            c += '\n' + f.to_cypher()

        # Create the links to facts
        for f in self.facts:
            c += '\n' + make_create_link_string(self.cypher_id, f.cypher_id, 'IS')

        # Create link to previous Event
        if previous_Event != None:
            c += '\n' + make_create_link_string(previous_Event.cypher_id, self.cypher_id, 'NEXT', {'duration': previous_Event.duration})
    
        return c
