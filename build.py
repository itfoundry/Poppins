#! /usr/bin/env AFDKOPython
# encoding: UTF-8
from __future__ import division, absolute_import, print_function, unicode_literals
import hindkit

DIGITS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
DIGITS_DEVANAGARI = ["dv" + i.title() for i in DIGITS]

def master_postprocess(self):
    self.import_from_font(
        source_path = "resources/ITF Misc-Regular.ufo",
        glyph_names_included = ".notdef zerowidthnonjoiner zerowidthjoiner dottedcircle".split(),
    )
    self.import_from_font(
        source_path = "masters/Poppins Devanagari-{}.ufo".format(self.name),
        import_anchors = True,
    )
    self.derive_glyphs([
        "NULL", "CR", "nonbreakingspace",
        "softhyphen", "divisionslash", "bulletoperator", "macronmod", "apostrophemod",
    ] + DIGITS_DEVANAGARI)

hindkit.constants.DERIVABLE_GLYPHS.update({k: [v] for k, v in zip(DIGITS, DIGITS_DEVANAGARI)})
hindkit.filters.POTENTIAL_BASES_FOR_LONG_mII.append("K_TA")
hindkit.Master.postprocess = master_postprocess
hindkit.FeatureMatches.mI_VARIANT_NAME_PATTERN = r"mI\.a\d\d"

DATA = {
    "roman": (
        [
            ("100", -50),
            ("900", 150),
        ],
        [
            ("Thin",       -50, 250),
            ("ExtraLight", -25, 275),
            ("Light",        0, 300),
            ("Regular",     21, 400),
            ("Medium",      44, 500),
            ("SemiBold",    70, 600),
            ("Bold",       100, 700),
            ("ExtraBold",  125, 800),
            ("Black",      150, 900),
        ],
    ),
    "italic": (
        [
            ("100i", -50),
            ("900i", 150),
        ],
        [
            ("Thin Italic",       -50, 250),
            ("ExtraLight Italic", -25, 275),
            ("Light Italic",        0, 300),
            ("Italic",             21, 400),
            ("Medium Italic",      44, 500),
            ("SemiBold Italic",    70, 600),
            ("Bold Italic",       100, 700),
            ("ExtraBold Italic",  125, 800),
            ("Black Italic",      150, 900),
        ],
    ),
}

for master_scheme, style_scheme in DATA.values():

    family = hindkit.Family(
        trademark = "Poppins",
        script_name = "Devanagari",
        append_script_name = False,
        client_name = "Google Fonts",
        initial_release_year = 2014,
        is_serif = False,
    )
    family.set_masters(master_scheme)
    family.set_styles(style_scheme)

    i = family.info
    i.openTypeNameDesigner = "Ninad Kale (Devanagari), Jonny Pinhorn (Latin)"
    i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = 1050, -350, 100
    i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = 1135, 627

    project = hindkit.Project(
        family,
        fontrevision = "3.010",
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
