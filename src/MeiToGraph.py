#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#--------------------------------
#
# Author            : Lasercata
# Last modification : 2024.07.25
# Version           : v1.0.0
#
#--------------------------------

'''Convert an MEI file to an internal graph representation'''

##-Imports
#---General
import xml.etree.ElementTree as ET

#---Project
from src.utils import log

from src.graph.Score import Score
from src.graph.TopRhythmic import TopRhythmic
from src.graph.Voice import Voice
from src.graph.Measure import Measure
from src.graph.Event import Event
from src.graph.Fact import Fact

##-Util
def remove_namespace_from_string(s: str) -> str:
    '''Removes the '{http://...}' (XML namespace) from the string `s`.'''

    if '{' in s and '}' in s:
        s = s[s.index('}') + 1:]

    return s

def remove_namespace_from_keys(d: dict[str, str]) -> dict[str, str]:
    '''Removes the '{http://...}' from the keys of `d`.'''

    new_d = {}

    for k in d:
        new_d[remove_namespace_from_string(k)] = d[k]

    return d

##-Main
class MeiToGraph:
    '''Convert a MEI file to the internal graph representation, and use this representation to dump the cypher.'''

    def __init__(self, fn, verbose=False):
        '''
        Initiates the MeiToGraph class.

        - fn      : the filename of the MEI file to convert ;
        - verbose : if True, log errors and warnings.
        '''
    
        #---Init from method arguments
        self.fn = fn
        self.verbose = verbose

        #---Init for Score
        self.composer = None
        self.collection = None
        self.score_id = None

        #---Init for parsing
        self.current_measure = None
        self.current_event = None
        self.facts = [] # Used for chords

    def parse_mei(self):
        '''Parses the MEI (XML) and create the graph''' #TODO: write better doc

        chord = False # Flag used to know if the currently read notes are in a chord or standalone.
        voice_def = False # Flag used for voice definition, when the id is not in the 'staffGrp', but in a sublabel.
        current_voice_nb = 0
        current_chord_duration = 0

        for event, elem in ET.iterparse(self.fn, ['start', 'end']):
            tag = remove_namespace_from_string(elem.tag)
            attrib = remove_namespace_from_keys(elem.attrib)

            #---Init
            #-Composer and collection
            if event == 'start' and tag == 'persName':
                self._handle_persName(attrib['role'], elem.text)

            #-Score id
            elif event == 'start' and tag == 'staffGrp':
                if 'id' in attrib:
                    self.score_id = attrib['id']
                else:
                    self.score_id = 'StaffGroup1'

                self._create_score_and_top_rhythmic()

            #-Voices definition
            elif event == 'start' and tag == 'staffDef':
                if 'id' in attrib:
                    self._add_voice(attrib['id'])
                else:
                    voice_def = True # The id is in a label

            elif voice_def and event == 'start' and tag == 'label':
                self._add_voice(elem.text)

            elif voice_def and event == 'end' and tag == 'staffDef':
                voice_def = False

            #---Notes
            #-Measures
            elif event == 'start' and tag == 'measure':
                self._add_measure(attrib['id'])

            #-Voice nb
            elif event == 'start' and tag == 'staff':
                current_voice_nb = int(attrib['n']) # Actualise the current voice number

            #-Chords
            elif event == 'start' and tag == 'chord':
                chord = True
                current_chord_duration = int(attrib['dur'])

            elif event == 'end' and tag == 'chord':
                chord = False

                # Adding all the notes in an Event
                self._add_event_from_facts(attrib['id'], 'note', current_chord_duration, current_voice_nb) #TODO: add verse / syllable

            #-Notes
            elif event == 'start' and tag == 'note':
                # Check accidentals
                accid = None
                accid_ges = None
                if 'accid' in attrib:
                    accid = attrib['accid']
                if 'accid.ges' in attrib:
                    accid_ges = attrib['accid.ges']

                # Create note
                self._add_fact( # Add the note as a Fact
                    attrib['id'],
                    'note',
                    attrib['pname'],
                    int(attrib['oct']),
                    int(attrib['dur']),
                    accid,
                    accid_ges,
                )

                # If it is not a chord, add the Event
                if not chord:
                    self._add_event_from_facts( # Add the Fact in an Event
                        attrib['id'] + '_event',
                        'note',
                        int(attrib['dur']),
                        current_voice_nb
                    ) #TODO: add verse
            
            #-Rest
            elif event == 'start' and tag == 'rest':
                self._add_fact(attrib['id'], 'rest', None, None, int(attrib['dur']), None, None)
                self._add_event_from_facts(attrib['id'] + '_event', 'rest', int(attrib['dur']), current_voice_nb)
            
            #TODO: add first event to voice
            #TODO: add Event 'END' (with no Fact child, type='END')

    def _handle_persName(self, role, text):
        '''
        Handles 'persName' tags found in the mei file (contain collection and composer).

        - role         : the value of the 'role' attribute ;
        - text         : the text ;
        - self.verbose : if True, print when there is an unknow role.
        '''
    
        if role == 'composer':
            self.composer = text

        elif role == 'collection':
            self.collection = text

        elif self.verbose:
            log('warn', f'MeiToGraph: _handle_persName: unknown role: "{role}"')

    def _create_score_and_top_rhythmic(self):
        '''
        Instanciates the `Score` and `TopRhythmic` elments (`self.score` and `self.top_rhythmic`).

        - self.verbose : if True, show warnings if some attributes are not set.
        '''
    
        if self.composer == None:
            self.composer = ''

            if self.verbose:
                log('warn', f'MeiToGraph: _create_score: `self.composer` is not defined')
    
        if self.collection == None:
            self.collection = ''

            if self.verbose:
                log('warn', f'MeiToGraph: _create_score: `self.collection` is not defined')

        self.score = Score(self.fn, self.score_id, self.composer, self.collection, voices=[])
        self.top_rhythmic = TopRhythmic(self.fn, self.composer, self.collection, measures=[])

    def _add_voice(self, id_):
        '''
        Adds a voice to `self.score`.

        - id_ : the voice id.
        '''

        v = Voice(self.fn, id_)
        self.score.add_voice(v)

    def _add_measure(self, id_):
        '''
        Creates and adds a new `Measure` to `self.top_rhythmic`.

        - id_ : the measure id.
        '''

        old_measure = self.current_measure
        self.current_measure = Measure(self.fn, id_, events=[])
        self.top_rhythmic.add_measure(self.current_measure) #TODO: ensure that the measure added here is not a copy (so when events are added, they are added there too)

        #TODO: write on the fly measure per measure ?
        pass # To do this, use old_measure.to_cypher_file() ?

    def _add_fact(self, id_: str, type_: str, class_: str|None, octave: int|None, duration: int, accid: str|None, accid_ges: str|None):
        '''
        Creates and adds a `Fact` to `self.facts`. Called when on tag `note` in a chord.

        - id_       : the mei id of the note ;
        - type_     : either 'note' for a note, or 'rest' for a rest ;
        - class_    : the class of the note (e.g 'c', 'd', ...) ;
        - octave    : the octave of the note ;
        - duration  : the duration of the note (1 for whole, 2 for half, ...) ;
        - accid     : a potential accidental on the note ;
        - accid_ges : a potential accidental on the key.
        '''
    
        #-Create Fact
        f = Fact(self.fn, id_, type_, class_, octave, duration, accid, accid_ges, None) #TODO: syllable.
        self.facts.append(f)

    def _add_event_from_facts(self, id_: str, type_: str, duration: int, voice_nb: int):
        '''
        Creates a new `Event` with all the facts from `self.facts` in it, and add it to the current measure.

        - id_      : the mei id of the note ;
        - type_    : either 'note' for a note, or 'rest' for a rest ;
        - duration : the duration of the note (1 for whole, 2 for half, ...) ;
        - voice_nb : the number of the current voice.
        '''

        #-Set `start` and `end`
        old_event = self.current_event

        if old_event == None:
            start = 0
        else:
            start = old_event.end

        end = start + (1 / duration)

        #-Create Event
        self.current_event = Event(self.fn, id_, type_, duration, start, start, end, facts=self.facts)

        #-Add event to current measure
        if self.current_measure == None:
            raise ValueError('MeiToGraph: _add_event_from_facts: error: note outside of a measure')

        self.current_measure.add_event(self.current_event)

        #-Clear the facts
        self.facts = []

        #-If it is first event, set it as first event of the voice
        #TODO: do not rely on `old_event == None`: will not work if more than one voice
    
        pass

