#!/usr/bin/python

import subprocess
import itfgfd

FAMILY_NAME = 'XDevanagari'

STYLE_NAMES = [
  'Light',
  'Regular',
  'Medium',
  'SemiBold',
  'Bold',
]

UFOIG_ARGS = [
  # '-kern',
  '-mark',
  # '-hint',
  '-flat',
  '-mkmk',
  '-clas',
  '-indi',
]

MAKEOTF_ARGS = [
  '-r',
  '-shw',
]

MATCH_mI_OFFSETS_DICT = {
  'Light':    0,
  'Regular':  0,
  'Medium':   0,
  'SemiBold': 0,
  'Bold':     0,
}

# Generate OpenType classes:
itfgfd.generate_classes(itfgfd.get_font('mm', suffix = '_0'))

# Reset style directories:
itfgfd.reset_style_dir(STYLE_NAMES)

# Interpolate instances:
subprocess.call(['UFOInstanceGenerator.py', 'mm', '-o', 'styles'] + UFOIG_ARGS)

# Match mI (matra i) variants to base glyphs:
itfgfd.match_mI(STYLE_NAMES, MATCH_mI_OFFSETS_DICT)

# Compile OTFs:
itfgfd.call_makeotf(FAMILY_NAME, STYLE_NAMES, MAKEOTF_ARGS)
