import xmltodict
from eurobisqc.util import misc


def find_area(xml_input):
    """ This may be not generic enough, must verify within the eml.xml specs
        if the geographical area is always in the same element structure then it should work
        :returns list of x bondaries, y bondaries [(east,west), (north,south)]
        :returns None if area not present or not found where expected
        If multiple areas are in the XML, then we consider the area that comprises all areas
        listed, which is defined by the westmost, eastmost, southmost and northmost coordinates
    """

    dict_input = xmltodict.parse(xml_input)

    west = 180
    east = -180
    south = 90
    north = -90

    geo_area_dict = None
    geo_areas = []
    # Notice that we have a problem if we have a list of areas... ...to be adjusted.
    # If there are multiple areas, we have to decide how to proceed,
    if 'coverage' in dict_input['eml:eml']['dataset']:
        if 'geographicCoverage' in dict_input['eml:eml']['dataset']['coverage']:
            if isinstance(dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'], list):
                # This shall go
                if 'boundingCoordinates' in dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'][0]:
                    geo_area_dict = \
                        dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'][0]['boundingCoordinates']

                for element in dict_input['eml:eml']['dataset']['coverage']['geographicCoverage']:
                    if 'boundingCoordinates' in element:
                        geo_areas.append(element['boundingCoordinates'])
            else:
                geo_area_dict = \
                    dict_input['eml:eml']['dataset']['coverage']['geographicCoverage']['boundingCoordinates']

    # Is it well formed
    valid = True

    # We have a list
    if len(geo_areas):
        for area in geo_areas:
            if misc.is_number(area['westBoundingCoordinate']):
                west = min(float(area['westBoundingCoordinate']), west)

            if misc.is_number(area['eastBoundingCoordinate']):
                east = max(float(area['eastBoundingCoordinate']), east)

            if misc.is_number(area['northBoundingCoordinate']):
                north = max(float(area['northBoundingCoordinate']), north)

            if misc.is_number(area['southBoundingCoordinate']):
                south = min(float(area['southBoundingCoordinate']), south)

            if not south <= north or not west <= east:
                valid = False

    # We have a single area
    elif geo_area_dict is not None:
        if misc.is_number(geo_area_dict['westBoundingCoordinate']):
            west = float(geo_area_dict['westBoundingCoordinate'])

        if valid and misc.is_number(geo_area_dict['eastBoundingCoordinate']):
            east = float(geo_area_dict['eastBoundingCoordinate'])

        if valid and misc.is_number(geo_area_dict['northBoundingCoordinate']):
            north = float(geo_area_dict['northBoundingCoordinate'])

        if valid and misc.is_number(geo_area_dict['southBoundingCoordinate']):
            south = float(geo_area_dict['southBoundingCoordinate'])

        if not south <= north or not west <= east:
            valid = False

    if valid:
        # If the area is valid but it represents the whole globe, this verification is already covered
        if east == 180 and west == -180 and south == -90 and north == 90:
            return None

        return {"east": east, "west": west, "north": north, "south": south}
    else:
        # Could not figure out the area
        return None
