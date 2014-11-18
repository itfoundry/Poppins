#!/usr/bin/python

import argparse, sys, subprocess, os.path

import itf
from config import (
    FAMILY_NAME, STYLE_NAMES, UFOIG_ARGS,
    MATCH_mI_OFFSETS_DICT, MAKEOTF_ARGS, OUTPUT_DIR
)


parser = argparse.ArgumentParser()

procedures = parser.add_argument_group(
    title='build procedure triggers',
    description='execute `python build.py -grimc` to run all the procedures.'
)

procedures.add_argument(
    '-g', '--generate', action='store_true',
    help='generate OpenType classes'
)
procedures.add_argument(
    '-r', '--reset', action='store_true',
    help='reset style/instance directories'
)
procedures.add_argument(
    '-i', '--interpolate', action='store_true',
    help='interpolate instances'
)
procedures.add_argument(
    '-m', '--match', action='store_true',
    help='match mI (i matra) variants to base glyphs'
)
procedures.add_argument(
    '-c', '--compile', action='store_true',
    help='compile OTFs'
)

if len(sys.argv) == 1:
    parser.print_help()
    sys.exit(2)

args = parser.parse_args()


if args.generate:
    itf.generate_classes(directory = 'masters', suffix = '_0')


if args.reset:

    print '\n#ITF: Resetting style/instance directories...'

    subprocess.call(['rm', '-fr', 'styles'])
    subprocess.call(['mkdir', 'styles'])

    for style_name in STYLE_NAMES:

        print '\tResetting %s...' % style_name

        style_dir = itf.STYLES_DIR + style_name
        IsBoldStyle_value = 'false'

        subprocess.call(['mkdir', style_dir])

        with open(style_dir + '/features', 'w') as f:
            f.write(itf.TEMPLATE_FEATURES)

        with open(style_dir + '/fontinfo', 'w') as f:
            if style_name == 'Bold':
                IsBoldStyle_value = 'true'
            f.write(itf.TEMPLATE_FONTINFO % IsBoldStyle_value)

    print '#ITF: Done.\n'


if args.interpolate:

    itf.fix_Glyphs_UFO_masters()

    subprocess.call(
        ['UFOInstanceGenerator.py', 'masters', '-o', 'styles'] + UFOIG_ARGS
    )


if args.match:

    print '\n#ITF: Matching mI...\n'

    for style_name in STYLE_NAMES:
        print '\t%s...' % style_name
        itf.match_mI(style_name, MATCH_mI_OFFSETS_DICT[style_name])
        print '\t%s done.\n' % style_name

    print '#ITF: Done.\n'


if args.compile:

    subprocess.call(['rm', '-fr', 'build'])
    subprocess.call(['mkdir', 'build'])

    for style_name in STYLE_NAMES:

        style_dir = 'styles/' + style_name
        otf_path = 'build/%s-%s.otf' % (FAMILY_NAME, style_name)

        subprocess.call([
            'makeotf',
            '-f', style_dir + '/font.ufo',
            '-o', otf_path,
            '-mf', 'FontMenuNameDB',
            '-gf', 'GlyphOrderAndAliasDB',
        ] + MAKEOTF_ARGS)

        subprocess.call(['rm', '-f', style_dir + '/current.fpr'])

        if os.path.exists(otf_path) and os.path.exists(OUTPUT_DIR):
            subprocess.call(['cp', '-f', otf_path, OUTPUT_DIR])
