#!/usr/bin/python

import subprocess, re
import robofab.world

styles_dir = 'styles/'

stem_anchor_name = 'abvm_Ekaar'

template_features = '''\
#!opentype
include (../../family.fea);
'''

template_fontinfo = '''\
#!opentype

IsBoldStyle   false
IsItalicStyle false

PreferOS/2TypoMetrics      true
IsOS/2WidthWeigthSlopeOnly true
IsOS/2OBLIQUE              false
'''

template_fontinfo_Bold = '''\
#!opentype

IsBoldStyle   true
IsItalicStyle false

PreferOS/2TypoMetrics      true
IsOS/2WidthWeigthSlopeOnly true
IsOS/2OBLIQUE              false
'''


def reset_style_dir(style_name):

  style_dir = styles_dir + style_name

  subprocess.call(['mkdir', style_dir])

  file = open(style_dir + '/features' , 'w')
  file.write(template_features)
  file.close()

  file = open(style_dir + '/fontinfo' , 'w')
  if style_name == 'Bold':
    file.write(template_fontinfo_Bold)
  else:
    file.write(template_fontinfo)
  file.close()


def get_stem_position(font, glyph_name, stem_right_margin):

  glyph = font[glyph_name]

  has_stem_anchor = False
  for anchor in glyph.anchors:
    if anchor.name == stem_anchor_name:
      has_stem_anchor = True
      anchor_index = anchor.index
      break

  if has_stem_anchor:
    stem_position = glyph.anchors[anchor_index].x
  else:
    stem_position = glyph.width - stem_right_margin

  return stem_position


def generate_class_def_line_list(class_name, glyph_name_list):

  if glyph_name_list:
    class_def_line_list = ['@%s = [' % class_name] + \
                          ['  %s' % glyph_name for glyph_name in glyph_name_list] + \
                          ['];', '']
  else:
    class_def_line_list = ['@%s = [.notdef];' % class_name, '']

  return class_def_line_list


def match_mI(style_name, stem_position_offset):

  style_dir = styles_dir + style_name

  font = robofab.world.OpenFont(style_dir + '/font.ufo')

  mI_list   = sorted(font.groups['mI_ALTS'])
  base_list =    set(font.groups['mI_BASES'])

  mI_dict, mI_stretch_dict, mI_matching_dict = {}, {}, {}

  for index, glyph in enumerate(mI_list):
    mI_dict[index]          = glyph
    mI_stretch_dict[index]  = abs(font[glyph].rightMargin)
    mI_matching_dict[index] = []

  last_index = len(mI_list) - 1

  for anchor in font['dvmE'].anchors:
    if anchor.name == '_' + stem_anchor_name:
      stem_right_margin = abs(anchor.x)
      break
  else:
    print "Error: Can't find anchor `_%s`!" % stem_anchor_name

  tolerance_of_mI_stretch_shortage = (font['dvVA'].width - stem_right_margin) / 2

  invalid_base_list, long_base_list = [], []

  for base in base_list:

    if (not base.startswith('dv')) or (font[base].width <= 0):
      invalid_base_list.append(base)

    else:
      stem_position = get_stem_position(font, base, stem_right_margin) + stem_position_offset

      if stem_position < mI_stretch_dict[0]:
        mI_matching_dict[0].append(base)
      elif stem_position >= mI_stretch_dict[last_index]:
        if stem_position < mI_stretch_dict[last_index] + tolerance_of_mI_stretch_shortage:
          mI_matching_dict[last_index].append(base)
        else:
          long_base_list.append(base)
      else:
        for i in range(len(mI_list)):
          if stem_position < mI_stretch_dict[i]:
            if mI_stretch_dict[i] - stem_position < abs(mI_stretch_dict[i - 1] - stem_position):
              mI_matching_dict[i].append(base)
            else:
              mI_matching_dict[i - 1].append(base)
            break

  class_def_line_list = []
  substitute_rule_line_list = []

  class_def_line_list.extend(
    generate_class_def_line_list("mI_BASES_INVALID", invalid_base_list)
  )
  class_def_line_list.extend(
    generate_class_def_line_list("mI_BASES_TOO_LONG", long_base_list)
  )

  abvm_file = open(style_dir + '/abvm.fea', 'r')
  original_abvm_content = abvm_file.read()
  abvm_file.close()

  if re.search(
    r'(?m)^# lookup MARK_BASE_abvm_Reph_alt \{',
    original_abvm_content
  ):

    original_abvm_content = re.sub(
      r'(?m)\n\n\n^lookup MARK_BASE_abvm_Reph_alt \{\n(.+\n)+^\} MARK_BASE_abvm_Reph_alt;',
      r'',
      original_abvm_content
    )

    commented_abvm_lookup = re.search(
      r'(?m)^# lookup MARK_BASE_abvm_Reph_alt \{\n(.+\n)+^# \} MARK_BASE_abvm_Reph_alt;',
      original_abvm_content
    ).group()

    uncommented_abvm_lookup = '\n'.join([
      line[2:] for line in commented_abvm_lookup.splitlines()
    ])

    original_abvm_content = original_abvm_content.replace(
      commented_abvm_lookup,
      uncommented_abvm_lookup
    )

  original_abvm_lookup = re.search(
    r'(?m)^lookup MARK_BASE_abvm_Reph_alt {\n(.+\n)+^} MARK_BASE_abvm_Reph_alt;',
    original_abvm_content
  ).group()

  modified_abvm_lookup = original_abvm_lookup.replace(
    '\tpos base dvmI.a',
    '  pos base @mI_BASES_'
  )

  Reph_positioning_offset = font[mI_list[0]].width

  for index, glyph in enumerate(mI_list):

    tag = mI_dict[index][-2:]
    substitute_rule_prefix = '  '

    class_def_line_list.extend(
      generate_class_def_line_list(
        'mI_BASES_' + tag,
        mI_matching_dict[index]
      )
    )

    if len(mI_matching_dict[index]) == 0:
      substitute_rule_prefix = '# '
      modified_abvm_lookup = modified_abvm_lookup.replace(
        '  pos base @mI_BASES_' + tag,
        '# pos base @mI_BASES_' + tag
      )

    locator = '@mI_BASES_' + tag + ' <anchor'
    search_result = re.search(
      locator + ' ' + r'\-?\d+',
      modified_abvm_lookup
    )

    if search_result:

      x = search_result.group().split(' ')[-1]
      modified_x = str(int(x) - Reph_positioning_offset)

      modified_abvm_lookup = modified_abvm_lookup.replace(
        locator + ' ' + x,
        locator + ' ' + modified_x,
      )

    substitute_rule_line_list.append(
      "{}sub dvmI' @mI_BASES_{} by {};".format(
        substitute_rule_prefix,
        tag,
        mI_dict[index]
      )
    )

  commented_original_abvm_lookup = '\n'.join([
    '# ' + line
    for line in original_abvm_lookup.splitlines()
  ])

  modified_abvm_content = original_abvm_content.replace(
    original_abvm_lookup,
    commented_original_abvm_lookup + '\n\n\n' + modified_abvm_lookup
  )
  abvm_file = open(style_dir + '/abvm.fea', 'w')
  abvm_file.write(modified_abvm_content)
  abvm_file.close()

  result_file = open(style_dir + '/pres_mI.fea', 'w')
  result_file.write('#!opentype\n\n')
  result_line_list = ['# CLASSES', ''] + \
                     class_def_line_list + \
                     ['# RULES', ''] + \
                     substitute_rule_line_list
  result_file.write("\n".join(result_line_list) + '\n')
  result_file.close()
