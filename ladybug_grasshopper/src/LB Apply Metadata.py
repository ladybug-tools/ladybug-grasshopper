# Ladybug: A Plugin for Environmental Analysis (GPL)
# This file is part of Ladybug.
#
# Copyright (c) 2026, Ladybug Tools.
# You should have received a copy of the GNU Affero General Public License
# along with Ladybug; If not, see <http://www.gnu.org/licenses/>.
#
# @license AGPL-3.0-or-later <https://spdx.org/licenses/AGPL-3.0-or-later>

"""
Set or override metadata for a Ladybug data collection.
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
            If provided, it will replace the current metadata.
            If not provided, the original metadata will be preserved.
            Note: 
                * Keys 'Zone', 'Surface', and 'System' will have their values 
                  converted to uppercase. These keys are used for data matching 
                  and will not appear in chart titles. 
                * Key 'type' will modify the legend name in LB Monthly Chart,
                  which is helpful when comparing multiple data collections 
                  of the same type.

    Returns:
        data: The data collection with the metadata applied to it.
"""

ghenv.Component.Name = 'LB Apply Metadata'
ghenv.Component.NickName = 'ApplyMeta'
ghenv.Component.Message = '1.10.0'
ghenv.Component.Category = 'Ladybug'
ghenv.Component.SubCategory = '1 :: Analyze Data'
ghenv.Component.AdditionalHelpFromDocStrings = '2'

try:
    from ladybug.datacollection import BaseCollection
except ImportError as e:
    raise ImportError('\nFailed to import ladybug:\n\t{}'.format(e))

try:
    from ladybug_rhino.grasshopper import all_required_inputs
except ImportError as e:
    raise ImportError('\nFailed to import ladybug_rhino:\n\t{}'.format(e))


# Clear outputs at the beginning to ensure fresh data
data = None


def parse_metadata_single(metadata_input):
    """Parse a single metadata input into a dictionary."""
    if metadata_input is None:
        return {}
    
    # If already a dictionary, return as is
    if isinstance(metadata_input, dict):
        return metadata_input.copy()
    
    # If a string, try to parse as JSON or key:value pairs
    if isinstance(metadata_input, str):
        try:
            import json
            return json.loads(metadata_input)
        except ValueError:
            # Try parsing as key:value,key:value format
            result = {}
            pairs = metadata_input.split(',')
            for pair in pairs:
                if ':' in pair:
                    key, value = pair.split(':', 1)
                    result[key.strip()] = value.strip()
            return result
    
    return {}


def parse_metadata(metadata_input):
    """Parse metadata input, handling both single and multiple entries."""
    if metadata_input is None:
        return None
    
    # Check if it's a DataTree with multiple branches
    if hasattr(metadata_input, 'BranchCount'):
        # Merge all branches into a single dictionary
        merged_metadata = {}
        for branch in metadata_input.Branches:
            for item in branch:
                item_dict = parse_metadata_single(item)
                merged_metadata.update(item_dict)
        return merged_metadata if merged_metadata else None
    
    # Check if it's a list/tuple of metadata
    if isinstance(metadata_input, (list, tuple)):
        merged_metadata = {}
        for item in metadata_input:
            item_dict = parse_metadata_single(item)
            merged_metadata.update(item_dict)
        return merged_metadata if merged_metadata else None
    
    # Single metadata entry
    return parse_metadata_single(metadata_input)


def process_special_keys(metadata):
    """Process special keys: convert to uppercase and add display keys."""
    # Keys that need uppercase conversion
    uppercase_keys = ('Zone', 'Surface', 'System')
    
    # Convert to uppercase
    for key in uppercase_keys:
        if key in metadata:
            value = metadata[key]
            if isinstance(value, str):
                metadata[key] = value.upper()
            elif isinstance(value, list):
                metadata[key] = [v.upper() if isinstance(v, str) else v for v in value]
    
    # Add display keys for excluded keys so they appear in charts
    # Zone -> Room (for display)
    if 'Zone' in metadata and 'Room' not in metadata:
        metadata['Room'] = metadata['Zone']
    
    # Surface -> Face (for display)
    if 'Surface' in metadata and 'Face' not in metadata:
        metadata['Face'] = metadata['Surface']
    
    return metadata


def process_data_collection(data_collection, new_metadata):
    """Process a single data collection and apply metadata."""
    # Create a duplicate to avoid mutating the original
    new_collection = data_collection.duplicate()
    
    # Only apply metadata if provided
    if new_metadata is not None and new_metadata:
        # Process special keys
        new_metadata = process_special_keys(new_metadata)
        # Set metadata
        new_collection.header.metadata = new_metadata
    
    return new_collection


if all_required_inputs(ghenv.Component):
    # Parse metadata input (handles both single and multiple entries)
    meta_dict = parse_metadata(_metadata_) if '_metadata_' in globals() else None
    
    # Process single data collection or list of collections
    if isinstance(_data, BaseCollection):
        # Single data collection
        data = process_data_collection(_data, meta_dict)
    else:
        # List of data collections
        try:
            data = [process_data_collection(d, meta_dict) for d in _data]
        except TypeError:
            raise TypeError('_data must be a Data Collection or a list of Data '
                          'Collections. Got {}.'.format(type(_data)))