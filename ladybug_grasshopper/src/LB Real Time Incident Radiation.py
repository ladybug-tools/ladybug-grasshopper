# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Compute Incident Radiation values for any sky matrix in real time using the Geometry/Sky
intersection matrix produced by the "LB Incident Radiation" component.
_
Using this component enables one to scroll through radiation on an hour-by-hour
or month-by-month basis in a manner that is an order of magnitude faster than
running each sky matrix through the "LB Incident Radiation" component.
_
The speed of this component is thanks to the fact that the Geometry/Sky intersection
matrix contains the relationship between the geometry and each patch of the sky.
So computing new radiation values is as simple as multiplying the sky matrix by
the intersection matrix.
-

    Args:
        _int_mtx: A Geometry/Sky Intersection Matrix from the "LB Incident Radiation" 
            component. This matrix contains the relationship between each point of
            the analyzed geometry and each patch of the sky.
        _sky_mtx: A Sky Matrix from the "LB Cumulative Sky Matrix" component, which
            describes the radiation coming from the various patches of the sky.
            The "LB Sky Dome" component can be used to visualize any sky matrix.

    Returns:
        results: A list of numbers that aligns with the points of the original analysis
            performed with the "LB Incident Radiation"  component. Each number
            indicates the cumulative incident radiation received by each of the
            points from the sky matrix in kWh/m2. To visualize these radiation
            values in the Rhino scene, connect these values to the "LB Spatial
            Heatmap" component along with the mesh output from the original
            analysis with the "LB Incident Radiation"  component.
"""

ghenv.Component.Name = 'LB Real Time Incident Radiation'
ghenv.Component.NickName = 'RTrad'
ghenv.Component.Message = '1.7.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


try:  # python 2
    from itertools import izip as zip
except ImportError:  # python 3
    pass

try:
    from ladybug_rhino.grasshopper import all_required_inputs, de_objectify_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # deconstruct the matrices and get the total radiation from each patch
    int_mtx = de_objectify_output(_int_mtx)
    sky_mtx = de_objectify_output(_sky_mtx)
    total_sky_rad = [dirr + difr for dirr, difr in zip(sky_mtx[1], sky_mtx[2])]
    ground_rad = [(sum(total_sky_rad) / len(total_sky_rad)) * sky_mtx[0][1]] * len(total_sky_rad)
    all_rad = total_sky_rad + ground_rad 

    # compute the results
    results = []
    for pt_rel in int_mtx:
        results.append(sum(r * w for r, w in zip(pt_rel, all_rad)))
