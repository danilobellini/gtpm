#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Danilo de Jesus da Silva Bellini
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
Guitar Tab Problem Maker Test Module
"""

from ..guitar import Guitar, GuitarString

def test_guitar_length():
  assert len(Guitar("")) == 0
  assert len(Guitar("A3")) == 1
  assert len(Guitar("D3 F5")) == 2
  assert len(Guitar("A4 A4 A4")) == 3

def test_guitar_strings_are_guitar_string_intances():
  assert all(isinstance(gs, GuitarString) for gs in Guitar("F#1 G9 Bb2"))

def test_guitar_string_tune():
  gt = Guitar("A4 A4 A4 A3")
  assert gt[0].tune == gt[1].tune == gt[2].tune == "A4"
  assert gt[3].tune == "A3"
  assert Guitar("F8 D7")[0].tune == "F8"
