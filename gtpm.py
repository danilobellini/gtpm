#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2012-2013 Danilo de Jesus da Silva Bellini
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Created on Tue Sep 10 22:21:34 2013
# danilo [dot] bellini [at] gmail [dot] com
"""
Guitar Tab Problem Maker

Features:
- Reading exercises (shuffled per string)
- Fingering exercises (fingering follows a pattern)
- Playing with AudioLazy

"""

from __future__ import print_function

from audiolazy import (sHz, Streamix, adsr, z, gauss_noise, thub, chain, pi,
                       repeat, str2midi, midi2freq, karplus_strong, saw_table,
                       zeros, AudioIO, inf, atan, TableLookup, sin_table,
                       orange, xrange)
from random import shuffle
import pylab

# Input parameters
tuning = "E5 B4 G4 D4 A3 E3".split()
first_fret = 1
last_fret = 7
fingers = orange(4) # list of used fingers ("imao" fingering from 0 to 3)
width = 79 # monospaced characters
beat = 60 # bpm
notes_per_beat = 4
starting_beats = 4
shuffle_fingers = True
shuffle_per_string = False # Ignored when shuffle_fingers is False
invert_when_backwards = True

# Create notes as pairs (string_index, fret)
if shuffle_fingers and not shuffle_per_string:
  shuffle(fingers)
num_strings = len(tuning)
notes = []
inv_fingers = fingers[::-1]
for forefinger_fret in xrange(first_fret, last_fret + 1):
  inverter = slice(None, None, (-1) ** forefinger_fret) # Alternates asc/desc
  if invert_when_backwards:
    finger_order = inv_fingers[inverter]
  else:
    finger_order = fingers
  for idx in orange(num_strings)[inverter]:
    frets = [x + forefinger_fret for x in finger_order]
    if shuffle_fingers and shuffle_per_string:
      shuffle(frets)
    notes.extend((idx, fret) for fret in frets)

#
# Tablature display
#

# Create tablature columns
# A column is a list of strings for each row
tab_cols = [[el for el in tuning], ["|-"] * num_strings]
for string_idx, fret in notes:
  column = ["-"] * num_strings
  column[string_idx] = "{}".format(fret)
  tab_cols.append(column)
  tab_cols.append(["-"] * num_strings)
tab_cols[-1] = ["-||"] * num_strings

# Ensure the width is always the same in each row
for col in tab_cols:
  length = max(len(el) for el in col)
  for idx, el in enumerate(col):
    col[idx] = "{1:-<{0}}".format(length, el)

# Separates the tuning heading columns (which should be in every staff)
heading_cols, tab_cols = tab_cols[:2], tab_cols[2:]
heading_length = sum(len(col[0]) for col in heading_cols)
available_width = width - heading_length

# Breaks the columns in blocks (staves) by its length
tab = []
staff_row = []
total_length = 0
for col in tab_cols:
  length = len(col[0])
  if staff_row and total_length + length > available_width:
    if total_length != available_width:
      staff_row.append(["-" * (available_width - total_length)] * num_strings)
    tab.append(staff_row)
    staff_row = []
    total_length = 0
  staff_row.append(col)
  total_length += length
if staff_row:
  tab.append(staff_row)

# Prints the tablature
for staff in tab:
  print("\n".join("".join(el) for el in zip(*(heading_cols + staff))))
  print()

#
# Audio
#

# Useful values from AudioLazy
rate = 44100
s, Hz = sHz(rate)
ms = 1e-3 * s
kHz = 1e3 * Hz
beat_duration = 60. / beat * s # In samples
dur = beat_duration / notes_per_beat # Per note
smix = Streamix() # That's our sound mixture
env = adsr(dur, a=40*ms, d=35*ms, s=.6, r=70*ms).take(inf) # Envelope

# Effects used
def distortion(sig, multiplier=18):
  return atan(multiplier * sig) * (2 / pi)

# Intro count synth
filt = (1 - z ** -2) * .5
if starting_beats > 0:
  inoisy_stream = filt(gauss_noise()) * env
  inoisy_thub = thub(inoisy_stream.append(0).limit(beat_duration),
                     starting_beats)
  inoisy = chain.from_iterable(repeat(inoisy_thub).limit(starting_beats))
  smix.add(.1 * s, inoisy)
  smix.add(starting_beats * beat_duration - dur, []) # Event timing

# Wavetable lookup initialization
square_table = TableLookup([1] * 256 + [-1] * 256)
harmonics = dict(enumerate([1, 3, 2, 1, .3, .1, .7, .9, 1, 1, .5, .4, .2], 1))
table = sin_table.harmonize(harmonics).normalize()
mem_table = (3 * saw_table + (sin_table - saw_table) ** 3).normalize()

# Notes synth
midi_tuning = str2midi(tuning)
midi_pitches = [midi_tuning[string_idx] + fret for string_idx, fret in notes]
for freq in midi2freq(midi_pitches):
  ks_memory = .1 * gauss_noise() + .9 * mem_table(freq * Hz)
  ks_snd = distortion(karplus_strong(freq * Hz,
                                     tau=.2 * s,
                                     memory=ks_memory))
  tl_snd = .5 * table(freq * Hz) * env
  smix.add(dur, .5 * ks_snd + .5 * tl_snd)

# Shows synthesis wavetables
pylab.subplot(2, 1, 1)
pylab.plot(table.table)
pylab.title("Table lookup waveform")
pylab.axis(xmax=len(table) - 1)
pylab.subplot(2, 1, 2)
pylab.plot(mem_table.table)
pylab.title("Karplus-strong memory (besides noise)")
pylab.axis(xmax=len(mem_table) - 1)
pylab.tight_layout()
pylab.show()

# Voila!
smix.add(dur, zeros(.2 * s)) # Avoid ending click
with AudioIO(True) as player:
  player.play(smix, rate=rate)
