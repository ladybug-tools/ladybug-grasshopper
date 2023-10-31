# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Draw thermal comfort polygons on a Psychrometric Chart using the UTCI outdoor
thermal comfort model.
-

    Args:
        _psyc_chart: A ladybug Psychrometric Chart object on which the UTCI comfort
            polygons will be plot. This can be obtained from the "LB Psychrometric
            Chart" component.
        _mrt_: A number or list of numbers for the mean radiant temperature. These
            should be in Celsius if the Psychrometric Chart is in SI and
            Farenheit if the Psychrometric Chart is in IP. If None, a polygon for
            operative temperature will be plot, assuming that radiant temperature
            and air temperature are the same. (Default: None).
        _wind_speed_: A number or list of numbers for for the meteorological wind speed
            values in m/s (measured 10 m above the ground). If None, this will
            default to a low wind speed of 0.5 m/s, which is the lowest input
            speed that is recommended for the UTCI model.
        utci_par_: Optional UTCIParameter object to specify parameters under
            which conditions are considered acceptable. If None, default will
            assume comfort thresholds consistent with those used by meteorologists
            to categorize outdoor conditions.
        merge_poly_: Boolean to note whether all comfort polygons should be merged
            into a single polygon instead of separate polygons for each set of
            input conditions. (Default: False).
        plot_stress_: Boolean to note whether polygons for heat/cold stress should be plotted
            in the output. This will include 3 polygons on either side of the comfort
            polygon(s) for...
            _
            * Moderate Stress
            * Strong Stress
            * Very Strong Stress

    Returns:
        report: ...
        total_comfort: The percent of the data on the psychrometric chart that
            are inside all comfort polygons.
        total_comf_data: Data collection or a 0/1 value noting whether each of the data
            points on the psychrometric chart lies inside of a comfort polygon.
            _
            This can be connected to the "LB Create Legend" component to generate
            a list of colors that can be used to color the points output from
            "LB Psychrometric Chart" component to see exactly which points are
            comfortable and which are not.
            _
            Values are one of the following:
                0 = uncomfortable
                1 = comfortable
        polygons: A list of Breps representing the range of comfort (or heat/cold stress) for the
            input mrt and air speed.
        polygon_names:  A list of names for each of the polygons which correspond with the polygons
            output above. This will include both the comfort polygons and the
            cold/heat stress polygons.
        polygon_data: A list of data collections or 0/1 values indicating whether each 
            of the data points on the psychrometric chart lies inside each of
            the comfort polygons. Each data collection or here corresponds to the
            names in the polygon_names output above.
            _
            Values are one of the following:
                0 = outside
                1 = inside
"""

ghenv.Component.Name = 'LB UTCI Polygon'
ghenv.Component.NickName = 'UTCI Polygon'
ghenv.Component.Message = '1.7.1'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '2 :: Visualize Data'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug.psychchart import PsychrometricChart
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_comfort.chart.polygonutci import PolygonUTCI
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_comfort:\n\t{}'.format(e))

try:
    from ladybug_rhino.config import tolerance
    from ladybug_rhino.fromgeometry import from_polyline2d_to_offset_brep
    from ladybug_rhino.grasshopper import all_required_inputs, \
        list_to_data_tree, give_warning
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def strategy_warning(polygon_name):
    """Give a warning about a polygon not fitting on the chart."""
    msg = 'Polygon "{}" could not fit on the chart given the current location of ' \
        'the comfort polygon(s).\nTry moving the comfort polygon(s) by changing ' \
        'its criteria to see the missing polygon.'.format(polygon_name)
    give_warning(ghenv.Component, msg)
    print(msg)


def process_polygon(polygon_name, polygon):
    """Process a strategy polygon that does not require any special treatment."""
    if polygon is not None:
        polygon_names.append(polygon_name)
        strategy_poly.append(from_polyline2d_to_offset_brep(polygon, offset, z))
        dat = poly_obj.evaluate_polygon(polygon, tolerance)
        dat = dat[0] if len(dat) == 1 else poly_obj.create_collection(dat, polygon_name)
        polygon_data.append(dat)
    else:
        strategy_warning(polygon_name)


def merge_polygon_data(poly_data):
    """Merge an array of polygon comfort conditions into a single data list."""
    val_mtx = [dat.values for dat in poly_data]
    merged_values = []
    for hr_data in zip(*val_mtx):
        hr_val = 1 if 1 in hr_data else 0
        merged_values.append(hr_val)
    return merged_values


if all_required_inputs(ghenv.Component):
    # convert the temperature values to C if the polygon is in IP
    assert isinstance(_psych_chart, PsychrometricChart), 'PolygonUTCI ' \
        'psychrometric chart must be a ladybug PsychrometricChart. ' \
        'Got {}.'.format(type(_psych_chart))
    z = _psych_chart.z
    offset = _psych_chart.x_dim * 0.25
    if _psych_chart.use_ip:
        _mrt_ = PolygonUTCI.TEMP_TYPE.to_unit(_mrt_, 'C', 'F')

    # create the PolygonUTCI object
    poly_obj = PolygonUTCI(_psych_chart, _mrt_, _wind_speed_, comfort_parameter=utci_par_)

    # draw the comfort polygon
    polygon_names = []
    comfort_data = []
    if merge_poly_:
        polygons = [from_polyline2d_to_offset_brep(poly_obj.merged_comfort_polygon, offset, z)]
        comfort_data.append(poly_obj.merged_comfort_data)
        polygon_names.append('Comfort')
    else:
        polygons = [
            from_polyline2d_to_offset_brep(poly, offset, z)
            for poly in poly_obj.comfort_polygons
        ]
        comfort_data.extend(poly_obj.comfort_data)
        if len(polygons) == 1:
            polygon_names.append('Comfort')
        else:
            names = ('Comfort {}'.format(i + 1) for i in range(len(polygons)))
            polygon_names.extend(names)

    # draw the cold/heat stress polygons if requested
    polygon_data = comfort_data[:]
    if plot_stress_:
        stress_polys = (
            poly_obj.moderate_cold_polygon, poly_obj.strong_cold_polygon,
            poly_obj.very_strong_cold_polygon, poly_obj.moderate_heat_polygon,
            poly_obj.strong_heat_polygon, poly_obj.very_strong_heat_polygon
        )
        stress_names = (
            'Moderate Cold Stress', 'Strong Cold Stress',
            'Very Strong Cold Stress', 'Moderate Heat Stress',
            'Strong Heat Stress', 'Very Strong Heat Stress'
        )
        for poly, name in zip(stress_polys, stress_names):
            stress_data = poly_obj.evaluate_inside(poly[0], poly[2], name)
            if 'Cold' in name:
                polygons.insert(0, from_polyline2d_to_offset_brep(poly, offset, z))
                polygon_names.insert(0, name)
                polygon_data.insert(0, stress_data)
            else:
                polygons.append(from_polyline2d_to_offset_brep(poly, offset, z))
                polygon_names.append(name)
                polygon_data.append(stress_data)

    # compute total comfort values
    polygon_comfort = [dat.average * 100 for dat in comfort_data] if \
        isinstance(comfort_data[0], BaseCollection) else \
        [dat * 100 for dat in comfort_data]
    if isinstance(comfort_data[0], BaseCollection):
        merged_vals = merge_polygon_data(comfort_data)
        total_comf_data = poly_obj.create_collection(merged_vals, 'Total Comfort')
        total_comfort = total_comf_data.average * 100
    else:
        total_comf_data = 1 if sum(comfort_data) > 0 else 0
        total_comfort = total_comf_data * 100
