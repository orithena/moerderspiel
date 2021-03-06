#!/usr/bin/python

import random, fileinput, re

class WordGenerator:
  """ 
  Generates a random word of arbitrary length that could be memorized far more
  easily than a completely random word. Give this class a text file to read in
  and it will derive it's matrix of transition probabilities from any string it
  could find in it (while ignoring any other characters in that file).
  
  It does have a default transition matrix built-in, based on /usr/share/dict/ngerman
  """
  consonants = list('bcdfghjklmnpqrstvwxyz')
  vowels = list('aeiou')
  # default matrix of transition probabilities, based on /usr/share/dict/ngerman
  # '`' is placeholder for "word start"
  poss = {'a': {'a': 37, 'c': 2628, 'b': 1777, 'e': 213, 'd': 1848, 
                'g': 1417, 'f': 431, 'i': 1583, 'h': 246, 'k': 618, 
                'j': 50, 'm': 1878, 'l': 5167, 'o': 57, 'n': 6674, 
                'q': 52, 'p': 1531, 's': 2938, 'r': 5510, 'u': 941, 
                't': 7162, 'w': 488, 'v': 762, 'y': 797, 'x': 169, 'z': 261}, 
          '`': {'a': 4339, 'c': 7039, 'b': 4426, 'e': 2932, 'd': 4498, 
                'g': 2502, 'f': 3101, 'i': 2857, 'h': 2752, 'k': 791, 
                'j': 867, 'm': 4232, 'l': 2434, 'o': 1760, 'n': 1465, 
                'q': 355, 'p': 5695, 's': 8542, 'r': 4182, 'u': 1700, 
                't': 3736, 'w': 2043, 'v': 1154, 'y': 272, 'x': 33, 'z': 188}, 
          'c': {'a': 3406, 'c': 404, 'b': 3, 'e': 2494, 'd': 10, 'g': 5, 
                'f': 3, 'i': 1672, 'h': 3033, 'k': 1899, 'j': 0, 'm': 9, 
                'l': 982, 'o': 4105, 'n': 10, 'q': 48, 'p': 1, 's': 343, 
                'r': 1429, 'u': 1136, 't': 1705, 'w': 0, 'v': 1, 'y': 280, 
                'x': 0, 'z': 11}, 
          'b': {'a': 1665, 'c': 24, 'b': 457, 'e': 1767, 'd': 42, 'g': 4, 
                'f': 12, 'i': 1232, 'h': 19, 'k': 3, 'j': 49, 'm': 30, 
                'l': 1999, 'o': 1366, 'n': 29, 'q': 0, 'p': 8, 's': 404, 
                'r': 1089, 'u': 990, 't': 80, 'w': 13, 'v': 17, 'y': 143, 
                'x': 0, 'z': 0}, 
          'e': {'a': 2950, 'c': 2133, 'b': 479, 'e': 1607, 'd': 8431, 
                'g': 749, 'f': 841, 'i': 642, 'h': 249, 'k': 153, 'j': 72, 
                'm': 1696, 'l': 3374, 'o': 462, 'n': 6448, 'q': 190, 'p': 1147, 
                's': 11881, 'r': 12022, 'u': 301, 't': 2646, 'w': 550, 
                'v': 843, 'y': 518, 'x': 965, 'z': 122}, 
          'd': {'a': 1112, 'c': 59, 'b': 104, 'e': 4555, 'd': 457, 'g': 300, 
                'f': 58, 'i': 3369, 'h': 77, 'k': 8, 'j': 62, 'm': 119, 
                'l': 573, 'o': 1155, 'n': 104, 'q': 4, 'p': 46, 's': 1014, 
                'r': 715, 'u': 647, 't': 42, 'w': 122, 'v': 91, 'y': 232, 
                'x': 0, 'z': 12}, 
          'g': {'a': 1283, 'c': 3, 'b': 27, 'e': 2182, 'd': 16, 'g': 562, 
                'f': 21, 'i': 1246, 'h': 817, 'k': 7, 'j': 4, 'm': 108, 
                'l': 825, 'o': 750, 'n': 412, 'q': 1, 'p': 16, 's': 625, 
                'r': 1285, 'u': 716, 't': 54, 'w': 31, 'v': 0, 'y': 191, 
                'x': 0, 'z': 8}, 
          'f': {'a': 755, 'c': 2, 'b': 13, 'e': 986, 'd': 2, 'g': 6, 
                'f': 745, 'i': 1480, 'h': 9, 'k': 3, 'j': 2, 'm': 4, 'l': 829, 
                'o': 1001, 'n': 9, 'q': 0, 'p': 3, 's': 133, 'r': 667, 'u': 812, 
                't': 322, 'w': 1, 'v': 0, 'y': 183, 'x': 0, 'z': 0}, 
          'i': {'a': 2216, 'c': 3787, 'b': 733, 'e': 4027, 'd': 1511, 'g': 1468, 
                'f': 939, 'i': 14, 'h': 33, 'k': 206, 'j': 29, 'm': 1633, 'l': 2712, 
                'o': 3561, 'n': 14463, 'q': 103, 'p': 923, 's': 4850, 'r': 1441, 
                'u': 189, 't': 3609, 'w': 25, 'v': 1359, 'y': 10, 'x': 120, 'z': 1322}, 
          'h': {'a': 2297, 'c': 20, 'b': 76, 'e': 3325, 'd': 26, 'g': 7, 'f': 46, 
                'i': 2190, 'h': 24, 'k': 10, 'j': 5, 'm': 150, 'l': 174, 'o': 2149, 
                'n': 122, 'q': 4, 'p': 17, 's': 279, 'r': 456, 'u': 631, 't': 551, 
                'w': 92, 'v': 2, 'y': 397, 'x': 0, 'z': 3}, 
          'k': {'a': 348, 'c': 10, 'b': 60, 'e': 1705, 'd': 21, 'g': 8, 'f': 33, 
                'i': 1163, 'h': 94, 'k': 32, 'j': 7, 'm': 45, 'l': 277, 'o': 156, 
                'n': 204, 'q': 0, 'p': 35, 's': 667, 'r': 84, 'u': 87, 't': 27, 
                'w': 53, 'v': 0, 'y': 166, 'x': 0, 'z': 0}, 
          'j': {'a': 346, 'c': 0, 'b': 0, 'e': 245, 'd': 0, 'g': 0, 'f': 1, 
                'i': 103, 'h': 0, 'k': 1, 'j': 0, 'm': 0, 'l': 0, 'o': 312, 
                'n': 0, 'q': 0, 'p': 0, 's': 2, 'r': 2, 'u': 341, 't': 0, 
                'w': 0, 'v': 0, 'y': 0, 'x': 0, 'z': 0}, 
          'm': {'a': 3100, 'c': 70, 'b': 863, 'e': 3003, 'd': 7, 'g': 2, 'f': 50, 
                'i': 2581, 'h': 14, 'k': 1, 'j': 0, 'm': 718, 'l': 69, 'o': 1779, 
                'n': 131, 'q': 3, 'p': 1518, 's': 601, 'r': 30, 'u': 715, 't': 9, 
                'w': 13, 'v': 8, 'y': 150, 'x': 0, 'z': 0}, 
          'l': {'a': 3806, 'c': 166, 'b': 145, 'e': 6155, 'd': 566, 'g': 130, 
                'f': 167, 'i': 5339, 'h': 41, 'k': 208, 'j': 5, 'm': 210, 'l': 3365, 
                'o': 2642, 'n': 95, 'q': 6, 'p': 171, 's': 1164, 'r': 44, 'u': 1129, 
                't': 654, 'w': 33, 'v': 200, 'y': 2769, 'x': 0, 'z': 6}, 
          'o': {'a': 709, 'c': 1188, 'b': 692, 'e': 351, 'd': 979, 'g': 1026, 
                'f': 387, 'i': 669, 'h': 134, 'k': 432, 'j': 30, 'm': 1989, 
                'l': 2397, 'o': 1621, 'n': 7238, 'q': 42, 'p': 1346, 's': 1798, 
                'r': 4678, 'u': 2863, 't': 1648, 'w': 1183, 'v': 949, 'y': 265, 
                'x': 213, 'z': 102}, 
          'n': {'a': 2572, 'c': 2250, 'b': 161, 'e': 4460, 'd': 2980, 'g': 9164, 
                'f': 511, 'i': 2967, 'h': 183, 'k': 622, 'j': 90, 'm': 114, 'l': 212, 
                'o': 1517, 'n': 843, 'q': 98, 'p': 127, 's': 3693, 'r': 146, 
                'u': 532, 't': 4815, 'w': 97, 'v': 324, 'y': 226, 'x': 25, 'z': 64}, 
          'q': {'a': 4, 'c': 0, 'b': 1, 'e': 0, 'd': 0, 'g': 0, 'f': 0, 'i': 7, 'h': 0, 
                'k': 0, 'j': 0, 'm': 0, 'l': 0, 'o': 1, 'n': 0, 'q': 0, 'p': 0, 's': 0, 
                'r': 0, 'u': 1132, 't': 0, 'w': 0, 'v': 0, 'y': 0, 'x': 0, 'z': 0}, 
          'p': {'a': 1971, 'c': 19, 'b': 38, 'e': 2935, 'd': 21, 'g': 10, 'f': 21, 
                'i': 1657, 'h': 997, 'k': 17, 'j': 4, 'm': 34, 'l': 1309, 'o': 1858, 
                'n': 26, 'q': 0, 'p': 969, 's': 685, 'r': 2229, 'u': 769, 't': 584, 
                'w': 22, 'v': 0, 'y': 148, 'x': 0, 'z': 1}, 
          's': {'a': 1537, 'c': 1608, 'b': 106, 'e': 3702, 'd': 60, 'g': 56, 'f': 105, 
                'i': 2901, 'h': 2413, 'k': 440, 'j': 14, 'm': 792, 'l': 902, 'o': 1343, 
                'n': 444, 'q': 204, 'p': 1480, 's': 3066, 'r': 58, 'u': 1436, 
                't': 7113, 'w': 369, 'v': 21, 'y': 372, 'x': 0, 'z': 5}, 
          'r': {'a': 5552, 'c': 778, 'b': 499, 'e': 7686, 'd': 1148, 'g': 590, 'f': 234, 
                'i': 5675, 'h': 162, 'k': 478, 'j': 37, 'm': 934, 'l': 540, 'o': 3916, 
                'n': 868, 'q': 32, 'p': 427, 's': 3408, 'r': 1101, 'u': 1303, 't': 1789, 
                'w': 137, 'v': 316, 'y': 884, 'x': 8, 'z': 17}, 
          'u': {'a': 803, 'c': 828, 'b': 689, 'e': 800, 'd': 642, 'g': 559, 'f': 259, 
                'i': 807, 'h': 21, 'k': 84, 'j': 18, 'm': 1267, 'l': 1962, 'o': 167, 
                'n': 3043, 'q': 5, 'p': 735, 's': 2718, 'r': 2452, 'u': 11, 't': 1663, 
                'w': 8, 'v': 58, 'y': 27, 'x': 63, 'z': 88}, 
          't': {'a': 3271, 'c': 451, 'b': 112, 'e': 7832, 'd': 28, 'g': 38, 'f': 134, 
                'i': 8190, 'h': 2265, 'k': 9, 'j': 6, 'm': 157, 'l': 750, 'o': 2567, 
                'n': 123, 'q': 0, 'p': 61, 's': 2551, 'r': 2886, 'u': 1329, 't': 1438, 
                'w': 220, 'v': 8, 'y': 930, 'x': 0, 'z': 113}, 
          'w': {'a': 1205, 'c': 9, 'b': 61, 'e': 931, 'd': 83, 'g': 11, 'f': 24, 
                'i': 919, 'h': 376, 'k': 40, 'j': 0, 'm': 24, 'l': 148, 'o': 617, 
                'n': 289, 'q': 0, 'p': 27, 's': 275, 'r': 219, 'u': 15, 't': 25, 
                'w': 6, 'v': 0, 'y': 28, 'x': 0, 'z': 6}, 
          'v': {'a': 966, 'c': 0, 'b': 0, 'e': 3130, 'd': 2, 'g': 1, 'f': 0, 'i': 1364, 
                'h': 0, 'k': 0, 'j': 0, 'm': 0, 'l': 10, 'o': 468, 'n': 1, 'q': 0, 
                'p': 0, 's': 15, 'r': 11, 'u': 72, 't': 1, 'w': 0, 'v': 17, 'y': 33, 
                'x': 0, 'z': 0}, 
          'y': {'a': 287, 'c': 182, 'b': 86, 'e': 355, 'd': 101, 'g': 59, 'f': 34, 
                'i': 378, 'h': 35, 'k': 11, 'j': 6, 'm': 227, 'l': 195, 'o': 160, 
                'n': 205, 'q': 1, 'p': 255, 's': 507, 'r': 151, 'u': 55, 't': 101, 
                'w': 69, 'v': 5, 'y': 3, 'x': 19, 'z': 23}, 
          'x': {'a': 98, 'c': 128, 'b': 2, 'e': 249, 'd': 0, 'g': 2, 'f': 4, 'i': 268, 
                'h': 49, 'k': 0, 'j': 0, 'm': 2, 'l': 5, 'o': 55, 'n': 2, 'q': 2, 
                'p': 247, 's': 4, 'r': 0, 'u': 50, 't': 216, 'w': 6, 'v': 1, 'y': 32, 
                'x': 1, 'z': 1}, 
          'z': {'a': 299, 'c': 2, 'b': 4, 'e': 1099, 'd': 1, 'g': 1, 'f': 0, 'i': 487, 
                'h': 20, 'k': 2, 'j': 0, 'm': 8, 'l': 73, 'o': 127, 'n': 7, 'q': 1, 
                'p': 3, 's': 4, 'r': 3, 'u': 25, 't': 5, 'w': 6, 'v': 6, 'y': 41, 
                'x': 0, 'z': 179},
          }
  
  def __init__(self):
    random.seed()
    #DEBUG: print self.poss
  
  def readwordlist(self, filename):
    """
    Init transition probability matrix with 0 for each two-letter combination
    and call appendwordlist.
    
    Use it for the first file you want to read in.
    """
    # I like nested list comprehensions
    self.poss = dict([
                      (
                        c, 
                        dict([
                          (r,0) 
                          for r in [ 
                            chr(j) for j in range(97, ord('z')+1) 
                          ] 
                        ]) 
                      ) 
                      for c in 
                      [ 
                        chr(i) for i in range(96, ord('z')+1) 
                      ] 
                    ])
    self.appendwordlist(filename)
  
  def appendwordlist(self, filename):
    """
    Reads a file and counts the letter transitions in any word that is surrounded
    by spaces. This increments the numbers in the transition matrix.
    
    Use it for all files you want to read in except for the first. Actually, you
    could use it for the first file; then you would add to the default matrix instead
    of using a fresh one.
    """
    for line in fileinput.input(filename):
      for word in line.lower().strip().split(' '):
        if( re.match('^[a-z]+$', word) != None ):
          # oc = old char, c = current char, chr(96) is placeholder char for "word start"
          oc = chr(96)
          for c in list(word):
            poss = self.poss[oc] 
            poss[c] += 1
            oc = c
    fileinput.close()
  
  def generate_word(self, length):
    """
    Generates a word of arbitrary length based on the current transition matrix.
    """
    s = ''
    oc = chr(96)
    for a in range(0, length):
      summe = sum(self.poss[oc].values())
      r = random.randint(0, summe-1)
      x = 0
      for c,p in self.poss[oc].items():
        x += p
        if r < x:
          oc = c
          s += c
          break
    return s

  def generate_word_from_pattern(self, pattern):
    """
    Generates a word based on a vowel/consonant pattern. Length of the result
    is derived from the pattern, as is the places of vowels and consonants.
    
    Ex.: with pattern='aaabbababbbaa', this may produce 'ouerbinirtrea';
    pattern='singularity' may produce 'winsireners'
    """
    s = ''
    oc = chr(96)
    for pc in list(pattern):
      d = dict([ 
                (x, self.poss[oc][x]) 
                for x in list(
                  set(self.poss[oc].keys()) 
                  & set(self.consonants if pc in self.consonants else self.vowels)
                ) 
              ])
      summe = sum(d.values())
      #DEBUG: print oc, d, summe
      r = random.randint(0, summe-1)
      x = 0
      for c,p in d.items():
        x += p
        if r < x:
          oc = c
          s += c
          break
    return s

  def generate_pattern(self, length):
    """
    Generates a vowel/consonant pattern that does not allow too many consonants 
    or vowels in a row.
    """
    p = ''
    count = random.randint(2,4)
    same = True
    for a in range(0,length):
      r = random.randint(0,3)
      #DEBUG: print r, same, 
      if r == count:
        count += 1
      else:
        same = not same
        count = 0 if same else 1
      p += 't' if same else 'a'
      #DEBUG: print ' -> ', r, same, ' => ', p
    return p

  def generate(self, length):
    """
    Generates a word of a certain length. Uses generate_pattern() to avoid
    too many consonants or vowels in a row.
    
    This is the standard method to use. Minimal usage of this class:
      print WordGenerator().generate(8)
    """
    return self.generate_word_from_pattern(self.generate_pattern(length))

if __name__ == "__main__":
  import sys
  try:
    print WordGenerator().generate(int(sys.argv[1]))
  except:
    try:
      print WordGenerator().generate_word_from_pattern(sys.argv[1])
    except:
      print 'I Expect either a Word or a Length from The Command Line.'

  