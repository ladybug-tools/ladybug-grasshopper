# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2023, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Calculate wind speed at a specific height above the ground for a given terrain type.
_
By default, the component will calculate wind speed at a height of 1 meter, which
is suitable for most thermal comfort models like PET and SET. Alternatively, by
hooking up the output wind data to the "LB Wind rose" component, a wind rose
for any terrain or at height above the ground can be produced.
_
This component uses the same wind profile function as used by the "LB Wind Profile"
component.
-

    Args:
        _met_wind_vel: A data collection of meteorological wind speed measured at
            the _met_height_ with the _met_terrian [m/s]. Typically, this comes
            from the "LB Import EPW" component. This can also be a number for
            the meteorological wind speed in m/s.
        _height_: The height above the ground to be evaluated in meters. (Default: 1 meter,
            which is suitable for most thermal comfort models like PET and SET.).
        _terrain_: Text string that sets the terrain class associated with the output air_speed.
            This can also be an integer that codes for the terrain. (Default: city).
            Must be one the following.
            _
            0 = city - 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = suburban - suburbs, wooded areas.
            2 = country - open, with scattered objects generally less than 10m high.
            3 = water - flat areas downwind of a large water body (max 500m inland).
        _met_height_: A number for the height above the ground at which the meteorological
            wind speed is measured in meters. (Default: 10 meters, which is the
            standard used by most airports and EPW files).
        _met_terrain_: Text string that sets the terrain class associated with the
            meteorological wind speed. This can also be an integer that codes
            for the terrain. (Default: country, which is typical of most
            airports where wind measurements are taken). Must be one the following.
            _
            0 = city - 50% of buildings above 21m over a distance of at least 2000m upwind.
            1 = suburban - suburbs, wooded areas.
            2 = country - open, with scattered objects generally less than 10m high.
            3 = water - flat areas downwind of a large water body (max 500m inland).
        log_law_: A boolean to note whether the wind profile should use a logarithmic
            law to determine wind speeds instead of the default power law,
            which is used by EnergyPlus. (Default: False).

    Returns:
        report: Reports, errors, warnings, etc.
        air_speed: A data collection or single value for the air speed at the input
            _height_ above the ground for the input _terrain_. This can be plugged
            into thermal comfort models like PET or SET/PMV. Alternatively, by
            connecting the wind data to the "LB Wind rose" component, a wind rose
            for the input _terrain_ and _height_ above the ground can be produced.
"""

ghenv.Component.Name = 'LB Wind Speed'
ghenv.Component.NickName = 'WindSpeed'
ghenv.Component.Message = '1.6.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '4'

try:
    from ladybug.datacollection import BaseCollection
    from ladybug.windprofile import WindProfile
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))

# dictionary to map integers to terrain types
TERRAIN_TYPES = {
    '0': 'city',
    '1': 'suburban',
    '2': 'country',
    '3': 'water',
    'city': 'city',
    'suburban': 'suburban',
    'country': 'country',
    'water': 'water'
}


if all_required_inputs(ghenv.Component):
    # set default values
    _height_ = 1 if _height_ is None else _height_
    _terrain_ = 'city' if _terrain_ is None else TERRAIN_TYPES[_terrain_.lower()]
    _met_height_ = 10 if _met_height_ is None else _met_height_
    _met_terrain_ = 'country' if _met_terrain_ is None \
        else TERRAIN_TYPES[_met_terrain_.lower()]
    log_law_ = False if log_law_ is None else log_law_

    # create the wind profile object and extract the air speeds
    profile = WindProfile(_terrain_, _met_terrain_, _met_height_, log_law_)
    if isinstance(_met_wind_vel, BaseCollection):
        air_speed = profile.calculate_wind_data(_met_wind_vel, _height_)
    else:  # assume that it is a single number
        _met_wind_vel = float(_met_wind_vel)
        air_speed = profile.calculate_wind(_met_wind_vel, _height_)
