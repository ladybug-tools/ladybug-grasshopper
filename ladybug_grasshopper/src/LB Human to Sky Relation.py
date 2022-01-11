# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2022, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate parameters for the relationship between human geometry and the sky given
the position of a human subject and context geometry surrounding this position.
_
The outputs of this component can be plugged into either the "LB Outdoor Solar MRT"
or the "LB Indoor Solar MRT" in order to account for context shading around a
human subject in these MRT calculations.
-

    Args:
        north_: A number between -360 and 360 for the counterclockwise
            difference between the North and the positive Y-axis in degrees.
            90 is West and 270 is East. This can also be Vector for the
            direction to North. (Default: 0)
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component, the "LB Import Location" component, or the "LB Construct
            Location" component. This will be used to compute hourly sun
            positions for the fract_body_exp.
        _position: A point for the position of the human subject in the Rhino scene.
            This is used to understand where a person is in relationship to the
            _context. The point input here should be at the feet of the human
            a series of points will be generated above. This can also be a list
            of points, which will result in several outputs.
        _context: Rhino Breps and/or Rhino Meshes representing context geometry
            that can block the human subject's direct sun and view to the sky.
        _pt_count_: A positive integer for the number of points used to represent
            the human subject geometry. Points are evenly distributed over the
            _height_ and are used to compute fracitonal values for the
            fract_body_exp in the case that only some of the points can see the
            sun. When context shade around the subject is large or coarse,
            using a single point is likely to return similar results as using
            several points. However, this number should be increased when
            context is detailed and has the potential to shade only part of
            the human subject at a given time. (Default: 1).
        _height_: A number for the the height of the human subject in the current Rhino
            Model units. (Default: 1.8 m in the equivalent Rhino Model units;
            roughly the average height of a standing adult).
        _cpu_count_: An integer to set the number of CPUs used in the execution of the
            intersection calculation. If unspecified, it will automatically default
            to one less than the number of CPUs currently available on the
            machine or 1 if only one processor is available.
        _run: Set to "True" to run the component and compute the human/sky relationship.
            If set to "False" but all other required inputs are specified, this
            component will output points showing the human subject.

    Returns:
        report: ...
        human_points: The points used to represent the human subject in the calculation
            of the fraction of the body exposed to sun. Note that these are
            generated even when _run is set to "False".
        human_line: Line representing the height of the human subject. Note that this
            is generated even when _run is set to "False".
        fract_body_exp: A data collection for the fraction of the body exposed to
            direct sunlight at each hour of the year. This can be plugged into
            the "Solar MRT" components in order to account for context shading
            in the computation of MRT.
        sky_exposure: A single number between 0 and 1 for the fraction of the sky
            vault in human subject’s view. This can be plugged into the
            "Solar MRT" components in order to account for context shading
            in the computation of MRT.
"""

ghenv.Component.Name = "LB Human to Sky Relation"
ghenv.Component.NickName = 'HumanToSky'
ghenv.Component.Message = '1.4.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '3 :: Analyze Geometry'
ghenv.Component.AdditionalHelpFromDocStrings = '3'

import math

try:
    from ladybug_geometry.geometry2d.pointvector import Vector2D
    from ladybug_geometry.geometry3d.pointvector import Point3D, Vector3D
    from ladybug_geometry.geometry3d.line import LineSegment3D
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_geometry:\n\t{}'.format(e))

try:
    from ladybug.sunpath import Sunpath
    from ladybug.viewsphere import view_sphere
    from ladybug.datacollection import HourlyContinuousCollection
    from ladybug.header import Header
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.datatype.fraction import Fraction
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import conversion_to_meters
    from ladybug_rhino.togeometry import to_point3d, to_vector2d
    from ladybug_rhino.fromgeometry import from_point3d, from_vector3d, \
        from_linesegment3d
    from ladybug_rhino.intersect import join_geometry_to_mesh, intersect_mesh_rays
    from ladybug_rhino.grasshopper import all_required_inputs, list_to_data_tree, \
        recommended_processor_count
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def human_height_points(position, height, pt_count):
    """Get a list of points and a line representing the human geometry.

    Args:
        position: Rhino point for the position of the human.
        height: Number for the height of the human.
        pt_count: Integer for the number of points representing the human.

    Returns:
         A tuple with human points as first element and human line as second.
         Both geomtries are Rhino geometries.
    """
    lb_feet_pt = to_point3d(position).move(Vector3D(0, 0, height / 100))
    lb_hum_line = LineSegment3D(lb_feet_pt, Vector3D(0, 0, height))
    lb_pts = [lb_hum_line.midpoint] if pt_count == 1 else \
        lb_hum_line.subdivide_evenly(pt_count - 1)
    if len(lb_pts) == pt_count - 1:  # sometimes tolerance kills the last point
        lb_pts.append(lb_feet_pt.move(Vector3D(0, 0, height)))
    h_points = [from_point3d(pt) for pt in lb_pts]
    return h_points, from_linesegment3d(lb_hum_line)


def fract_exposed_from_mtx(person_sun_int_matrix, day_pattern):
    """Get a Data Collection of fraction exposed values from an intersection matrix.

    Args:
        person_sun_int_matrix: An intersection matrix of 0s and 1s for the points
            of a single person.
        day_pattern: A list of 8760 booleans indicating whether the sun is
            up (True) or down (Fasle).

    Returns:
         A data collection for the fraction of body exposed.
     """
    pt_count = len(person_sun_int_matrix)
    fract_per_sun = [sum(pt_int_ar) / pt_count for pt_int_ar in zip(*person_sun_int_matrix)]
    fract_exp_vals = []
    per_sun_i = 0
    for is_sun in day_pattern:
        if is_sun:
            fract_exp_vals.append(fract_per_sun[per_sun_i])
            per_sun_i += 1
        else:
            fract_exp_vals.append(0)
    meta_dat = {'type': 'Fraction of Body Exposed to Direct Sun'}
    fract_exp_head = Header(Fraction(), 'fraction', AnalysisPeriod(), meta_dat)
    return HourlyContinuousCollection(fract_exp_head, fract_exp_vals)


def sky_exposure_from_mtx(person_sky_int_matrix, patch_weights):
    """Get a the sky exposure from an intersection matrix.

    Args:
        person_sky_int_matrix: An intersection matrix of 0s and 1s for the
            points of a person intersected with the 145 tregenza patches.
        patch_weights: A list of 145 weights to be applies to the patches.

    Returns:
         A value for the sky exposure of the person.
     """
    pt_count = len(person_sky_int_matrix)
    sky_exp_per_pt = [sum((r * w) / 145 for r, w in zip(int_list, patch_wghts))
                      for int_list in person_sky_int_matrix]
    return sum(sky_exp_per_pt) / pt_count


if all_required_inputs(ghenv.Component):
    # process the north input if specified
    if north_ is not None:  # process the north_
        try:
            north_ = math.degrees(to_vector2d(north_).angle_clockwise(Vector2D(0, 1)))
        except AttributeError:  # north angle instead of vector
            north_ = float(north_)
    else:
        north_ = 0

    # set the default point count, height, and cpu_count if unspecified
    _pt_count_ = _pt_count_ if _pt_count_ is not None else 1
    _height_ = _height_ if _height_ is not None else 1.8 / conversion_to_meters()
    workers = _cpu_count_ if _cpu_count_ is not None else recommended_processor_count()

    # create the points representing the human geometry
    human_points = []
    human_line = []
    for pos in _position:
        hpts, hlin = human_height_points(pos, _height_, _pt_count_)
        human_points.extend(hpts)
        human_line.append(hlin)

    if _run:
        # mesh the context for the intersection calculation
        shade_mesh = join_geometry_to_mesh(_context)

        # generate the sun vectors for each sun-up hour of the year
        sp = Sunpath.from_location(_location, north_)
        sun_vecs = []
        day_pattern = []
        for hoy in range(8760):
            sun = sp.calculate_sun_from_hoy(hoy)
            day_pattern.append(sun.is_during_day)
            if sun.is_during_day:
                sun_vecs.append(from_vector3d(sun.sun_vector_reversed))

        # intersect the sun vectors with the context and compute fraction exposed
        sun_int_matrix, angles = intersect_mesh_rays(
            shade_mesh, human_points, sun_vecs, cpu_count=workers)
        fract_body_exp = []
        for i in range(0, len(human_points), _pt_count_):
            fract_body_exp.append(
                fract_exposed_from_mtx(sun_int_matrix[i:i + _pt_count_], day_pattern))

        # generate the vectors and weights for sky exposure
        sky_vecs = [from_vector3d(vec) for vec in view_sphere.tregenza_dome_vectors]
        patch_wghts = view_sphere.dome_patch_weights(1)

        # compute the sky exposure
        sky_int_matrix, angles = intersect_mesh_rays(
            shade_mesh, human_points, sky_vecs, cpu_count=workers)
        sky_exposure = []
        for i in range(0, len(human_points), _pt_count_):
            sky_exposure.append(
                sky_exposure_from_mtx(sky_int_matrix[i:i + _pt_count_], patch_wghts))
