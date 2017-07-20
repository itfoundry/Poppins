#! /usr/bin/env AFDKOPython
# encoding: UTF-8
from __future__ import division, absolute_import, print_function, unicode_literals
import hindkit

def master_postprocess(self):
    self.import_from_font(
        source_path = "resources/ITF Misc-Regular.ufo",
        glyph_names_included = ".notdef zerowidthnonjoiner zerowidthjoiner dottedcircle".split(),
    )
    self.import_from_font(
        source_path = "masters/Poppins Devanagari-{}.ufo".format(self.name),
        import_anchors = True,
    )
    self.derive_glyphs("NULL CR nonbreakingspace zerowidthspace".split())

hindkit.Master.postprocess = master_postprocess
hindkit.FeatureMatches.mI_VARIANT_NAME_PATTERN = r"mI\.a\d\d"
hindkit.filters.POTENTIAL_BASES_FOR_LONG_mII.append("K_TA")

STYLES_ITF_CamelCase = [
    ("Light",     0, 300),
    ("Regular",  21, 400),
    ("Medium",   44, 500),
    ("SemiBold", 70, 600),
    ("Bold",    100, 700),
]

family = hindkit.Family(
    trademark = "Poppins",
    script_name = "Devanagari",
    append_script_name = False,
    client_name = "Google Fonts",
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
    fontrevision = "2.200",
    options = {
        "prepare_mark_positioning": True,
        "match_mI_variants": 1,
            "position_marks_for_mI_variants": True,
        "do_style_linking": True,
        "additional_unicode_range_bits": [0, 1, 2],
        "use_os_2_version_4": True,
            "prefer_typo_metrics": True,
        "build_ttf": True,
    },
)
project.build()
