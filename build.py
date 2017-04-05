#! /usr/bin/env AFDKOPython
# encoding: UTF-8
from __future__ import division, absolute_import, print_function, unicode_literals
import hindkit

STYLES_ITF_CamelCase = [
    ("Light",     0, 300),
    ("Regular",  21, 400),
    ("Medium",   44, 500),
    ("SemiBold", 70, 600),
    ("Bold",    100, 700),
]

family = hindkit.Family(
    trademark = "Poppins",
    script_name = "Latin",
    client_name = "Google Fonts",
    variant_tag = "Latin-only", #!
    initial_release_year = 2014,
    is_serif = False,
)
family.set_masters()
family.set_styles(STYLES_ITF_CamelCase)

i = family.info
i.openTypeNameDesigner = "Ninad Kale (Devanagari), Jonny Pinhorn (Latin)"
i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = 1050, -350, 100
i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = 1100, 400

project = hindkit.Project(
    family,
    fontrevision = "2.110",
    options = {
        "do_style_linking": True,
        # "omit_mac_name_records": False, # False for Office 2011 for Mac
        "additional_unicode_range_bits": [1, 2],
        "build_ttf": True,
    },
)
project.build()
