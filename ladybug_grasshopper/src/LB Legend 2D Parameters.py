# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Customize the properties of a screen-oreinted 2D legend displaying with the
"LB Preview VisualizationSet" component.
-

    Args:
        origin_x_: An integer in pixels to note the X coordinate of the base point from
            where the 2D legend will be generated (assuming an origin in the
            upper-left corner of the screen with higher positive values of
            X moving to the right). Alternatively, this can be a text string
            ending in a % sign to denote the percentage of the screen where
            the X coordinate exists (eg. 5%). The default is set to make the
            legend clearly visible in the upper-left corner of the
            screen (10 pixels).
        origin_y_: An integer in pixels to note the Y coordinate of the base point from
            where the legend will be generated (assuming an origin in the
            upper-left corner of the screen with higher positive values of
            Y moving downward). Alternatively, this can be a text string
            ending in a % sign to denote the percentage of the screen where
            the X coordinate exists (eg. 5%). The default is set to make the
            legend clearly visible in the upper-left corner of the
            screen (50 pixels).
        seg_height_: A integer in pixels to note the height for each of the legend segments.
            Alternatively, this can be a text string ending in a % sign to
            denote the percentage of the screen (eg. 5%). The default is set
            to make most legends readable on standard resolution
            screens (25px for horizontal and 36px for vertical).
        seg_width_: An integer in pixels to set the width of each of the legend segments.
            Alternatively, this can be a text string ending in a % sign to
            denote the percentage of the screen (eg. 5%). The default is set
            to make most legends readable on standard resolution
            screens (36px for horizontal and 25px for vertical).
        text_height_: An integer in pixels to set the height for the legend text.
            Alternatively, this can be a text string ending in a % sign to
            denote the percentage of the screen (eg. 2%).

    Returns:
        leg_par: A legend parameter object that can be plugged into the "LB Preview
            VisualizationSet" component to specify the properties of a
            screen-oriented legend.
"""

ghenv.Component.Name = 'LB Legend 2D Parameters'
ghenv.Component.NickName = 'Legend2D'
ghenv.Component.Message = '1.6.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


try:
    from ladybug.legend import Legend2DParameters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))


def parse_dim_text(dim_text):
    """Parse text representing a dimension into an input for legend parameters."""
    try:
        px_txt = int(dim_text)
        return '{}px'.format(px_txt)
    except ValueError:
        return dim_text


# parse all of the inputs
origin_x_ = parse_dim_text(origin_x_) if origin_x_ is not None else None
origin_y_ = parse_dim_text(origin_y_) if origin_y_ is not None else None
seg_height_ = parse_dim_text(seg_height_) if seg_height_ is not None else None
seg_width_ = parse_dim_text(seg_width_) if seg_width_ is not None else None
text_height_ = parse_dim_text(text_height_) if text_height_ is not None else None

# make the 2D legend parameters
leg_par2d = Legend2DParameters(origin_x_, origin_y_, seg_height_, seg_width_, text_height_)
