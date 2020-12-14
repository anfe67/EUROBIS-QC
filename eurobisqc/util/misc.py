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

def string_to_dict(s):
    """ Very simplistic helper function
        :param: s - String of keys:values
        can take the form of a JSON,
        can have : or = as key-value separator
        and _ , ; as pair separator
        returns a dictionary of key:values
        or {'conversion_fail':True} """

    s = s.strip()
    if '{' in s:
        s = s.replace('{', '')
    if '}' in s:
        s = s.replace('}', '')
    if '"' in s:
        s = s.replace('"', '')
    if '=' in s:
        s=s.replace('=',':')
    if ';' in s:
        s=s.replace(';', ':')
    if ',' in s:
        s=s.replace(',', ':')
    if '_' in s:
        s=s.replace('_', ':')

    s_l = s.split(':')
    if len(s_l) % 2 == 0:
        return {s_l[i]: s_l[i + 1] for i in range(0, len(s_l), 2)}
    else:
        return {'conversion_fail':True}