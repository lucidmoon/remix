#!/usr/bin/env python
# encoding: utf=8

"""
step-by-section.py

For each bar, take one of the nearest (in timbre) beats 
to the last beat, chosen from all of the beats that fall
on the one in this section. Repeat for all the twos, etc.

This version divides things by section, retaining the 
structure and approximate length of the original. The 
variation parameter, (_v_) means there's a roughly 
one in _v_ chance that the actual next beat is chosen. A 
musical M-x dissociated-press.

Originally by Adam Lindsay, 2009-03-10.
"""
import random

import echonest.audio as audio
from echonest.sorting import *
from echonest.selection import *

usage = """
Usage:
    python step-by-section.py inputFilename outputFilename [variation]

variation is the number of near candidates chosen from. [default=4]

Example:
    python step-by-section.py Discipline.mp3 Displicine.mp3 6
"""
def main(infile, outfile, choices=4):
    audiofile = audio.LocalAudioFile(infile)
    meter = audiofile.analysis.time_signature['value']
    fade_in = audiofile.analysis.end_of_fade_in
    fade_out = audiofile.analysis.start_of_fade_out
    sections = audiofile.analysis.sections.that(overlap_range(fade_in, fade_out))
    outchunks = audio.AudioQuantumList()

    for section in sections:
        print str(section) + ":"
        beats = audiofile.analysis.beats.that(are_contained_by(section))
        segments = audiofile.analysis.segments.that(overlap(section))
        num_bars = len(section.children())
        
        print "\t", len(beats), "beats,", len(segments), "segments"
        if len(beats) < meter:
            continue
        
        b = []
        segstarts = []
        for m in range(meter):
            b.append(beats.that(are_beat_number(m)))
            segstarts.append(segments.that(overlap_starts_of(b[m])))
        
        if not b:
            continue
        elif not b[0]:
            continue
        
        now = b[0][0]
        
        for x in range(0, num_bars * meter):
            beat = x % meter
            next_beat = (x + 1) % meter
            now_end_segment = segments.that(contain_point(now.end))[0]
            next_candidates = segstarts[next_beat].ordered_by(timbre_distance_from(now_end_segment))
            if not next_candidates:
                continue
            next_choice = next_candidates[random.randrange(min(choices, len(next_candidates)))]
            next = b[next_beat].that(start_during(next_choice))[0]
            outchunks.append(now)
            print "\t" + now.context_string()
            now = next
    
    out = audio.getpieces(audiofile, outchunks)
    out.encode(outfile)
    
    
def are_beat_number(beat):
    def fun(x):        
        if x.local_context()[0] == beat:
            return x
    return fun

#
if __name__ == '__main__':
    import sys
    try:
        inputFilename = sys.argv[1]
        outputFilename = sys.argv[2]
        if len(sys.argv) > 3:
            variation = int(sys.argv[3])
        else:
            variation = 4
    except:
        print usage
        sys.exit(-1)
    main(inputFilename, outputFilename, variation)
