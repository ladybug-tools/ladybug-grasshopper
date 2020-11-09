# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to change the colors, numerical range, and/or number of divisions
of any Ladybug legend along with the corresponding colored mesh that the legend refers to.
-
Any Ladybug component that outputs a colored mesh and a legend will have an input
that can accept Legend Parameters from this component.
-

    Args:
        min_: A number to set the lower boundary of the legend. If None, the
            minimum of the values associated with the legend will be used.
        max_: A number to set the upper boundary of the legend. If None, the
            maximum of the values associated with the legend will be used.
        seg_count_: An interger representing the number of steps between
            the high and low boundary of the legend. The default is set to 11
            and any custom values input in here should always be greater than or
            equal to 2.
        colors_: An list of color objects. Default is Ladybug's original colorset.
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

ghenv.Component.Name = 'LB Legend Parameters'
ghenv.Component.NickName = 'LegendPar'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'


try:
    from ladybug.legend import LegendParameters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_plane
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if colors_ == []:
    colors_ = None
if base_plane_:
    base_plane_ = to_plane(base_plane_)

leg_par = LegendParameters(min=min_, max=max_, segment_count=seg_count_,
                           colors=colors_, base_plane=base_plane_)

leg_par.continuous_legend = continuous_leg_
leg_par.decimal_count = num_decimals_
leg_par.include_larger_smaller = larger_smaller_
leg_par.vertical = vert_or_horiz_
leg_par.segment_height = seg_height_
leg_par.segment_width = seg_width_
leg_par.text_height = text_height_
leg_par.font = font_
