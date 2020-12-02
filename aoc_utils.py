"""
Various utilities for Advent of Code.
"""

import numpy as np
import re
from collections import Counter, defaultdict
from itertools import product, combinations, permutations
from aocd import get_data

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
        
SPECIAL_CHARS = r"\[](){}*+?|^$."
        

class DataObj:
    """Turn a dictionary into something you can reference like obj.name"""
    def __init__(self, d):
        self.__dict__ = d
        
class InstructionParser:
    """String parsing minilanguage for AoC instructions.
    
    Theoretically faster and more intutive than writing your
    own regexes every time??
    
    The language consists of a newline-delimited set of strings like
    
    move: move to %x:i,%y:i and turn %direc:w
    plant: plant %num:n %color:p flowers
    
    The first word ([a-z_]+) before the colon (and space!) is the name of the instruction,
    and the % delimited sections are variable spots.
    
    A variable spot is denoted by %name:t where name is [a-z][a-z0-9_]* and t is a type character.
    
    A string will be matched against each rule in sequence, returning the first
    one it matches. If it doesn't match anything, an exception is thrown.
    
    When the parser is run on a string, it returns a (str, dict) tuple.
    The string is the name if the instruction matched,
    and the dict is a dictionary of variable names and their matched values.
    
    Type characters:
    w: lowercase word [a-z]+ (returns string)
    p: phrase of lowercase words [a-z ]+ (returns string)
    n: nonnegative integer [0-9]+ (returns int)
    i: integer -?[0-9]+ (returns int)
    
    For example, with the string example above,
    
    "move to -13,34 and turn north"
    would get parsed to
    ("move", {x:-13, y:34, direc:"north"})
    
    "plant 4 dark blue flowers"
    would get parsed to
    ("plant", {num:4, color:"dark blue"})
    
    Attributes:
    rules: list of (rule name, rule variables and types, compiled regex)
    
    
    Methods:
    match(str, as_dict=False): Parse a single string into a dictionary of
    {var_name:var_value}, with {rule:rule_name} as the rule that was matched.
    If as_dict is False, return a DataObj instead (for easier indexing)
    """
    
    def __init__(self, code):
        """
        code: the input source code.
        
        Will throw an error if not properly formatted.
        """
        lines = code.strip().split("\n")
        self.rules = []
        for l in lines:
            colon_sep=l.split(": ")
            if len(colon_sep)==1:
                raise ValueError(f"Incorrectly formatted rule {line}")
            name = colon_sep[0]
            if name == "rule":
                raise ValueError(f"Can't have a rule named 'rule'")
            template = ": ".join(colon_sep[1:])
            
            #escape any special characters before we tinker
            for c in SPECIAL_CHARS:
                template=template.replace(c, "\\"+c)
            tokens = re.split(r"(%[a-z][a-z0-9_]*:[wpni])", template) #split out the variable decs
            variables = []
            pattern = ["^"]
            
            for t in tokens:
                if not t:
                    continue
                elif t[0]!="%":
                    pattern.append(t)
                else:
                    rule, mode =  re.fullmatch(r"%([a-z][a-z0-9_]*):([wpni])", t).groups()
                    if mode == "p": #phrase, with possible spaces
                        pattern.append(r"([a-z]+(?: [a-z]+)*)")
                    elif mode == "w": #word, no spaces
                        pattern.append(r"([a-z]+)")
                    elif mode == "n":
                        pattern.append(r"([0-9]+)")
                    elif mode == "i":
                        pattern.append(r"(-?[0-9]+)")
                    else:
                        raise ValueError(f"the mode {mode} is not supported")
                    variables.append((rule, mode))
            pattern.append("$")
            self.rules.append((name, variables, re.compile("".join(pattern))))
            
    def match(self, string, as_dict = False):
        """Find which rule matches string, return its variables.
        
        Tries to match string against each of the rules in sequence.
        As soon as it matches one, it fills in the variable names,
        as well as the name of the rule that was matched,
        and outputs either a dict or a DataObj with that info."""
        for name, variables, pattern in self.rules:
            match = pattern.fullmatch(string)
            if not match:
                continue
            else:
                out = {"rule": name}
                for ((var_name, mode), var_value) in zip(variables, match.groups()):
                    if mode == "p" or mode == "w":
                        out[var_name] = var_value
                    elif mode == "n" or mode == "i":
                        out[var_name] = int(var_value)
                    else:
                        raise ValueError(f"the mode {mode} is not supported")
                if as_dict:
                    return out
                else:
                    return DataObj(out)
        raise ValueError(f"The line {string} isn't matched by any pattern")
            
    def match_list(self, l, as_dict = False):
        """Apply match() to an iterator of strings."""
        return [self.match(s, as_dict) for s in l]
    
    def match_block(self, b, as_dict = False):
        """Apply match() to a newline-delimited block."""
        return [self.match(s, as_dict) for s in b.split("\n") if s!=""]
                