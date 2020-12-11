import datetime
import re

from pyxylookup.pyxylookup import lookup


def check_float(value, valid_range=None):
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


def do_xylookup(results):
    output = [None] * len(results)
    indices = []
    coordinates = []
    for i in range(len(results)):
        result = results[i]
        if "decimalLongitude" in result["annotations"] and "decimalLatitude" in result["annotations"]:
            indices.append(i)
            coordinates.append([result["annotations"]["decimalLongitude"], result["annotations"]["decimalLatitude"]])
    if len(coordinates) > 0:
        xy = lookup(coordinates, shoredistance=True, grids=True, areas=True)
        for i in range(len(indices)):
            output[indices[i]] = xy[i]
    return output


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


# Move to utils - misc
def parse_lsid(s):
    m = re.search("^urn:lsid:marinespecies.org:taxname:([0-9]+)$", s)
    if m:
        return m.group(1)
    else:
        return None
