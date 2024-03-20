# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Use this component to change the colors, range, and display of any Ladybug legend
along with the corresponding colored mesh that the legend refers to.
-
The legend parameters from this component have more limitations than the normal
Legend Parameters. However, these legend parameters will do auto-categorization
of data, binning values into groups based on custom ranges.
-

    Args:
        _domain: A list of one or more numbers noting the bondaries of the data
            categories. For example, [100, 2000] creates three categories of
            (<100, 100-2000, >2000). Values must always be ordered from lowest
            to highest.
        _colors: An list of color objects with a length equal to the number of items
            in the domain + 1. These are used to color each of the categories of data.
        categories_: An optional list of text strings with a length equal to the
            colors. These will be used to name each of the categories in the legend.
            If None, the legend text will simply mark the numerical ranges of the
            categories. (Default: None).
        continuous_cols_: Boolean noting whether colors generated are continuous
            or discrete. If True, the colors generated from the corresponding
            legend will be in a continuous gradient. If False, they will be
            categorized in incremental groups according to the segment_count.
            (Default: False).
        continuous_leg_: Boolean. If True, the colors along the legend will be in
            a continuous gradient. If False, they will be categorized in
            incremental groups according to the number_of_segments.
            Default is False for depicting discrete categories.
        num_decimals_: An optional integer to set the number of decimal
            places for the numbers in the legend text. Default is 2.
        larger_smaller_: Boolean noting whether to include larger than and
            smaller than (> and <) values after the upper and lower legend segment
            text. Default is False.
        vert_or_horiz_: Boolean. If True, the legend mesh and text points
            will be generated vertically.  If False, they will genrate a
            horizontal legend. Default is True for a vertically-oriented legend.
        base_plane_: A Plane to note the starting point and orientation from
            where the legend will be genrated. The default is the world XY plane
            at origin (0, 0, 0).
        seg_height_: An optional number to set the height of each of the legend
            segments. Default is 1.
        seg_width_: An optional number to set the width of each of the legend
            segments. Default is 1 when legend is vertical. When horizontal, the
            default is (text_height * (number_decimal_places + 2)).
        text_height_: An optional number to set the size of the text in model units.
            Default is half of the segment_height.
        font_: An optional text string to specify the font to be used for the text.
            Examples include "Arial", "Times New Roman", "Courier" (all without
            quotations). Default is "Arial".
    
    Returns:
        leg_par: A legend parameter object that can be plugged into any of the
            Ladybug components with a legend.
"""

ghenv.Component.Name = 'LB Legend Parameters Categorized'
ghenv.Component.NickName = 'LegendParCategorized'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


try:
    from ladybug.legend import LegendParametersCategorized
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_plane
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    if base_plane_:
        base_plane_ = to_plane(base_plane_)
    if len(categories_) == 0:
        categories_ = None

    leg_par = LegendParametersCategorized(
        domain=_domain, colors=_colors, category_names=categories_,
        base_plane=base_plane_)

    leg_par.continuous_colors = continuous_cols_
    leg_par.continuous_legend = continuous_leg_
    leg_par.decimal_count = num_decimals_
    leg_par.include_larger_smaller = larger_smaller_
    leg_par.vertical = vert_or_horiz_
    leg_par.segment_height = seg_height_
    leg_par.segment_width = seg_width_
    leg_par.text_height = text_height_
    leg_par.font = font_
