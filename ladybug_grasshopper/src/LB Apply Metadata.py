# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
#
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Apply metadata to a Ladybug data collection.
-

    Args:
        _data: A Ladybug data collection object or a list of data collections.
        _metadata_: Optional metadata to be associated with the Header. The input
            should be a list of text strings with a property name and value for
            the property separated by a colon. For example:
            _
            .    source: TMY
            .    city: New York
            .    country: USA
            _
            By default, the connected metadata will be merged with the existing
            metadata on the data collection. If the same key exists in both
            places, the new value will overwrite the old one.
            Note:
                * Keys 'Zone', 'Surface', and 'System' will have their values
                  converted to uppercase in order to align with downstream object-
                  matching workflows.
                * Key 'type' will modify the legend name in LB Monthly Chart,
                  which is helpful when comparing multiple data collections
                  of the same type.
        override_: Boolean to note whether the existing metadata should be
            overwritten instead of merged. If True, only the connected metadata
            will remain on the output data collection. If no _metadata_ is
            connected, this input can be used to clear all existing metadata.

    Returns:
        data: The data collection with the metadata applied to it.
"""

ghenv.Component.Name = 'LB Apply Metadata'
ghenv.Component.NickName = 'ApplyMeta'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '0'

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


def parse_metadata_single(metadata_input):
    """Parse a single metadata input into a dictionary."""
    if metadata_input is None:
        return {}

    if isinstance(metadata_input, dict):
        return metadata_input.copy()

    if isinstance(metadata_input, str):
        try:
            import json
            parsed = json.loads(metadata_input)
            return parsed if isinstance(parsed, dict) else {}
        except ValueError:
            result = {}
            pairs = metadata_input.split(',')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    result[key.strip()] = value.strip()
            return result

    return {}


def parse_metadata(metadata_input):
    """Parse metadata input into a single dictionary."""
    if metadata_input is None:
        return None

    if isinstance(metadata_input, (list, tuple)):
        merged_metadata = {}
        for item in metadata_input:
            item_dict = parse_metadata_single(item)
            merged_metadata.update(item_dict)
        return merged_metadata if merged_metadata else None

    return parse_metadata_single(metadata_input)


def process_special_keys(metadata):
    """Uppercase keys used for downstream object matching."""
    metadata = metadata.copy()
    uppercase_keys = ('Zone', 'Surface', 'System')

    for key in uppercase_keys:
        if key in metadata:
            value = metadata[key]
            if isinstance(value, str):
                metadata[key] = value.upper()
            elif isinstance(value, list):
                metadata[key] = [v.upper() if isinstance(v, str) else v for v in value]

    return metadata


def process_data_collection(data_collection, new_metadata, override):
    """Process a single data collection and apply metadata."""
    new_collection = data_collection.duplicate()

    if new_metadata is not None:
        new_metadata = process_special_keys(new_metadata)
        if override:
            new_collection.header.metadata = new_metadata
        else:
            metadata = new_collection.header.metadata.copy()
            metadata.update(new_metadata)
            new_collection.header.metadata = metadata
    elif override:
        new_collection.header.metadata = {}

    return new_collection


if all_required_inputs(ghenv.Component):
    meta_dict = parse_metadata(_metadata_)
    override_ = False if override_ is None else override_

    if isinstance(_data, BaseCollection):
        data = process_data_collection(_data, meta_dict, override_)
    else:
        try:
            data = [process_data_collection(d, meta_dict, override_) for d in _data]
        except TypeError:
            raise TypeError('_data must be a Data Collection or a list of Data '
                          'Collections. Got {}.'.format(type(_data)))