#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.26
# Version           : v1.0.0
#
#--------------------------------

'''Represent the Measure nodes in the graph'''

##-Imports
from src.graph.Event import Event
from src.graph.utils_graph import make_create_string, make_create_link_string

##-Main
class Measure:
    '''Represent an `Measure` node'''

    n = 1 # Used as a counter

    def __init__(self, source: str, id_: str, events: list[Event] = []):
        '''
        Initate Measure.

        - source     : the name of the source file ;
        - id_        : the mei id of the Measure node ;
        - events     : the list of `Event`s ;
        '''

        self.source = source
        self.id_ = id_
        self.events = events

        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.input_file = self.source.replace('.', '_').replace('-', '_')
        self.cypher_id = self.id_ + '_' + self.input_file

        self.number = Measure.n
        Measure.n += 1;

    def add_event(self, e: Event):
        '''
        Adds an event to the event list.

        - e : an `Event` to add.
        '''
    
        self.events.append(e)

    def to_cypher(self, parent_cypher_id: str, previous_Measure=None) -> str:
        '''
        Returns the CREATE cypher clauses, that creates the Measure node, its child nodes and links (see `Event.to_cypher`),
        and the link from the previous Measure (if it exists).

        Input:
            - parent_cypher_id : the cypher id of the parent (a `TopRhythmic`) ;
            - previous_Measure: the previous Measure. If this is the first Measure, pass None instead.

        Order of creation :
            - Measure ;
            - Link from parent (TopRhythmic) to this Measure (:RHYTHMIC) ;
            - Events (see `Event.to_cypher` for more details) ;
            - Link from previous Measure (:NEXTMeasure).
        '''

        # Create the Measure node
        c = make_create_string(self.cypher_id, 'Measure', self.__dict__)

        # Create the link from parent (TopRhythmic) to this node (Measure)
        c += '\n' + make_create_link_string(parent_cypher_id, self.cypher_id, 'RHYTHMIC')

        # Create the events
        for k, e in enumerate(self.events):
            if k == 0:
                prev = None
            else:
                prev = self.events[k - 1]

            c += '\n' + e.to_cypher(self.cypher_id, prev)

        # Create link to previous Measure
        if previous_Measure != None:
            c += '\n' + make_create_link_string(previous_Measure.cypher_id, self.cypher_id, 'NEXTMeasure')
    
        return c
