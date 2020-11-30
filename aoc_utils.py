"""
Various utilities for Advent of Code.
"""

import numpy as np
import re
from collections import Counter, defaultdict
from itertools import product, combinations

ALPHABET = list("abcdefghijklmnopqrstuvwxyz")
VOWELS = list("aeiou")
CONSONANTS = [i for i in ALPHABET if i not in VOWELS]

def coord2d(x,y):
    """Return a 2d numpy array, for coordinate use."""
    return np.array([x,y])

DIRECTIONS = {
    "N": coord2d(0,1),
    "W": coord2d(-1,0),
    "E": coord2d(1,0),
    "S": coord2d(0,-1)
}

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]