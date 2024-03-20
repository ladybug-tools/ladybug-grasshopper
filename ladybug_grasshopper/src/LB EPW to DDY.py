# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Produce a DDY file from the data contained within an EPW or STAT file.
_
For EPW files, this method will first check if there is any heating or cooling
design day information contained within the EPW itself. If None is found, the
heating and cooling design days will be derived from analysis of the annual
data within the EPW. This process of analyzing the annual TMY data is
less representative of the climate since only one year of data is used to
derive the DDY (instead of the usual multi-year analysis). However, if the
EPW is the best available representation of the climate for a given site, it
can often be preferable to using a DDY constructed with more years of data
but from further away. Information on the uncertainty introduced by using
only one year of data to create design days can be found in AHSRAE HOF 2013,
Chapter 14.14.
_
For STAT files, the DDY file will only be produced if the design day information
is found within the file. If no information on the relevant design days are
found, and error will be raised and the component will fail to run.
-

    Args:
        _weather_file: The path to an .epw file or .stat file on your system, from
            which a .ddy will be generated.
        _percentile_: A number between 0 and 50 for the percentile difference
            from the most extreme conditions within the EPW or STAT
            to be used for the design day. Typical values are 0.4
            and 1.0. (Default: 0.4).
        monthly_cool_: A boolean to note whether the resulting .ddy file should
            contain twelve cooling design days for each of the months of
            the year. This type of DDY file is useful when the peak cooling
            might not be driven by warm outdoor temperatures but instead by
            the highest-intensity solar condition, which may not conincide
            with the highest temperature. Monthly conditions will be for the
            2.0% hottest conditions in each month, which generally aligns with
            the annual 0.4% cooling design conditions.
        _folder_: An optional file path to a directory into which the DDY file
            will be written.  If None, the DDY file will be written to the
            ladybug default weather data folder and placed in a sub-folder
            called "ddy".
        _write: Set to "True" to write the .ddy file.

    Returns:
        ddy_file: A .ddy file path that has been written to your system.
"""

ghenv.Component.Name = 'LB EPW to DDY'
ghenv.Component.NickName = 'EPWtoDDY'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os

try:
    from ladybug.epw import EPW
    from ladybug.stat import STAT
    from ladybug.config import folders
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component) and _write:
    # set default values
    _percentile_ = 0.4 if _percentile_ is None else _percentile_
    _folder_ = os.path.join(folders.default_epw_folder, 'ddy') if _folder_ \
        is None else _folder_
    if _weather_file.lower().endswith('.epw'):
        f_name = os.path.basename(_weather_file.lower()).replace('.epw', '.ddy')
        epw_data = True
    elif _weather_file.lower().endswith('.stat'):
        f_name = os.path.basename(_weather_file.lower()).replace('.stat', '.ddy')
        epw_data = False
    else:
        raise ValueError('Failed to recognize the file type of "{}".\n'
                         'Must end in .epw or .stat.'.format(_weather_file))
    f_path = os.path.join(_folder_, f_name)

    # create the DDY file
    if epw_data:
        epw = EPW(_weather_file)
        ddy_file = epw.to_ddy_monthly_cooling(f_path, _percentile_, 2) \
            if monthly_cool_ else epw.to_ddy(f_path, _percentile_)
    else:
        stat = STAT(_weather_file)
        ddy_file = stat.to_ddy_monthly_cooling(f_path, _percentile_, 2) \
            if monthly_cool_ else stat.to_ddy(f_path, _percentile_)
