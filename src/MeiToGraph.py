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
from src.utils import log, write_file

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

    return new_d

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

        self.fn_without_path = fn.split('/')[-1]

        #---Init for Score
        self.composer = None
        self.collection = None
        self.score_id = None

        self.score = None

        #---Init for parsing
        self.current_measure = None
        self.current_events = [] # self.current_events[k] is the current event for the voice k + 1
        self.facts = [] # Used for chords

    def parse_mei(self):
        '''Parses the MEI (XML) to create the graph with the internal representation.'''

        chord = False # Flag used to know if the currently read notes are in a chord or standalone.
        voice_def = False # Flag used for voice definition, when the id is not in the 'staffGrp', but in a sublabel.
        current_voice_nb = 0
        current_chord_duration = 0
        current_syllable = None # Used to store syllables. None when there is no syllable for the current note.

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
                    voice_def = True # The id is in a label, see below

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
                self._add_event_from_facts(attrib['id'], 'note', current_chord_duration, None, current_voice_nb)

            #-Notes
            elif event == 'end' and tag == 'note': # Parsing on end to have syllables already seen
                # Check accidentals
                accid = None
                accid_ges = None
                if 'accid' in attrib:
                    accid = attrib['accid']
                if 'accid.ges' in attrib:
                    accid_ges = attrib['accid.ges']

                # Get duration
                if chord:
                    duration = current_chord_duration
                else:
                    duration = int(attrib['dur'])

                # Get dots
                dots = 0
                if 'dots' in attrib:
                    try:
                        dots = int(attrib['dots'])
                    except ValueError as err:
                        log('err', f'MeiToGraph: parse_mei: adding note: dots: error when trying to convert dot value to int. Dots will be set to 0 for this note.\nCurrent file : "{self.fn}".\nCurrent note id : "{attrib["id"]}".')

                # Get grace status
                grace = None
                if 'grace' in attrib:
                    grace = attrib['grace']

                # Create note
                self._add_fact( # Add the note as a Fact
                    attrib['id'] + '_fact',
                    'note',
                    attrib['pname'],
                    int(attrib['oct']),
                    duration,
                    dots,
                    accid,
                    accid_ges,
                    current_syllable,
                    grace
                )

                # Reset current syllable
                current_syllable = None

                # If it is not a chord, add the Event
                if not chord:
                    self._add_event_from_facts( # Add the Fact in an Event
                        attrib['id'],
                        'note',
                        int(attrib['dur']),
                        dots,
                        current_voice_nb
                    )

            #-Syllables
            elif event == 'start' and tag == 'syl':
                current_syllable = elem.text
            
            #-Rest
            elif event == 'start' and tag == 'rest':
                # Get dots
                dots = 0
                if 'dots' in attrib:
                    try:
                        dots = int(attrib['dots'])
                    except ValueError as err:
                        log('err', f'MeiToGraph: parse_mei: adding rest: dots: error when trying to convert dot value to int. Dots will be set to 0 for this rest.\nCurrent file : "{self.fn}".\nCurrent rest id : "{attrib["id"]}".')

                # Add note fact and event
                self._add_fact(attrib['id'] + '_fact', 'rest', None, None, int(attrib['dur']), dots, None, None, None, None)
                self._add_event_from_facts(attrib['id'], 'rest', int(attrib['dur']), dots, current_voice_nb)
            
        self._add_last_events()

    def to_file(self, out_fn: str, no_confirmation: bool = False) -> bool:
        '''
        Convert the internal graph to a cypher dump, and write it to a file.

        If the `self.parse_mei` method has already been called (so `self.score` is not None), it does not call it again.
        Otherwise, it calls the method (so it is not needed to call `parse_mei` before calling this method).

        Return :
            - True  if the file has been written
            - False otherwise.

        - out_fn          : the filename where to write the output ;
        - no_confirmation : if True, do not ask for confirmation to overwrite the file if it already exists.
        '''
    
        if self.score == None:
            self.parse_mei()

        dump = self.score.to_cypher(self.top_rhythmic)
        return write_file(out_fn, dump, no_confirmation, self.verbose)

    #TODO: def dump(self, uri: str, user: str, pwd: str)

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
            if self.composer != None:
                self.collection = self.composer
                if self.verbose:
                    log('warn', f'MeiToGraph: _create_score: ({self.fn}): using `composer` instead of `collection` as the latter does not exists in the file')
            else:
                self.collection = ''

                if self.verbose:
                    log('warn', f'MeiToGraph: _create_score: ({self.fn}): `self.collection` is not defined')

        self.top_rhythmic = TopRhythmic(self.fn_without_path, self.composer, self.collection, measures=[])
        self.score = Score(self.fn_without_path, self.score_id, self.composer, self.collection, voices=[])

    def _add_voice(self, id_):
        '''
        Adds a voice to `self.score`.

        - id_ : the voice id.
        '''

        v = Voice(self.fn_without_path, id_) # Create the voice
        self.score.add_voice(v) # Add it to the voice list

        self.current_events.append(None) # Add an empty event in the current events list for this new voice

    def _add_measure(self, id_):
        '''
        Creates and adds a new `Measure` to `self.top_rhythmic`.

        - id_ : the measure id.
        '''

        old_measure = self.current_measure
        self.current_measure = Measure(self.fn_without_path, id_, events=[])
        self.top_rhythmic.add_measure(self.current_measure)

    def _add_fact(self, id_: str, type_: str, class_: str|None, octave: int|None, duration: int, dots: int, accid: str|None, accid_ges: str|None, syllable: str|None, grace: None|str):
        '''
        Creates and adds a `Fact` to `self.facts`. Called when on tag `note` in a chord.

        - id_       : the mei id of the note ;
        - type_     : either 'note' for a note, or 'rest' for a rest ;
        - class_    : the class of the note (e.g 'c', 'd', ...) ;
        - octave    : the octave of the note ;
        - duration  : the duration of the note (1 for whole, 2 for half, ...) ;
        - dots      : the number of dots on the note ;
        - accid     : a potential accidental on the note ;
        - accid_ges : a potential accidental on the key ;
        - syllable  : the potential syllable attatched to a note ;
        - grace     : If not None, indicate that the note is a grace note, and give its type.
        '''
    
        #-Create Fact
        f = Fact(self.fn_without_path, id_, type_, class_, octave, duration, dots, accid, accid_ges, syllable, grace)
        self.facts.append(f)

    def _add_event_from_facts(self, id_: str, type_: str, duration: int, dots: int|None, voice_nb: int):
        '''
        Creates a new `Event` with all the facts from `self.facts` in it, and add it to the current measure.

        - id_      : the mei id of the note ;
        - type_    : either 'note' for a note, or 'rest' for a rest ;
        - duration : the duration of the note (1 for whole, 2 for half, ...) ;
        - dots     : the number of dots on the note. For a chord, None is given, and it is retreived using the max from facts ;
        - voice_nb : the number of the current voice. First voice is number 1 (not 0).
        '''

        voice_index = voice_nb - 1

        #-Set `start` and `end`
        old_event = self.current_events[voice_index]

        if old_event == None:
            start = 0
        else:
            start = old_event.end

        if duration == 0:
            end = None # Last event
        else:
            end = start + (1 / duration)

        #-Get dots
        if dots == None:
            dots = 0

            for f in self.facts:
                if f.dots > dots:
                    dots = f.dots

        #-Create Event
        self.current_events[voice_index] = Event(self.fn_without_path, id_, type_, duration, dots, start, start, end, facts=self.facts, voice_nb=voice_nb)

        #-Add event to current measure
        if self.current_measure == None:
            raise ValueError('MeiToGraph: _add_event_from_facts: error: note outside of a measure')

        self.current_measure.add_event(self.current_events[voice_index], voice_nb)

        #-Clear the facts
        self.facts = []

        #-If it is first event of the current voice, set it as first event of the voice
        if voice_index > len(self.score.voices):
            raise ValueError(f'MeiToGraph: _add_event_from_facts: error with `voice_nb`: too large (number of voices : {len(self.score.voices)}, but `voice_nb` was set to {voice_nb})')

        if not self.score.voices[voice_index].is_first_event_set():
            self.score.voices[voice_index].set_event(self.current_events[voice_index])

    def _add_last_events(self):
        '''
        Adds the last event for each voice.
        Also reset `Voice.n` and `Measure.n`.
        '''
    
        for k in range(len(self.current_events)):
            self._add_event_from_facts(f'END_voice_{k + 1}', 'END', 0, 0, k + 1)

        # Reset counter
        Voice.n = 1
        Measure.n = 1

