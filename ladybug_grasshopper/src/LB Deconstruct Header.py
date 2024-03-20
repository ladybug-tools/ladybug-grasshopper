# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2024, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
# 
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Deconstruct a Ladybug Header into its components.
-

    Args:
        _header: The header of the DataCollection (containing metadata).

    Returns:
        data_type: Type of data (e.g. Temperature) (Default: unknown).
        unit: Units of the data_type (e.g. C) (Default: unknown)
        a_period: A Ladybug AnalysisPeriod object.
        metadata: Optional metadata associated with the Header.
"""

ghenv.Component.Name = "LB Deconstruct Header"
ghenv.Component.NickName = 'XHeader'
ghenv.Component.Message = '1.8.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.header import Header
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


if all_required_inputs(ghenv.Component):
    assert isinstance(_header, Header), 'Expected Ladybug Header. ' \
        'Got {}.'.format(type(_header))
    data_type = _header.data_type
    unit = _header.unit
    a_period = _header.analysis_period
    metadata = [': '.join([str(key), str(val)]) for key, val in _header.metadata.items()]