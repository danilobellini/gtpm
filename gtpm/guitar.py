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
# Created on Fri Sep 20 07:48:33 2013
# danilo [dot] bellini [at] gmail [dot] com
"""
Guitar description module
"""

class GuitarString(object):

  def __init__(self, tune):
    self.tune = tune

class Guitar(list):

  def __init__(self, tuning):
    gen = (GuitarString(tune) for tune in tuning.split())
    super(Guitar, self).__init__(gen)
