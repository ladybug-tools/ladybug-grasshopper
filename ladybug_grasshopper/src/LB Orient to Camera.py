# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Orient a series of geometries to the active viewport camera.
-

    Args:
        _geo: A series of geometries to be oriented to the camera of the active
            Rhino viewport.
        _position_: A point to be used as the origin around which the the geometry
            will be oriented. If None, the lower left corner of the bounding box
            around the geometry will be used.
        refresh_: Connect a Grasshopper "button" component to refresh the orientation
            upon hitting the button. You can also connect a Grasshopper "Timer"
            component to update the view in real time as you navigate through
            the Rhino scene.
    
    Returns:
        geo: The input geometry that has been oriented to the camera of the active
            Rhino viewport.
"""

ghenv.Component.Name = 'LB Orient to Camera'
ghenv.Component.NickName = 'OrientCam'
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug_rhino.grasshopper import all_required_inputs
    from ladybug_rhino.viewport import orient_to_camera
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    geo = orient_to_camera(_geo, _position_)
