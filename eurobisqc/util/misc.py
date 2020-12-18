import datetime
import re
from eurobisqc.util import qc_flags


def check_float(value, valid_range=None):
    """ From OBIS-QC, takes a value and determines if this is a valid representation of a float
        which lies within the given range
        :param value - The number
        :param valid_range - The range within the value must lie  """

    result = {"valid": None, "float": None, "in_range": None}
    if value is not None:
        try:
            value_float = float(value)
            if valid_range is not None:
                result["in_range"] = valid_range[0] <= value_float <= valid_range[1]
                if result["in_range"]:
                    result["float"] = value_float
                    result["valid"] = True
                else:
                    result["valid"] = False
            else:
                result["float"] = value_float
                result["valid"] = True
        except ValueError:
            result["valid"] = False
    return result


def is_number(s):
    """ Utility function """

    try:
        float(s)
        return True
    except ValueError:
        return False


def date_to_millis(d):
    """Convert a date to milliseconds."""

    return int((d - datetime.date(1970, 1, 1)).total_seconds() * 1000)


def parse_lsid(s):
    """ verify correctness of lsid - from obis-qc"""

    m = re.search("^urn:lsid:marinespecies.org:taxname:([0-9]+)$", s)
    if m:
        return m.group(1)
    else:
        return None


def string_to_dict(dyn_prop_string):
    """ Very simplistic helper function
        :param: s - String of keys:values
        can take the form of a JSON,
        can have : or = as key-value separator
        and _ , ; as pair separator
        returns a dictionary of key:values
        or {'conversion_fail':True} """

    if len(dyn_prop_string) > 0:
        dyn_prop_string = dyn_prop_string.strip()
        # dyn_prop_string = dyn_prop_string.lower()  # Is this really necessary?

        if '{' in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace('{', '')
        if '}' in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace('}', '')
        if '"' in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace('"', '')
        if "'" in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace("'", '')
        if '=' in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace('=', ':')
        if ';' in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace(';', ':')
        if ',' in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace(',', ':')
        if '_' in dyn_prop_string:
            dyn_prop_string = dyn_prop_string.replace('_', ':')

        string_list = dyn_prop_string.split(':')
        if len(string_list) > 0 and len(string_list) % 2 == 0:
            return {string_list[i].strip(): string_list[i + 1].strip() for i in range(0, len(string_list), 2)}
        else:
            return {'conversion_fail': True}
    else:
        return {'conversion_fail': True}


def do_xylookup(records):
    """ derived from equivalent in obis-qc - takes a list of records already QCd
        for LAT - LON presence and validity - QC field must
        be present """

    # FLAG: This is ok in pycharm not for nosetest
    from pyxylookup.pyxylookup import lookup
    # FLAG: Ths is ok for nosetest, not for running in pycharm
    # import pyxylookup # and then use pyxylookup.lookup
    output = [None] * len(records)
    indices = []
    coordinates = []
    for i in range(len(records)):
        record = records[i]
        # The record has been already checked for LAT LON validity, but verify anyway...
        if "decimalLongitude" in record and \
                "decimalLatitude" in record and \
                "QC" in record and \
                not ((record["QC"] & qc_flags.QCFlag.GEO_LAT_LON_INVALID.bitmask) |
                     (record["QC"] & qc_flags.QCFlag.GEO_LAT_LON_MISSING.bitmask)):
            indices.append(i)
            lon = check_float(record["decimalLongitude"])["float"]
            lat = check_float(record["decimalLatitude"])["float"]

            coordinates.append([lon, lat])

    if len(coordinates) > 0:
        xy = lookup(coordinates, shoredistance=True, grids=True, areas=True)
        for i in range(len(indices)):
            output[indices[i]] = xy[i]
    return output
