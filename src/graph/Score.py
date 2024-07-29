#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.26
# Version           : v1.0.0
#
#--------------------------------

'''Represents the Score node in the graph'''

##-Imports
from src.graph.TopRhythmic import TopRhythmic
from src.graph.Voice import Voice
from src.graph.utils_graph import make_create_string

##-Main
class Score:
    '''Represent an `Score` node'''

    def __init__(self, source: str, id_: str, composer: str, collection: str, voices: list[Voice] = []):
        '''
        Initate Score.

        - source     : the name of the source file ;
        - id_        : the mei id of the 'staffGrp' ;
        - composer   : a string describing the composer ;
        - collection : the collection name ;
        - voices     : the list of voices.
        '''

        self.source = source
        self.id_ = id_
        self.composer = composer
        self.collection = collection
        self.voices = voices

        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.input_file = self.source.replace('.', '_').replace('-', '_').replace('/', '_')
        self.cypher_id = self.id_ + '_' + self.input_file

    def add_voice(self, v: Voice):
        '''
        Adds a voice to the voice list.

        - v : a `Voice` to add.
        '''
    
        self.voices.append(v)

    def to_cypher(self, top_rhythmic: TopRhythmic) -> str:
        '''
        Returns the CREATE cypher clauses that creates the Score node, and its child nodes and links (see `TopRhythmic.to_cypher`).

        Input:
            - top_rhythmic : the TopRhythmic child.

        Order of creation :
            - Score ;
            - TopRhythmic (see `TopRhythmic.to_cypher` for more details) ;
            - Voices.
        '''

        # Create the Score node
        c = make_create_string(self.cypher_id, 'Score', self.__dict__)

        # Create the TopRhythmic
        c += '\n' + top_rhythmic.to_cypher(self.cypher_id)

        # Create voices
        for v in self.voices:
            c += '\n' + v.to_cypher(self.cypher_id, top_rhythmic.cypher_id)

        return c
