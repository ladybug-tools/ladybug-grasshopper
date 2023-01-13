# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Visualize a sky matrix from the "LB Cumulative Sky Matrix" component as a colored
dome, subdivided into patches with a radiation value for each patch.
-

    Args:
        _sky_mtx: A Sky Matrix from the "LB Cumulative Sky Matrix" component or the
            "LB Benefit Sky Matrix" component, which describes the radiation
            coming from the various patches of the sky.
        _center_pt_: A point for the center of the dome. (Default: (0, 0, 0))
        _scale_: A number to set the scale of the sky dome. The default is 1,
            which corresponds to a radius of 100 meters in the current Rhino
            model's unit system.
        projection_: Optional text for the name of a projection to use from the sky
            dome hemisphere to the 2D plane. If None, a 3D sky dome will be drawn
            instead of a 2D one. (Default: None) Choose from the following:
                * Orthographic
                * Stereographic
        irradiance_: Boolean to note whether the sky dome should be plotted with units of
            cumulative Radiation (kWh/m2) [False] or with units of average
            Irradiance (W/m2) [True]. (Default: False).
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
        legend: A legend showing the kWh/m2 or W/m2 values that correspond to the colors
            of the mesh.
        title: A text object for the title of the sky dome.
        patch_vecs: A list of vectors for each of the patches of the sky dome.
            All vectors are unit vectors and point from the center towards each
            of the patches. They can be used to construct visualizations of the
            rays used to perform radiation analysis.
        patch_values: Radiation values for each of the sky patches in kWh/m2 or W/m2.
            This will be one list if show_comp_ is "False" and a list of 3
            lists (aka. a Data Tree) for total, direct, diffuse if show_comp_
            is "True".
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
        vis_set: An object containing VisualizationSet arguments for drawing a detailed
            version of the Sky Dome in the Rhino scene. This can be connected to
            the "LB Preview Visualization Set" component to display this version
            of the Sky Dome in Rhino.
"""

ghenv.Component.Name = 'LB Sky Dome'
ghenv.Component.NickName = 'SkyDome'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

try:
    from ladybug_geometry.geometry3d.pointvector import Point3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug_radiance.visualize.skydome import SkyDome
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_radiance:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point3d
    from ladybug_rhino.fromgeometry import from_mesh3d, from_vector3d
    from ladybug_rhino.fromobjects import legend_objects, compass_objects
    from ladybug_rhino.text import text_objects
    from ladybug_rhino.grasshopper import all_required_inputs, \
        objectify_output, list_to_data_tree
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def translate_dome(lb_mesh, lb_compass, graphic, title_txt, values):
    """Translate sky dome geometry into a format suitable for Rhino.

    Args:
        lb_mesh: A ladybug Mesh3D for the dome.
        lb_compass: A ladybug Compass object.
        graphic: A GraphicContainer for the dome.
        title_txt: Text for title of the dome.
        values: A list of radiation values that align with the dome_mesh faces.

    Returns:
        dome_mesh: A Rhino colored mesh for the dome.
        dome_compass: Rhino objects for the dome compass.
        dome_legend:  Rhino objects for the dome legend.
        dome_title: A bake-able title for the dome.
        values: A list of radiation values that align with the dome_mesh faces.
    """
    # translate the dome visualization, including legend and compass
    dome_mesh = from_mesh3d(lb_mesh)
    dome_legend = legend_objects(graphic.legend)
    dome_compass = compass_objects(
        lb_compass, z, None, sky_dome.projection, graphic.legend_parameters.font)

    # construct a title from the metadata
    dome_title = text_objects(title_txt, graphic.lower_title_location,
                              graphic.legend_parameters.text_height,
                              graphic.legend_parameters.font)

    return dome_mesh, dome_compass, dome_legend, dome_title, values


if all_required_inputs(ghenv.Component):
    # set defaults for global variables
    _scale_ = 1 if _scale_ is None else _scale_
    radius = (100 * _scale_) / conversion_to_meters()
    if _center_pt_ is not None:  # process the center point
        center_pt3d = to_point3d(_center_pt_)
        z = center_pt3d.z
    else:
        center_pt3d, z = Point3D(), 0

    # create the SkyDome object
    sky_dome = SkyDome(_sky_mtx, legend_par_, irradiance_,
                       center_pt3d, radius, projection_)

    # output patch patch vectors
    patch_vecs = [from_vector3d(vec) for vec in sky_dome.patch_vectors]

    # create the dome visualization
    if not show_comp_:  # only create the total dome mesh
        mesh, compass, legend, title, mesh_values = translate_dome(*sky_dome.draw())
        patch_values = sky_dome.total_values
    else:  # create domes for total, direct and diffuse
        # loop through the 3 radiation types and produce a dome
        mesh, compass, legend, title, mesh_values = [], [], [], [], []
        rad_types = ('total', 'direct', 'diffuse')
        for dome_i in range(3):
            cent_pt = Point3D(center_pt3d.x + radius * 3 * dome_i,
                              center_pt3d.y, center_pt3d.z)
            dome_mesh, dome_compass, dome_legend, dome_title, dome_values = \
                translate_dome(*sky_dome.draw(rad_types[dome_i], cent_pt))
            mesh.append(dome_mesh)
            compass.extend(dome_compass)
            legend.extend(dome_legend)
            title.append(dome_title)
            mesh_values.append(dome_values)
        rad_data = (sky_dome.total_values, sky_dome.direct_values, sky_dome.diffuse_values)
        patch_values = list_to_data_tree(rad_data)
        mesh_values = list_to_data_tree(mesh_values)

    # output the visualization set
    vis_set = [sky_dome, show_comp_]
    vis_set = objectify_output('VisualizationSet Aruments [SkyDome]', vis_set)
