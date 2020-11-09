# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2020, Ladybug Tools.
# You should have received a copy of the GNU General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>

"""
Produce a DDY file with a heating and a cooling design day from an EPW.
_
This method will first check if there is any heating or cooling design day information
contained within the EPW itself. If None is found, the heating and cooling design
days will be derived from analysis of the annual data within the EPW, which is
usually less representative of the climate since only one year of data is used
to derive the DDY (instead of the usual multi-year analysis that is performed for
DDYs distributed with EPWs).
_
Information on the uncertainty introduced by using only one year of data to create
design days can be found in AHSRAE HOF 2013, Chapter 14.14.
-

    Args:
        _epw_file: An .epw file path on your system, from which a .ddy will
            be generated.
        _percentile_: A number between 0 and 50 for the percentile difference
            from the most extreme conditions within the EPW to be used for
            the design day. Typical values are 0.4 and 1.0. (Default: 0.4).
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
ghenv.Component.Message = '1.1.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '0 :: Import'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

import os

try:
    from ladybug.epw import EPW
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
    f_name = os.path.basename(_epw_file).replace('.epw', '.ddy')
    f_path = os.path.join(_folder_, f_name)

    # create the DDY file
    epw = EPW(_epw_file)
    ddy_file = epw.to_ddy(f_path, _percentile_)
