#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.26
# Version           : v1.0.0
#
#--------------------------------

'''Represent the Voices nodes in the graph'''

##-Imports
from src.graph.Event import Event
from src.graph.utils_graph import make_create_string, make_create_link_string

##-Main
class Voice:
    '''Represent an `Voice` node'''

    n = 1 # Used as a staff counter

    def __init__(self, source: str, id_: str, first_event: Event|None = None):
        '''
        Initate Voice.

        - source      : the name of the source file ;
        - id_         : the mei id of the Voice node ;
        - first_event : the first event of this voice.
        '''

        self.source = source
        self.id_ = id_.replace(' ', '_')
        self.first_event = first_event

        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.input_file = self.source.replace('.', '_').replace('-', '_')
        self.cypher_id = self.id_ + '_' + self.input_file

        self.staff_number = Voice.n
        Voice.n += 1;

    def set_event(self, e: Event):
        '''
        Sets `e` as the first event for this voice.

        - e : the `Event` to set as first of this voice.
        '''
    
        self.first_event = e

    def to_cypher(self, parent_cypher_id: str, top_rhythmic_cypher_id: str) -> str:
        '''
        Returns the CREATE cypher clauses, that creates the Voice node, its child nodes and links (see `Event.to_cypher`),
        and the link from the previous Voice (if it exists).

        Input:
            - parent_cypher_id       : the cypher id of the parent (the `Score`) ;
            - top_rhythmic_cypher_id : the cypher id of the `TopRhythmic`.

        Order of creation :
            - Voice ;
            - Link from parent (Score) to this Voice (:VOICE) ;
            - Link from this Voice to TopRhythmic (:RHYTHMIC) ;
            - Links from this Voice to the first event (:PLAYS and :timeSeries).
        '''

        # Create the Voice node
        c = make_create_string(self.cypher_id, 'Voice', self.__dict__)

        # Create the link from parent (Score) to this node (Voice)
        c += '\n' + make_create_link_string(parent_cypher_id, self.cypher_id, 'VOICE')

        # Create the link to TopRhythmic
        c += '\n' + make_create_link_string(self.cypher_id, top_rhythmic_cypher_id, 'RHYTHMIC')

        # Create the links to the first event
        if self.first_event == None:
            raise ValueError('Voice: to_cypher: `self.cypher_id` was not initialized !')

        c += '\n' + make_create_link_string(self.cypher_id, self.first_event.cypher_id, 'PLAYS')
        c += '\n' + make_create_link_string(self.cypher_id, self.first_event.cypher_id, 'timeSeries')
    
        return c
