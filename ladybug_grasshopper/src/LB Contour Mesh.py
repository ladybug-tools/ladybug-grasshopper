# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2025, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Create a contoured visualization of any mesh and corresponding numerical dataset.
_
This component works similar in principle to the "LB Mesh Threshold Selector"
except that it is intended to produce multiple contours (instead of one
contour defined by a single threshold). It includes options for lableing
each contour with its threshold value and smoothing the contours for a
more appealing visualization.
-

    Args:
        _values: A list of numbers that correspond to either the number of faces
            or vertices of the _mesh.
        _mesh: A Mesh for which contours will be derived.
        legend_par_: Ladybug LegendParameters to be used to customize the min/max and
            quantity of contours to draw. These can also be used to customize
            the text height and decimal count of the contours. If None, default
            legend parameters are used. (DefaultL None).
        _smooth_iter_: The number of times that the contours will be smoothed.
            Smoothing can make the contours more visually appealing but excessive
            smoothing can cause contours to be far from the real threshold
            in the mesh. Set to zero to not perform any smoothing. (Default: 1).
        no_labels_: Set to True to produce a set of contours with no breaks for
            text labels.

    Returns:
        report: Reports, errors, warnings, etc.
        contours: A data tree (aka. list of lists) where each sub-list represents
            contours associated with a specific threshold. Contours are
            composed of Rhino Polyline and Line objects.
        labels: A data tree of of text objects that denote the numerical value associated
            with each contour. The sub-lists of this data tree match the contours.
"""

ghenv.Component.Name = 'LB Contour Mesh'
ghenv.Component.NickName = 'ContourMesh'
ghenv.Component.Message = '1.9.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_rhino.fromobjects import mesh_to_contours, label_countours
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    smooth_iter = _smooth_iter_ if _smooth_iter_ is not None else 3
    contours, thresholds = mesh_to_contours(_mesh, _values, legend_par_, smooth_iter)
    if not no_labels_:
        contours, labels = label_countours(contours, thresholds, legend_par_)
        labels = list_to_data_tree(labels)
    contours = list_to_data_tree(contours)
