# Ladybug: A Plugin for Environmental Analysis (GPL) started by Mostapha Sadeghipour Roudsari
# This file is part of Ladybug.
#
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to make a 3D sun-path (aka. sun plot).
The component also outputs sun vectors that can be used for solar access
analysis or shading design.
-
    
    Args:
        north_: Input a number between 0 and 360.
            It represents the degrees off from the y-axis to make North.
            The default North direction is set to the Y-axis (0 degrees).
        _location: The output from the importEPW or constructLocation component.
            This is essentially a list of text summarizing a location on the
            earth.
        _hoys_: A list or a single number that respresent an hour of the year.
            Use Analysis Period or HOY nodes to generate the numbers.
        _center_pt_: Input a point here to change the location of the sun path.
            The default is set to the Dynamo model origin (0,0,0).
        _scale_: Input a number here to change the scale of the sun path.
            The default is set to 1.
        _sun_scale_: Input a number here to change the scale of the sun spheres
            located along the sun path.  The default is set to 1.
        _annual_: By default, this value is set to "True" (or 1) which
            will produce a sun path for the whole year. Set this input to "False"
            (or 0) to generate a sun path for just one day of the year (or
            several days if multiple days are included in the analysis period).

    Returns:
        vectors: Vector(s) indicating the direction of sunlight for each sun
            position on the sun path.
        altitudes: Number(s) indicating the sun altitude(s) in degrees for
            each sun position on the sun path.
        azimuths: Number(s) indicating the sun azimuths in degrees for each
            sun position on the sun path.
        sun_pts: Point(s) representing the location of the sun on the sunpath.
        analemma: A set of curves that mark the hourly positions of the sun
            throughout the different months of the year.
        compass: A set of curves that mark the cardinal directions in relation
            to the sun.
        daily: A set of curves that mark the path of the sun across the sky
            dome over the course of a day.
        center_pt: The center point of the sun path
        hoys: The hour of the year for each sun position on the sun path.
        datetimes: The date and info for each sun position on the sun path.
"""

ghenv.Component.Name = "LadybugPlus_SunPath"
ghenv.Component.NickName = 'sunpath'
ghenv.Component.Message = 'VER 0.0.04\nJUN_07_2019'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "02 :: VisualizeWeatherData"
ghenv.Component.AdditionalHelpFromDocStrings = "1"

try:
    from ladybug.sunpath import Sunpath
    import ladybug.geometry as geo
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if all_required_inputs(ghenv.Component):
    daylight_saving_period = None  # temporary until we fully implement it
    _hoys_ = _hoys_ or ()

    # initiate sunpath based on location
    sp = Sunpath.from_location(_location, north_, daylight_saving_period)

    # draw sunpath geometry
    sunpath_geo = \
        sp.draw_sunpath(_hoys_, _center_pt_, _scale_, _sun_scale_, _annual_)
    
    analemma = sunpath_geo.analemma_curves
    compass = sunpath_geo.compass_curves
    daily = sunpath_geo.daily_curves
    
    sun_pts = sunpath_geo.sun_geos

    suns = sunpath_geo.suns
    vectors = (geo.vector(*sun.sun_vector) for sun in suns)
    altitudes = (sun.altitude for sun in suns)
    azimuths = (sun.azimuth for sun in suns)
    center_pt = _center_pt_ or geo.point(0, 0, 0)
    hoys = (sun.hoy for sun in suns)
    datetimes = (sun.datetime for sun in suns)