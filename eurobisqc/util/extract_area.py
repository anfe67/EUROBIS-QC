import xmltodict
from eurobisqc.util import misc


def find_area(xml_input):
    """ This may be not generic enough, must verify within the eml.xml specs
        if the geographical area is always in the same element structure then it should work
        :returns list of x bondaries, y bondaries [(east,west), (north,south)]
        :returns None if area not present or not found where expected
    """

    dict_input = xmltodict.parse(xml_input)
    north = south = east = west = 0

    geo_area_dict = None
    # Notice that we have a problem if we have a list of areas... ...to be adjusted.
    # If there are multiple areas, we have to decide how to proceed,
    if 'coverage' in dict_input['eml:eml']['dataset']:
        if 'geographicCoverage' in dict_input['eml:eml']['dataset']['coverage']:
            if isinstance(dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'], list):
                if 'boundingCoordinates' in dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'][0]:
                    geo_area_dict = \
                        dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'][0]['boundingCoordinates']
            else:
                geo_area_dict = \
                    dict_input['eml:eml']['dataset']['coverage']['geographicCoverage']['boundingCoordinates']

    # Is it well formed
    valid = True
    if geo_area_dict is not None:
        if misc.is_number(geo_area_dict['westBoundingCoordinate']):
            west = float(geo_area_dict['westBoundingCoordinate'])
        else:
            valid = False

        if valid and misc.is_number(geo_area_dict['eastBoundingCoordinate']):
            east = float(geo_area_dict['eastBoundingCoordinate'])
        else:
            valid = False

        if valid and misc.is_number(geo_area_dict['northBoundingCoordinate']):
            north = float(geo_area_dict['northBoundingCoordinate'])
        else:
            valid = False

        if valid and misc.is_number(geo_area_dict['southBoundingCoordinate']):
            south = float(geo_area_dict['southBoundingCoordinate'])
        else:
            valid = False

        if valid:
            # If the area is valid but it represents the whole globe, there is no point
            if east == 180 and west == -180 and south == -90 and north == 90:
                return None

            return {"east": east, "west": west, "north": north, "south": south}
        else:
            return None
