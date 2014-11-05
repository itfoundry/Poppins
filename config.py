#!/usr/bin/python

FAMILY_NAME = 'Poppins'

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

MATCH_mI_OFFSETS_DICT = {
    'Light':    0,
    'Regular':  0,
    'Medium':   0,
    'SemiBold': 0,
    'Bold':     0,
}

MAKEOTF_ARGS = [
    '-r',
    '-shw',
]

OUTPUT_DIR = '/Library/Application Support/Adobe/Fonts'
