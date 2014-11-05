#!/usr/bin/python

from os.path import exists
from argparse import ArgumentParser
from subprocess import call

from config import (FAMILY_NAME, STYLE_NAMES, UFOIG_ARGS,
                    MATCH_mI_OFFSETS_DICT, MAKEOTF_ARGS, OUTPUT_DIR)
import itf


parser = ArgumentParser()
parser.add_argument(
    '-g', '--generateclasses', action='store_true',
    help='Generate OpenType classes'
)
parser.add_argument(
    '-r', '--resetdirectories', action='store_true',
    help='Reset style/instance directories'
)
parser.add_argument(
    '-i', '--interpolate', action='store_true',
    help='Interpolate instances'
)
parser.add_argument(
    '-m', '--matchmi', action='store_true',
    help='Match mI (i matra) variants to base glyphs'
)
parser.add_argument(
    '-c', '--compile', action='store_true',
    help='Compile OTFs'
)
args = parser.parse_args()


if args.generateclasses:
    itf.generate_classes(directory = 'masters', suffix = '_0')


if args.resetdirectories:

    print '\n#ITF: Resetting style/instance directories...'

    call(['rm', '-fr', 'styles'])
    call(['mkdir', 'styles'])

    IsBoldStyle_value = 'false'

    for style_name in STYLE_NAMES:

        print '\tResetting %s...' % style_name

        style_dir = itf.STYLES_DIR + style_name

        call(['mkdir', style_dir])

        with open(style_dir + '/features', 'w') as f:
            f.write(itf.TEMPLATE_FEATURES)

        with open(style_dir + '/fontinfo', 'w') as f:
            if style_name == 'Bold':
                IsBoldStyle_value = 'true'
            f.write(itf.TEMPLATE_FONTINFO % IsBoldStyle_value)

    print '#ITF: Done.\n'


if args.interpolate:

    call(
        ['UFOInstanceGenerator.py', 'masters', '-o', 'styles'] + UFOIG_ARGS
    )


if args.matchmi:

    print '\n#ITF: Matching mI...\n'

    for style_name in STYLE_NAMES:
        print '\t%s...' % style_name
        itf.match_mI(style_name, MATCH_mI_OFFSETS_DICT[style_name])
        print '\t%s done.\n' % style_name

    print '#ITF: Done.\n'


if args.compile:

    call(['rm', '-fr', 'build'])
    call(['mkdir', 'build'])

    for style_name in STYLE_NAMES:

        style_dir = 'styles/' + style_name
        otf_path = 'build/%s-%s.otf' % (FAMILY_NAME, style_name)

        call([
            'makeotf',
            '-f', style_dir + '/font.ufo',
            '-o', otf_path,
            '-mf', 'FontMenuNameDB',
            '-gf', 'GlyphOrderAndAliasDB',
        ] + MAKEOTF_ARGS)

        call(['rm', '-f', style_dir + '/current.fpr'])

        if exists(otf_path) and exists(OUTPUT_DIR):
            call(['cp', '-f', otf_path, OUTPUT_DIR])
