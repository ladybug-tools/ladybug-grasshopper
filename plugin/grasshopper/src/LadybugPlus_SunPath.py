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
        _centerPt_: Input a point here to change the location of the sun path.
            The default is set to the Dynamo model origin (0,0,0).
        _scale_: Input a number here to change the scale of the sun path.
            The default is set to 1.
        _sunScale_: Input a number here to change the scale of the sun spheres
            located along the sun path.  The default is set to 1.
        _annualSunPath_: By default, this value is set to "True" (or 1) which
            will produce a sun path for the whole year. Set this input to "False"
            (or 0) to generate a sun path for just one day of the year (or
            several days if multiple days are included in the analysis period).

    Returns:
        sunVectors: Vector(s) indicating the direction of sunlight for each sun
            position on the sun path.
        sunAltitudes: Number(s) indicating the sun altitude(s) in degrees for
            each sun position on the sun path.
        sunAzimuths: Number(s) indicating the sun azimuths in degrees for each
            sun position on the sun path.
        sunSpheres: A colored mesh of spheres representing sun positions.
        geometry: A set of curves that mark the path of the sun across the sky
            dome.
        centerPt: The center point of the sun path
        sunPositions: Point(s) idicating the location on the sun path of each
            sun position.
        hoys: The hour of the year for each sun position on the sun path.
        datetimes: The date and info for each sun position on the sun path.
"""

ghenv.Component.Name = "LadybugPlus_SunPath"
ghenv.Component.NickName = 'sunpath'
ghenv.Component.Message = 'VER 0.0.01\nAUG_18_2017'
ghenv.Component.Category = "LadybugPlus"
ghenv.Component.SubCategory = "02 :: VisualizeWeatherData"
ghenv.Component.AdditionalHelpFromDocStrings = "1"


try:
    from ladybug.dt import DateTime
    from ladybug.sunpath import Sunpath
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

if _location:

    daylightSavingPeriod = None  # temporary until we fully implement it
    
    # initiate sunpath based on location
    sp = Sunpath.fromLocation(_location, north_, daylightSavingPeriod,
        basePoint=_centerPt_, scale=_scale_, sunScale=_sunScale_)
    
    # draw suns
    months = {}
    for HOY in _hoys_:
        dt = LBDateTime.fromHOY(HOY)
        sp.drawSunFromDateTime(dt)
    
    # draw daily sunpath curves
    # draw sunpath geometry
    sp.drawSunpath(_hoys_, annual=_annualSunpath_)
    #if not _annualSunpath_ and dt.DOY not in months:
    #    # add this day
    #    sp.drawDailySunpath(dt.month, dt.day)
    #    months[dt.DOY] = dt  # keep track of days not to redraw them

    # generate outputs
    suns = sp.suns
    sunCount = len(suns)
    sunVectors = range(sunCount)
    sunAltitudes = range(sunCount)
    sunAzimuths = range(sunCount)
    sunPositions = range(sunCount)
    sunDateTimes = range(sunCount)
    
    for count, sun in enumerate(suns):
        sunVectors[count] = sun.vector
        sunAltitudes[count] = sun.altitude
        sunAzimuths[count] = sun.azimuth
        sunPositions[count] = sun.position
        sunDateTimes[count] = sun.datetime
    
    geometries = sp.geometries.values()
    sunSpheres = sp.sunGeometries
    centerPoint = sp.basePoint
