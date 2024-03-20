# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Bake a clored mesh into the Rhino scene as a group of colored hatches.
_
This is useful when exporting ladybug graphics from Rhino to vector-based programs
like Inkscape or Illustrator since hatches are exported from Rhino as colored-filled
polygons.
-

    Args:
        _mesh: A colored mesh (or list of colored meshes) to be baked into the Rhino
            scene as groups of colored hatches.
        layer_: Text for the layer name on which the hatch will be added. If unspecified,
            it will be baked onto the currently active layer.
        _run: Set to 'True' to bake the mesh into the scene as hatches.

    Returns:
        report: Reports, errors, warnings ...
"""

ghenv.Component.Name = 'LB Mesh to Hatch'
ghenv.Component.NickName = 'Hatch'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '0'


try:
    from ladybug_rhino.togeometry import to_mesh3d
    from ladybug_rhino.bakegeometry import bake_mesh3d_as_hatch
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _run:
    lb_mesh = to_mesh3d(_mesh, color_by_face=False)
    bake_mesh3d_as_hatch(lb_mesh, layer_)
