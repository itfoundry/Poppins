#!/usr/bin/python

from subprocess import call
import os.path
import itf_gfd


is_multiple_master = True

family_name = 'XDevanagari'

style_name_list = [
  'Light',
  'Regular',
  'Medium',
  'SemiBold',
  'Bold',
]


def main():

  call(['rm', '-fr', 'build'])
  call(['mkdir', 'build'])

  for style_name in style_name_list:

    otf_path = 'build/%s-%s.otf' % (family_name, style_name)
    style_dir = 'styles/' + style_name

    call(['makeotf'] + makeotf_arg_list)

    call(['rm', '-f', style_dir + '/current.fpr'])

    if os.path.exists(otf_path):
      call(['cp', '-f', otf_path, '/Library/Application Support/Adobe/Fonts'])


makeotf_arg_list = [
  '-f', style_dir + '/font.ufo',
  '-o', otf_path,
  '-mf', 'FontMenuNameDB',
  '-gf', 'GlyphOrderAndAliasDB',
  '-r',
  '-shw',
]


if __name__ == '__main__':
  main()
