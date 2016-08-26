#! /usr/bin/env AFDKOPython
# encoding: UTF-8
from __future__ import division, absolute_import, print_function, unicode_literals
import hindkit as kit
import datetime

def override(self):
    self.style_scheme = kit.constants.STYLES_ITF_CamelCase
    self.vertical_metrics_strategy = "Google Fonts"
    self.tables["name"].update({
        0: kit.fallback(
            self.family.info.copyright,
            "Copyright (c) {} Indian Type Foundry (info@indiantypefoundry.com)".format(datetime.date.today().year),
        ),
        7: None,
        11: "http://www.indiantypefoundry.com/googlefonts",
        13: "This Font Software is licensed under the SIL Open Font License, Version 1.1. This license is available with a FAQ at: http://scripts.sil.org/OFL",
        14: "http://scripts.sil.org/OFL",
    })
    self.tables["OS/2"].update({
        "fsType": 0,
    })

kit.Client.override = override
kit.FeatureMatches.mI_VARIANT_NAME_PATTERN = r"mI\.a\d\d"
kit.filters.POTENTIAL_BASES_FOR_LONG_mII.append("K_TA")

family = kit.Family(
    client_name = "Google Fonts",
    trademark = "Poppins",
    script_name = "Devanagari",
)
family.set_masters()
family.set_styles()

i = family.info
i.copyright = "Copyright (c) 2014, 2016 Indian Type Foundry (info@indiantypefoundry.com)"
i.openTypeNameDesigner = "Ninad Kale (Devanagari), Jonny Pinhorn (Latin)"
i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = 1050, -350, 100
i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = 1100, 400

project = kit.Project(
    family,
    fontrevision = "2.100",
    options = {
        "prepare_mark_positioning": True,
        "match_mI_variants": "single",
        "position_marks_for_mI_variants": True,
        "additional_unicode_range_bits": [0, 1, 2],
        # "build_ttf": True,
    },
)
project.build()
