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

    def __init__(self, source: str, id_: str, events: list[list[Event]] = []):
        '''
        Initate Measure.

        - source     : the name of the source file ;
        - id_        : the mei id of the Measure node ;
        - events     : the list of list of `Event`s : events[i][j] is the j-th event from the i-th voice in this measure.
        '''

        self.source = source
        self.id_ = id_
        self.events = events

        self._calculate_other_values();

    def _calculate_other_values(self):
        '''Calculate the other needed values.'''

        self.inputfile = self.source.replace('.', '_').replace('-', '_').replace('/', '_')
        self.cypher_id = self.id_ + '_' + self.inputfile

        self.number = Measure.n
        Measure.n += 1;

    def add_event(self, e: Event, voice_nb: int):
        '''
        Adds an event to the event list.

        - e        : an `Event` to add ;
        - voice_nb : the number of the voice to which the event is in (begin at 1, not at 0).
        '''

        voice_index = voice_nb - 1

        while len(self.events) < voice_index + 1: # Adding potentially missing voices
            self.events.append([])
    
        self.events[voice_index].append(e) # Adding the event in its voice

    def to_cypher(self, parent_cypher_id: str, previous_Measures=[]) -> str:
        '''
        Returns the CREATE cypher clauses, that creates the Measure node, its child nodes and links (see `Event.to_cypher`),
        and the link from the previous Measure (if it exists).

        Input:
            - parent_cypher_id  : the cypher id of the parent (a `TopRhythmic`) ;
            - previous_Measures : the list of previous Measures, excluding the current one.

        The list of previous measures is needed because it is possible that there is no notes in a measure for a voice, so to link the first event with the last one, we need to check all the way to the first measure (in the worst case)

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
        for voice_index, events_of_voice in enumerate(self.events):
            for k, e in enumerate(events_of_voice):
                if k == 0: # This is the first event of the measure
                    # Try to get the last event (which can not be in the last measure, but futher than that)
                    i = -1 # Previous measure index
                    while (-len(previous_Measures) <= i and len(previous_Measures[i].events) <= voice_index):
                        i -= 1

                    if i < -len(previous_Measures):
                        prev = None
                    else:
                        prev = previous_Measures[i].events[voice_index][-1]

                else: # There is a previous Event in this measure
                    prev = self.events[voice_index][k - 1]

                c += '\n' + e.to_cypher(self.cypher_id, prev)

        # Create link to previous Measure
        if len(previous_Measures) > 1:
            c += '\n' + make_create_link_string(previous_Measures[-1].cypher_id, self.cypher_id, 'NEXTMeasure')
    
        return c
