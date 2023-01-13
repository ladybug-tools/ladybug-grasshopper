# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Select a sub-region of a mesh using aligned values and conditional criteria.
_
This has multiple uses and can be applied to any study that outputs a list of
results that are aligned with a mesh. For example, quantifying the daylit area
from a daylight analysis, selecting the portion of a roof with enough solar
radiation for photovoltaic panels, etc.
-

    Args:
        _values: A list of numbers that correspond to either the number of faces
            or vertices of the _mesh.
        _mesh: The mesh from which a sub-region will be selected. This is typically
            a colored mesh output from a study.
        _operator_: A text string representing an operator for the the conditional statement. 
            The default is greater than (>).  This must be an operator in python
            and examples include the following:
                * > - Greater Than
                * < - Less Than
                * >= - Greater or Equal
                * <= - Less or Equal
                * == - Equals
                * != - Does not Equal
        _pct_threshold_: A number between 0 and 100 that represents the percentage
            of the mesh faces or vertices to be included in the resulting
            sub_mesh. (Default: 25%).
        abs_threshold_: An optional number that represents the absolute threshold above
            which a given mesh face or vertex is included in the resulting
            sub_mesh. An input here will override the percent threshold input
            above.

    Returns:
        report: Reports, errors, warnings, etc.
        total_value: The sum of each value that meets the criteria multiplied by the
            corresponding mesh face area. This can generally be used to
            understand how much value is captured according to the conditional
            critera. For example, if the input _mesh is a radiation study,
            this is equal to the total radiation falling on the sub_mesh.
            This may or may not be meaningful depending on the units of the
            connected _values. This output will always be zero for cases
            where values correspond to mesh vertices and not faces.
        total_area: The area of the sub_mesh that meets the criteria.
        sub_mesh: A new mesh with the faces or vertices removed to reveal just the portion
            that satisfies the conditional criteria. By default, this is hidden
            to that just the outline appears in the geometry preview.
        outline: A set of lines outlining the portion of the mesh that is above
            the threshold.
"""

ghenv.Component.Name = 'LB Mesh Threshold Selector'
ghenv.Component.NickName = 'MeshSelector'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_rhino.togeometry import to_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d_to_outline
    from ladybug_rhino.grasshopper import all_required_inputs, hide_output
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # check the input values and provide defaults
    lb_mesh = to_mesh3d(_mesh)
    val_count = len(_values)
    face_match = val_count == len(lb_mesh.faces)
    assert face_match or val_count == len(lb_mesh.vertices), \
        'Number of _values ({}) must match the number of mesh faces ({}) or ' \
        'the number of mesh vertices ({}).'.format(
            val_count, len(lb_mesh.faces), len(lb_mesh.faces))
    fract_thresh = 0.25 if _pct_threshold_ is None else _pct_threshold_ / 100
    operator = '>' if _operator_ is None else _operator_.strip()
    if operator in ('==', '!='):
        assert abs_threshold_ is not None, 'An abs_threshold_ must be ' \
            'specified to use the "{}" operator.'.format(operator)

    # get a list of boolean values that meet the conditional criteria
    if abs_threshold_ is not None:
        statement = '{} ' + operator + str(abs_threshold_)
        pattern = []
        for val in _values:
            pattern.append(eval(statement.format(val), {}))
    else:
        pattern = [False] * val_count
        target_count = int(fract_thresh * (val_count))
        face_i_sort = [x for (y, x) in sorted(zip(_values, range(val_count)))]
        rel_values = list(reversed(face_i_sort)) if '>' in operator else face_i_sort
        for cnt in rel_values[:target_count]:
            pattern[cnt] = True

    # remove the faces or vertices from the mesh and compute the outputs
    sub_mesh_lb, vf_pattern = lb_mesh.remove_faces(pattern) if face_match else \
        lb_mesh.remove_vertices(pattern)
    total_value, total_area = 0, 0
    if face_match:
        for incl, val, area in zip(pattern, _values, lb_mesh.face_areas):
            if incl:
                total_area += area
                total_value += val * area
    else:
        total_area = sub_mesh_lb.area

    # convert everything to Rhino geometry
    sub_mesh, outline = from_mesh3d_to_outline(sub_mesh_lb)
    hide_output(ghenv.Component, 3)