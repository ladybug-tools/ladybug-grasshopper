# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Compute solar infomation about a day of the year at a particular location. This includes
the time of sunrise, sunset, solar noon, and the length of the day in hours.
_
Note that these times are intended to represent a typical year and they will often
vary by a few minutes depending on where in the leap year cycle a given year falls.
-

    Args:
        _location: A ladybug Location that has been output from the "LB Import EPW"
            component or the "LB Construct Location" component.
        _doy: An integer for the day of the year for which solar information is
            be computed. The "LB Calculate HOY" component can be used to compute
            the day of the year from month and day inputs.
        _depression_: An angle in degrees indicating the additional period before/after
            the edge of the sun has passed the horizon where the sun is still
            considered up. Setting this value to 0 will compute sunrise/sunset
            as the time when the edge of the sun begins to touch the horizon.
            Setting it to the angular diameter of the sun (0.5334) will compute
            sunrise/sunset as the time when the sun just finishes passing the
            horizon (actual physical sunset). Setting it to 0.833 will compute
            the apparent sunrise/sunset, accounting for atmospheric refraction.
            Setting this to 6 will compute sunrise/sunset as the beginning/end
            of civil twilight. Setting this to 12 will compute sunrise/sunset
            as the beginning/end of nautical twilight. Setting this to 18 will
            compute sunrise/sunset as the beginning/end of astronomical
            twilight. (Default: 0.5334 for the physical sunset).
        solar_time_: A boolean to indicate if the output datetimes for sunrise,
            noon and sunset should be in solar time as opposed to the time zone
            of the location. (Default: False).
        dl_saving_: An optional analysis period for daylight saving time. This will be used
            to adjust the output times by an hour when applicable. If unspecified,
            no daylight saving time will be used

    Returns:
        sunrise: The time of sunrise expressed as HH:MM where hours range from 0 to 23.
            Note that this may be None if there is no sunrise or sunset on the
            specified day. (eg. at the north pole on the winter solstice).
        sunset: The time of sunset expressed as HH:MM where hours range from 0 to 23.
            Note that this may be None if there is no sunrise or sunset on the
            specified day. (eg. at the north pole on the winter solstice).
        solar_noon: The time of solar noon when the sun is at its highest point in the
            sky, expressed as HH:MM.
        noon_alt: The altitude of the sun at solar noon in degrees. This is the maximum
            altitude that will be expereinced on the input day.
        day_length: The length of the input day in hours.
"""

ghenv.Component.Name = 'LB Day Solar Information'
ghenv.Component.NickName = 'DayInfo'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.sunpath import Sunpath
    from ladybug.dt import Date
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    # set default values
    solar_time_ = False if solar_time_ is None else solar_time_  # process solar time
    _depression_ = 0.5334 if _depression_ is None else _depression_

    # initialize sunpath based on location
    sp = Sunpath.from_location(_location, 0, dl_saving_)

    # for each day of the year, compute the information
    sunrise, sunset, solar_noon, noon_alt, day_length = [], [], [], [], []
    for doy in _doy:
        doy_date = Date.from_doy(doy)
        solar_info = sp.calculate_sunrise_sunset(
            doy_date.month, doy_date.day, _depression_, solar_time_)
        print(solar_info)
        sr, sn, ss = solar_info['sunrise'], solar_info['noon'], solar_info['sunset']
        solar_noon.append(sn.time)
        noon_alt.append(sp.calculate_sun_from_date_time(sn).altitude)
        if sr is not None:
            sunrise.append(sr.time)
        else:
            sunrise.append(None)
        if ss is not None:
            sunset.append(ss.time)
            day_length.append((ss - sr).total_seconds() / 3600)
        else:
            sunset.append(None)
            day_length.append(None)
