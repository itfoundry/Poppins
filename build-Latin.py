#! /usr/bin/env AFDKOPython
# encoding: UTF-8
from __future__ import division, absolute_import, print_function, unicode_literals

import hindkit

RELEASE = 5
COMMIT = 1

DATA = {
    "roman": (
        [
            ("100", -50),
            ("500",  44),
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
            ("500i",  44),
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

def main():

    for master_scheme, style_scheme in DATA.values():

        family = hindkit.Family(
            trademark = "Poppins",
            script_name = "Latin",
            append_script_name = True,
            initial_release_year = 2014,
            source_tag = "Latin",
        )

        family.set_masters(master_scheme)
        for i in family.masters:
            i._filename = "Poppins-{}".format(i.name)

        family.set_styles(style_scheme)

        i = family.info
        i.openTypeNameDesigner = "Jonny Pinhorn"
        i.openTypeHheaAscender, i.openTypeHheaDescender, i.openTypeHheaLineGap = 1050, -350, 100
        i.openTypeOS2WinAscent, i.openTypeOS2WinDescent = 1135, 627

        project = hindkit.Project(
            family,
            release_commit = (RELEASE, COMMIT),
            options = {
                "do_style_linking": True,
                "additional_unicode_range_bits": [1, 2],
                "use_os_2_version_4": True,
                    "prefer_typo_metrics": True,
                "build_ttf": True,
            },
        )
        project.build()

# --- Overriding ---

hindkit.Project.directories["GOADB"] = "GlyphOrderAndAliasDB-Latin"

hindkit.constants.DERIVABLE_GLYPHS.update(
    {"quoteright.ss01": ["apostrophemod.ss01"]}
)

def master_postprocess(self):
    target_font = self.open()
    for glyph in target_font:
        glyph.clearAnchors()
    self.import_from_font(
        source_path = "resources/ITF Misc-Regular.ufo",
        glyph_names_included = [".notdef"],
    )
    self.derive_glyphs([
        "NULL", "CR", "nonbreakingspace",
        "softhyphen", "divisionslash", "bulletoperator", "macronmod", "apostrophemod",
        "apostrophemod.ss01",
    ])

hindkit.Master.postprocess = master_postprocess

# --- Executing ---

main()
