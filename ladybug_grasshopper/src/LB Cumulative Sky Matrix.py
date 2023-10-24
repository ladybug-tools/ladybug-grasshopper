# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Get a matrix containing radiation values from each patch of a sky dome.
_
Creating this matrix is a necessary pre-step before doing incident radiation
analysis with Rhino geometry or generating a radiation rose.
_
This component uses Radiance's gendaymtx function to calculate the radiation
for each patch of the sky. Gendaymtx is written by Ian Ashdown and Greg Ward.
Morere information can be found in Radiance manual at:
http://www.radiance-online.org/learning/documentation/manual-pages/pdfs/gendaymtx.pdf
-

    Args:
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component or the "LB Construct Location" component.
        _direct_rad: An annual hourly DataCollection of Direct Normal Radiation such
            as that which is output from the "LB Import EPW" component or the
            "LB Import STAT" component.
        _diffuse_rad: An annual hourly DataCollection of Diffuse Horizontal Radiation
            such as that which is output from the "LB Import EPW" component or
            the "LB Import STAT" component.
        _hoys_: A number or list of numbers between 0 and 8760 that respresent
            the hour(s) of the year for which to generate the sky matrix. The
            "LB Calculate HOY" component can output this number given a month,
            day and hour. The "LB Analysis Period" component can output a
            list of HOYs within a certain hour or date range. By default,
            the matrix will be for the entire year.
        high_density_: A Boolean to indicate whether the higher-density Reinhart sky
            matrix should be generated (True), which has roughly 4 times the sky
            patches as the (default) original Tregenza sky (False). Note that,
            while the Reinhart sky has a higher resolution and is more accurate,
            it will result in considerably longer calculation time for incident
            radiation studies. The difference in sky resolution can be observed
            with the "LB Sky Dome" component. (Default: False).
        _ground_ref_: A number between 0 and 1 to note the average ground reflectance
            that is associated with the sky matrix. (Default: 0.2).
        _folder_: The folder in which the Radiance commands are executed to
            produce the sky matrix. If None, it will be written to Ladybug's
            default EPW folder.

    Returns:
        report: ...
        sky_mtx: A sky matrix object containing the radiation coming from each patch
            of the sky. This can be used for a radiation study, a radition rose,
            or a sky dome visualization. It can also be deconstructed into its
            individual values with the "LB Deconstruct Matrix" component.
"""

ghenv.Component.Name = 'LB Cumulative Sky Matrix'
ghenv.Component.NickName = 'SkyMatrix'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import math

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_radiance.skymatrix import SkyMatrix
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.togeometry import to_vector2d
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

try:
    from lbt_recipes.version import check_radiance_date
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_radiance:\n\t{}'.format(e))

# check the istalled Radiance date and get the path to the gemdaymtx executable
check_radiance_date()


if all_required_inputs(ghenv.Component):
    # process and set defaults for all of the global inputs
    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(
                to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
    else:
        north_ = 0
    ground_r = 0.2 if _ground_ref_ is None else _ground_ref_

    # create the sky matrix object
    sky_mtx = SkyMatrix.from_components(
        _location, _direct_rad, _diffuse_rad, _hoys_, north_, high_density_, ground_r)
    if _folder_:
        sky_mtx.folder = _folder_
