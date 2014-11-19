#!/usr/bin/python

import os, re, collections

import robofab.world

from reference import POSSIBLE_mII_BASES, POSSIBLE_mI_BASES


STYLES_DIR = 'styles/'

STEM_ANCHOR_NAMES = ['abvm.e', 'abvm']

TEMPLATE_FEATURES = '''\
#!opentype
include (../../family.fea);
'''

TEMPLATE_FONTINFO = '''\
#!opentype

IsBoldStyle   %s
IsItalicStyle false

PreferOS/2TypoMetrics      true
IsOS/2WidthWeightSlopeOnly true
IsOS/2OBLIQUE              false
'''


GLYPH_ORDER = []

with open('GlyphOrderAndAliasDB', 'r') as f:
    goadb_content = f.read()

for line in goadb_content.splitlines():
    if line and (not line.startswith('#')):
        GLYPH_ORDER.append(line.split(' ')[1])


def get_font(directory, suffix = ''):

    font_file_name = ''

    for file_name in os.listdir(directory):
        if file_name.endswith(suffix + ".ufo"):
            font_file_name = file_name
            break
    if font_file_name:
        font = robofab.world.OpenFont(directory + '/' + font_file_name)
        return font
    else:
        print "#ITF: Can't find the font file with suffix `%s`." % suffix
        return None


def sort_glyphs(glyphs):

    sorted_glyphs = (
        [i for i in GLYPH_ORDER if i in glyphs] +
        [i for i in glyphs if i not in GLYPH_ORDER]
    )

    return sorted_glyphs


def generate_class_def_lines(class_name, glyph_names):

    if glyph_names:
        class_def_lines = (
            ['@%s = [' % class_name] +
            ['  %s' % glyph_name for glyph_name in glyph_names] +
            ['];', '']
        )
    else:
        class_def_lines = ['# @%s = [];' % class_name, '']

    return class_def_lines


def generate_classes(directory, suffix):

    print "\n#ITF: Generating OpenType classes..."

    generated_classes = {
        'COMBINING_MARKS': [],
        'mII_BASES':       [],
        'mI_ALTS':         [],
        'mI_BASES':        [],
    }

    font = get_font(directory, suffix)

    for glyph in font:

        glyph_name = glyph.name

        if re.search(r'^dvmI\.a\d\d$', glyph_name):
            generated_classes['mI_ALTS'].append(glyph_name)
            continue

        for anchor in glyph.anchors:
            if anchor.name.startswith('_'):
                generated_classes['COMBINING_MARKS'].append(glyph_name)
                break
        else:
            if glyph_name in POSSIBLE_mII_BASES:
                generated_classes['mII_BASES'].append(glyph_name)
            if glyph_name in POSSIBLE_mI_BASES:
                generated_classes['mI_BASES'].append(glyph_name)

    temp_groups = font.groups
    generated_classes = {
        k: sort_glyphs(v) for k, v in generated_classes.items()
    }

    temp_groups.update(generated_classes)

    font.groups = temp_groups
    font.save()

    toc_lines = ['# CONTENTS:']
    def_lines = []

    classes_to_be_written = {
        class_name: glyph_names
        for class_name, glyph_names in font.groups.items()
        if not class_name.startswith('@')
    }

    for class_name, glyph_names in sorted(classes_to_be_written.items()):
        toc_lines.append('# @%s' % class_name)
        def_lines.extend(
            generate_class_def_lines(class_name, glyph_names)
        )

    with open('family_classes.fea', 'w') as f:
        f.write('\n'.join(['#!opentype', ''] + toc_lines + [''] + def_lines))

    print "#ITF: Done."


def fix_Glyphs_UFO_masters(masters):

    for font in masters:

        if not font.info.postscriptFamilyBlues:
            font.info.postscriptFamilyBlues = []
        if not font.info.postscriptFamilyOtherBlues:
            font.info.postscriptFamilyOtherBlues = []
        if not font.info.postscriptStemSnapH:
            font.info.postscriptStemSnapH = []
        if not font.info.postscriptStemSnapV:
            font.info.postscriptStemSnapV = []

        font.save()


def get_stem_position(glyph, stem_right_margin):

    has_stem_anchor = False
    for anchor in glyph.anchors:
        if anchor.name in STEM_ANCHOR_NAMES:
            has_stem_anchor = True
            stem_anchor = anchor
            break

    if has_stem_anchor:
        stem_position = stem_anchor.x
    else:
        stem_position = glyph.width - stem_right_margin

    return stem_position


def restore_abvm_content(abvm_content):

    if re.search(
        r'# lookup MARK_BASE_abvm.i \{',
        abvm_content
    ):

        abvm_content = re.sub(
            r'(?m)\n\n\n^lookup MARK_BASE_abvm.i \{\n(^.+\n)+^\} MARK_BASE_abvm.i;',
            r'',
            abvm_content
        )

        commented_abvm_lookup = re.search(
            r'(?m)^# lookup MARK_BASE_abvm.i \{\n(^# .+\n)+^# \} MARK_BASE_abvm.i;',
            abvm_content
        ).group()

        uncommented_abvm_lookup = '\n'.join([
            line[2:] for line in commented_abvm_lookup.splitlines()
        ])

        original_abvm_content = abvm_content.replace(
            commented_abvm_lookup,
            uncommented_abvm_lookup
        )

    else:
        original_abvm_content = abvm_content

    return original_abvm_content


def write_mI_matches_to_files(style_dir, mI_table, long_base_names):

    with open(style_dir + '/abvm.fea', 'r') as f:
        abvm_content = f.read()

    original_abvm_content = restore_abvm_content(abvm_content)

    original_abvm_lookup = re.search(
        r'(?m)^lookup MARK_BASE_abvm.i {\n(.+\n)+^} MARK_BASE_abvm.i;',
        original_abvm_content
    ).group()

    modified_abvm_lookup = original_abvm_lookup.replace(
        'pos base dvmI.a',
        'pos base @mI_BASES_'
    )

    Reph_positioning_offset = mI_table[0].glyph.width

    class_def_lines = []
    class_def_lines.extend(
        generate_class_def_lines('mI_BASES_TOO_LONG', long_base_names)
    )

    substitute_rule_lines = []

    for mI in mI_table:

        mI_number = mI.glyph.name[-2:]
        to_comment_substitute_rule = False

        if not mI.matches:
            print '\t    `%s` is not used.' % mI.glyph.name
            to_comment_substitute_rule = True

            modified_abvm_lookup = modified_abvm_lookup.replace(
                '\tpos base @mI_BASES_' + mI_number,
                '#\tpos base @mI_BASES_' + mI_number
            )

        locator = '@mI_BASES_%s <anchor ' % mI_number

        search_result = re.search(
            locator + r'\-?\d+',
            modified_abvm_lookup
        )

        if search_result:
            x = search_result.group().split(' ')[-1]
            modified_x = str(int(x) - Reph_positioning_offset)
            modified_abvm_lookup = modified_abvm_lookup.replace(
                locator + x,
                locator + modified_x,
            )

        else:
            print "\t[!] `%s` doesn't have the anchor for Reph." % mI.glyph.name

        class_def_lines.extend(
            generate_class_def_lines(
                'mI_BASES_' + mI_number,
                mI.matches
            )
        )

        substitute_rule_lines.append(
            "{}sub dvmI' @mI_BASES_{} by {};".format(
                '# ' if to_comment_substitute_rule else '  ',
                mI_number,
                mI.glyph.name
            )
        )

    commented_original_abvm_lookup = '# ' + original_abvm_lookup.replace('\n', '\n# ')

    modified_abvm_content = original_abvm_content.replace(
        original_abvm_lookup,
        commented_original_abvm_lookup + '\n\n\n' + modified_abvm_lookup
    )

    with open(style_dir + '/abvm.fea', 'w') as f:
        f.write(modified_abvm_content)

    with open(style_dir + '/pres_mI.fea', 'w') as f:
        f.write('#!opentype\n\n')
        result_lines = (
            ['# CLASSES', ''] + class_def_lines +
            ['# RULES', ''] + substitute_rule_lines
        )
        f.write('\n'.join(result_lines) + '\n')


def match_mI(style_name, stem_position_offset):

    style_dir = STYLES_DIR + style_name

    font = robofab.world.OpenFont(style_dir + '/font.ufo')

    mI_list   = [font[glyph_name] for glyph_name in sorted(font.groups['mI_ALTS'])]
    base_list = [font[glyph_name] for glyph_name in font.groups['mI_BASES']]

    MatchRow = collections.namedtuple('MatchRow', 'glyph, stretch, matches')

    mI_table = [
        MatchRow(
            glyph   = mI,
            stretch = abs(mI.rightMargin),
            matches = []
        ) for mI in mI_list
    ]

    for anchor in font['dvmE'].anchors:
        if anchor.name in ['_' + name for name in STEM_ANCHOR_NAMES]:
            stem_right_margin = abs(anchor.x)
            break
    else:
        print "Error: Can't find the stem anchor in glyph `dvmE`!"

    tolerance_of_mI_stretch_shormI_numbere = (font['dvVA'].width - stem_right_margin) / 2
    long_base_names = []

    for base in base_list:

        base_name = base.name
        stem_position = get_stem_position(base, stem_right_margin) + stem_position_offset

        if stem_position < mI_table[0].stretch:
            mI_table[0].matches.append(base_name)

        elif stem_position >= mI_table[-1].stretch:
            if stem_position < mI_table[-1].stretch + tolerance_of_mI_stretch_shormI_numbere:
                mI_table[-1].matches.append(base_name)
            else:
                long_base_names.append(base_name)

        else:
            for index, mI in enumerate(mI_table):
                if stem_position < mI.stretch:
                    if mI.stretch - stem_position < abs(mI_table[index - 1].stretch - stem_position):
                        mI.matches.append(base_name)
                    else:
                        mI_table[index - 1].matches.append(base_name)
                    break

    write_mI_matches_to_files(style_dir, mI_table, long_base_names)
