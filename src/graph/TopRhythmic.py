#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.26
# Version           : v1.0.0
#
#--------------------------------

'''Represent the TopRhythmic node in the graph'''

##-Imports
from Measure import Measure
from src.graph.utils_graph import make_create_string, make_create_link_string

##-Main
class TopRhythmic:
    '''Represent an `TopRhythmic` node'''

    def __init__(self, source: str, composer: str, collection: str, measures: list[Measure] = []):
        '''
        Initate TopRhythmic.

        - source     : the name of the source file ;
        - composer   : a string describing the composer ;
        - collection : the collection name ;
        - measures   : the list of `Measure`s ;
        '''

        self.source = source
        self.composer = composer
        self.collection = collection
        self.id_ = 'top'
        self.measures = measures
        self.name = 'topRhythmic'

        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.input_file = self.source.replace('.', '_').replace('-', '_')
        self.cypher_id = self.id_ + '_' + self.input_file

    def add_measure(self, m: Measure):
        '''
        Adds a measure to the measure list.

        - m : a `Measure` to add.
        '''
    
        self.measures.append(m)

    def to_cypher(self, score_cypher_id: str) -> str:
        '''
        Returns the CREATE cypher clauses, that creates the TopRhythmic node, its child nodes and links (see `Measure.to_cypher`).

        Input:
            - score_cypher_id : the cypher id of the Score parent (not the `Voice`s).

        Order of creation :
            - TopRhythmic ;
            - Link from Score parent (:RHYTHMIC) ;
            - Measures (see `Measure.to_cypher` for more details) ;
        '''

        # Create the TopRhythmic node
        c = make_create_string(self.cypher_id, 'TopRhythmic', self.__dict__)

        # Create the link from Score parent
        c += '\n' + make_create_link_string(score_cypher_id, self.cypher_id, 'RHYTHMIC')

        # Create the measures
        for k, m in enumerate(self.measures):
            if k == 0:
                prev = None
            else:
                prev = self.measures[k - 1]

            c += '\n' + m.to_cypher(self.cypher_id, prev)

        return c
