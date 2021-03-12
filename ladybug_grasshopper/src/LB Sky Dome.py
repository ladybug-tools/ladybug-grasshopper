# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2021, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Visualize a sky matrix from the "LB Cumulative Sky Matrix" component as a colored
dome, subdivided into patches with a radiation value for each patch.
-

    Args:
        _sky_mtx: A Sky Matrix from the "LB Cumulative Sky Matrix" component, which
            describes the radiation coming from the various patches of the sky.
        _center_pt_: A point for the center of the dome. (Default: (0, 0, 0))
        _scale_: A number to set the scale of the sky dome. The default is 1,
            which corresponds to a radius of 100 meters in the current Rhino
            model's unit system.
        projection_: Optional text for the name of a projection to use from the sky
            dome hemisphere to the 2D plane. If None, a 3D sky dome will be drawn
            instead of a 2D one. (Default: None) Choose from the following:
                * Orthographic
                * Stereographic
        show_comp_: Boolean to indicate whether only one dome with total radiation
            should be displayed (False) or three domes with the solar radiation
            components (total, direct, and diffuse) should be shown. (Default: False).
        legend_par_: An optional LegendParameter object to change the display of the
            sky dome (Default: None).

    Returns:
        report: ...
        mesh:  A colored mesh representing the intensity of radiation for each of
            the sky patches within the sky dome.
        compass: A set of circles, lines and text objects that mark the cardinal
            directions in relation to the sky dome.
        legend: A legend showing the kWh/m2 values that correspond to the colors
            of the mesh.
        title: A text object for the title of the sunpath.
        patch_vecs: A list of vectors for each of the patches of the sky dome.
            All vectors are unit vectors and point from the center towards each
            of the patches. They can be used to construct visualizations of the
            rays used to perform radiation analysis.
        patch_values: Radiation values for each of the sky patches in kWh/m2. This
            will be one list if show_comp_ is "False" and a list of 3 lists (aka.
            a Data Tree) for total, direct, diffuse if show_comp_ is "True".
        mesh_values: Radiation values for each face of the dome mesh in kWh/m2. This
            can be used to post-process the radiation data and then regenerate
            the dome visualization using the mesh output from this component
            and the "LB Spatial Heatmap" component. Examples of useful post-
            processing include converting the units to something other than
            kWh/m2, inverting the +/- sign of radiation values depending on
            whether radiation is helpful or harmful to building thermal loads,
            etc. This will be one list if show_comp_ is "False" and a list of
            3 lists (aka. a Data Tree) for total, direct, diffuse if show_comp_
            is "True".
"""

ghenv.Component.Name = 'LB Sky Dome'
ghenv.Component.NickName = 'SkyDome'
ghenv.Component.Message = '1.2.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import math

try:
    from ladybug_geometry.geometry2d.pointvector import Point2D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.mesh import Mesh3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.viewsphere import view_sphere
    from ladybug.compass import Compass
    from ladybug.graphic import GraphicContainer
    from ladybug.legend import LegendParameters
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_vector3d
    from ladybug_rhino.fromobjects import legend_objects, compass_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.grasshopper import all_required_inputs, \
        de_objectify_output, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def draw_dome(dome_data, center, dome_name, legend_par):
    """Draw the dome mesh, compass, legend, and title for a sky dome.

    Args:
        dome_data: List of radiation values for the dome data
        center: Point3D for the center of the sun path.
        dome_name: Text for the dome name, which will appear in the title.
        legend_par: Legend parameters to be used for the dome

    Returns:
        dome_mesh: A colored mesh for the dome based on dome_data.
        dome_compass: A compass for the dome.
        dome_legend: A leend for the colored dome mesh.
        dome_title: A title for the dome.
        values: A list of radiation values that align with the dome_mesh faces.
    """
    # create the dome mesh and ensure patch values align with mesh faces
    if len(dome_data) == 145:  # tregenza sky
        lb_mesh = view_sphere.tregenza_dome_mesh_high_res.scale(radius)
        values = []  # high res dome has 3 x 3 faces per patch; we must convert
        tot_i = 0  # track the total number of patches converted
        for patch_i in view_sphere.TREGENZA_PATCHES_PER_ROW:
            row_vals = []
            for val in dome_data[tot_i:tot_i + patch_i]:
                row_vals.extend([val] * 3)
            for i in range(3):
                values.extend(row_vals)
            tot_i += patch_i
        values = values + [dome_data[-1]] * 18  # last patch has triangular faces
    else:  #reinhart sky
        lb_mesh = view_sphere.reinhart_dome_mesh.scale(radius)
        values = dome_data + [dome_data[-1]] * 11  # last patch has triangular faces

    # move and/or rotate the mesh as needed
    if north != 0:
        lb_mesh = lb_mesh.rotate_xy(math.radians(north), Point3D())
    if center != Point3D():
        lb_mesh = lb_mesh.move(Vector3D(center.x, center.y, center.z))

    # project the mesh if requested
    if projection_ is not None:
        if projection_.title() == 'Orthographic':
            pts = (Compass.point3d_to_orthographic(pt) for pt in lb_mesh.vertices)
        elif projection_.title() == 'Stereographic':
            pts = (Compass.point3d_to_stereographic(pt, radius, center)
                   for pt in lb_mesh.vertices)
        else:
            raise ValueError(
                'Projection type "{}" is not recognized.'.format(projection_))
        pts3d = tuple(Point3D(pt.x, pt.y, z) for pt in pts)
        lb_mesh = Mesh3D(pts3d, lb_mesh.faces)

    # output the dome visualization, including legend and compass
    move_fac = radius * 0.15
    min_pt = lb_mesh.min.move(Vector3D(-move_fac, -move_fac, 0))
    max_pt = lb_mesh.max.move(Vector3D(move_fac, move_fac, 0))
    graphic = GraphicContainer(values, min_pt, max_pt, legend_par)
    graphic.legend_parameters.title = 'kWh/m2'
    lb_mesh.colors = graphic.value_colors
    dome_mesh = from_mesh3d(lb_mesh)
    dome_legend = legend_objects(graphic.legend)
    dome_compass = compass_objects(
        Compass(radius, Point2D(center.x, center.y), north), z, None, projection_,
        graphic.legend_parameters.font)

    # construct a title from the metadata
    st, end = metadata[1], metadata[2]
    time_str = '{} - {}'.format(st, end) if st != end else st
    title_txt = '{} Radiation\n{}\n{}'.format(
        dome_name, time_str, '\n'.join([dat for dat in metadata[3:]]))
    dome_title = text_objects(title_txt, graphic.lower_title_location,
                              graphic.legend_parameters.text_height,
                              graphic.legend_parameters.font)

    return dome_mesh, dome_compass, dome_legend, dome_title, values


if all_required_inputs(ghenv.Component):
    # set defaults for global variables
    _scale_ = 1 if _scale_ is None else _scale_
    radius = (100 * _scale_) / conversion_to_meters()
    if _center_pt_ is not None:  # process the center point into a Point2D
        center_pt3d = to_point3d(_center_pt_)
        z = center_pt3d.z
    else:
        center_pt3d, z = Point3D(), 0

    # deconstruct the sky matrix and derive key data from it
    metadata, direct, diffuse = de_objectify_output(_sky_mtx)
    north = metadata[0]  # first item is the north angle
    sky_type = 1 if len(direct) == 145 else 2  # i for tregenza; 2 for reinhart
    total = [dirr + difr for dirr, difr in zip(direct, diffuse)] # total radiation

    # override the legend default min and max to make sense for domes
    l_par = legend_par_.duplicate() if legend_par_ is not None else LegendParameters()
    if l_par.min is None:
        l_par.min = 0
    if l_par.max is None:
        l_par.max = max(total)

    # output patch patch vectors
    patch_vecs_lb = view_sphere.tregenza_dome_vectors if len(total) == 145 \
        else view_sphere.reinhart_dome_vectors
    patch_vecs = [from_vector3d(vec) for vec in patch_vecs_lb]

    # create the dome meshes
    if not show_comp_:  # only create the total dome mesh
        mesh, compass, legend, title, mesh_values = \
            draw_dome(total, center_pt3d, 'Total', l_par)
        patch_values = total
    else:  # create domes for total, direct and diffuse
        # loop through the 3 radiation types and produce a dome
        mesh, compass, legend, title, mesh_values = [], [], [], [], []
        rad_types = ('Total', 'Direct', 'Diffuse')
        rad_data = (total, direct, diffuse)
        for dome_i in range(3):
            cent_pt = Point3D(center_pt3d.x + radius * 3 * dome_i,
                              center_pt3d.y, center_pt3d.z)
            dome_mesh, dome_compass, dome_legend, dome_title, dome_values = \
                draw_dome(rad_data[dome_i], cent_pt, rad_types[dome_i], l_par)
            mesh.append(dome_mesh)
            compass.extend(dome_compass)
            legend.extend(dome_legend)
            title.append(dome_title)
            mesh_values.append(dome_values)
        patch_values = list_to_data_tree(rad_data)
        mesh_values = list_to_data_tree(mesh_values)
