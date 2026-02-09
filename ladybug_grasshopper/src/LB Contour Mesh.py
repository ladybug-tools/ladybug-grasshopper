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
contour defined by a single threshold).
_
It includes options for lableing each contour with its threshold value and
smoothing the contours for a more appealing visualization.
_
If the output of this component is not as smooth or visually appealing as expected,
this is often because there are not enough faces in the input mesh to draw a
clear set of contours. Therefore lowering the mesh grid size used for the study
or increasing the smoothness of mesh parameters will often yeild a better contour
result. Alternatively, connecting "LB Legend Parameters" with a lower seg_count_
can produce fewer contours, which may provide the algorithm with enough data to
draw the contours cleanly.
-

    Args:
        _values: A list of numbers that correspond to either the number of faces
            or vertices of the _mesh.
        _mesh: A Mesh for which contours will be derived.
        legend_par_: Ladybug LegendParameters to be used to customize the min/max and
            quantity of contours to draw. These can also be used to customize
            the decimal count of the contours. If None, default legend parameters
            are used. (DefaultL None).
        legend_title_: A text string for Legend title. Typically, the units
            of the data are used here but the type of data might also be used.
            Default is an empty string.
        global_title_: A text string to label the entire mesh.  It will be
            displayed in the lower left of the result mesh. Default is for no
            title.
        _smooth_iter_: The number of times that the contours will be smoothed.
            Smoothing can make the contours more visually appealing but excessive
            smoothing can cause contours to be far from the real threshold
            in the mesh. Set to zero to not perform any smoothing. (Default: 0).
        label_text_hgt_: An optional number to set the size of the contour text labeld
            in model units. Set to zero to completely remove labels from the
            resulting output. Default is set to a fraction of the average
            contour length.

    Returns:
        report: Reports, errors, warnings, etc.
        contours: A data tree (aka. list of lists) where each sub-list represents
            contours associated with a specific threshold. Contours are
            composed of Rhino Polyline and Line objects.
        labels: A data tree of of text objects that denote the numerical value associated
            with each contour. The sub-lists of this data tree match the contours.
        mesh: The input _mesh that has been colored with results.
        legend: Geometry representing the legend for the mesh.
        title: A text object for the global_title.
        vis_set: A VisualizationSet object for drawing a detailed version of the
            heatmap in the Rhino scene. This can be connected to
            the "LB Preview Visualization Set" component to display this
            version of the heatmap in Rhino.
"""

ghenv.Component.Name = 'LB Contour Mesh'
ghenv.Component.NickName = 'ContourMesh'
ghenv.Component.Message = '1.9.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '4 :: Extra'
ghenv.Component.AdditionalHelpFromDocStrings = '1'

try:
    from ladybug_geometry.util import coordinates_hash_3d
    from ladybug_geometry.geometry3d import Polyline3D
    from ladybug.legend import LegendParameters, LegendParametersCategorized
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_display.visualization import VisualizationSet
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import current_tolerance
    from ladybug_rhino.togeometry import to_mesh3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_polyline3d
    from ladybug_rhino.fromobjects import mesh_to_contours, label_countours, legend_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.color import color_to_color
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))
tol = current_tolerance()


if all_required_inputs(ghenv.Component):
    # if the mesh is colored by vertices, change it to be faces for cleaner visuals
    lb_mesh = to_mesh3d(_mesh)
    if len(_values) == len(lb_mesh.vertices):
        face_values = []
        for face in lb_mesh.faces:
            fv = [_values[i] for i in face]
            face_values.append(sum(fv) / len(fv))
        _values = face_values

    # set up categorized legend parameters
    l_par = legend_par_.duplicate() if legend_par_ is not None else LegendParameters()
    if legend_title_ is not None:
        l_par.title = legend_title_
    if not isinstance(l_par, LegendParametersCategorized):
        l_par.include_larger_smaller = True
        if l_par.is_segment_count_default:
            l_par.segment_count = 7
        l_par = l_par.to_categorized(_values)

    # create the contours and snap the mesh to it
    smooth_iter = _smooth_iter_ if _smooth_iter_ is not None else 0
    contours, thresholds = mesh_to_contours(_mesh, _values, l_par, 0, as_lb_geo=True)
    if smooth_iter > 0:
        smoothed_cont, pt_map = [], {}
        for polylines in contours:
            sm_cont = []
            for pl in polylines:
                if isinstance(pl, Polyline3D):
                    smooth_pl = pl
                    for i in range(smooth_iter):
                        smooth_pl = smooth_pl.smooth()
                    sm_cont.append(smooth_pl)
                    for opt, npt in zip(pl, smooth_pl):
                        pt_map[coordinates_hash_3d(opt, tol)] = npt
                else:
                    sm_cont.append(pl)
            smoothed_cont.append(sm_cont)
        contours = smoothed_cont
        lb_mesh = lb_mesh.apply_point_map(pt_map, tol)

    # create the labels
    if label_text_hgt_ is None or label_text_hgt_ > 0:
        if label_text_hgt_ is not None or not l_par.is_text_height_default:
            lbl_l_par = l_par.duplicate()
            lbl_l_par.text_height = label_text_hgt_
        else:
            lbl_l_par = l_par
        contours, labels = label_countours(contours, thresholds, lbl_l_par)
        labels = list_to_data_tree(labels)
    else:
        contours = [[from_polyline3d(pl) for pl in cont] for cont in contours]

    # create the VisualizationSet and GraphicContainer
    vis_set = VisualizationSet.from_single_analysis_geo(
        'Data_Mesh', [lb_mesh], _values, l_par)
    graphic = vis_set.graphic_container()

    # generate titles
    if global_title_ is not None:
        title = text_objects(global_title_, graphic.lower_title_location,
                             graphic.legend_parameters.text_height * 1.5,
                             graphic.legend_parameters.font)

    # draw rhino objects
    contours = list_to_data_tree(contours)
    lb_mesh.colors = graphic.value_colors
    mesh = from_mesh3d(lb_mesh)
    legend = legend_objects(graphic.legend)
