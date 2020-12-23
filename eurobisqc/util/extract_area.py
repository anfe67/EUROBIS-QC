import xmltodict
from eurobisqc.util import misc


# TODO: FURTHER TESTS

def find_areas(xml_input):
    """ This may be not generic enough, must verify within the eml.xml specs
        if the geographical area is always in the same element structure then it should work
        :returns list of dicts - with bondaries, like in [{"east": east, "west": west, "north": north, "south": south}],
        they represent all the areas that we managed to extract from the EML
        :returns None if area not present or not found where expected
        If multiple areas are in the XML, then we consider the area that comprises all areas
        listed, which is defined by the westmost, eastmost, southmost and northmost coordinates
    """

    dict_input = xmltodict.parse(xml_input)

    west_most = -180
    east_most = 180
    south_most = -90
    north_most = 90

    xml_areas = []
    geo_areas = []

    # Notice that we have a problem if we have a list of areas... ...to be adjusted.
    # If there are multiple areas, we have to decide how to proceed,
    if 'coverage' in dict_input['eml:eml']['dataset']:
        if 'geographicCoverage' in dict_input['eml:eml']['dataset']['coverage']:
            if isinstance(dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'], list):
                # To test...
                if 'boundingCoordinates' in dict_input['eml:eml']['dataset']['coverage']['geographicCoverage'][0]:
                    for element in dict_input['eml:eml']['dataset']['coverage']['geographicCoverage']:
                        if 'boundingCoordinates' in element:
                            xml_areas.append(element['boundingCoordinates'])
            else:
                xml_areas.append(
                    dict_input['eml:eml']['dataset']['coverage']['geographicCoverage']['boundingCoordinates'])
                # geo_area_dict = \
                # dict_input['eml:eml']['dataset']['coverage']['geographicCoverage']['boundingCoordinates']

    # Is it well formed
    valid = True

    # We have a list, propose a
    if len(xml_areas):
        for xml_area in xml_areas:

            south = 0
            north = 0
            east = 0
            west = 0  # Make sure this is the scope

            if misc.is_number(xml_area['westBoundingCoordinate']):
                west = float(xml_area['westBoundingCoordinate'])

            if misc.is_number(xml_area['eastBoundingCoordinate']):
                east = float(xml_area['eastBoundingCoordinate'])

            if misc.is_number(xml_area['northBoundingCoordinate']):
                north = float(xml_area['northBoundingCoordinate'])

            if misc.is_number(xml_area['southBoundingCoordinate']):
                south = float(xml_area['southBoundingCoordinate'])

            if south <= north and west <= east:
                if west_most <= west <= east_most and \
                        west_most <= east <= east_most and \
                        south_most <= south <= north_most and \
                        south_most <= north <= north_most and \
                        not (south == south_most and north == north_most and west == west_most and east == east_most):
                    geo_areas.append({"east": east, "west": west, "north": north, "south": south})

        if not len(geo_areas):
            valid = False  # No valid areas found

    if valid:
        # If the area is valid but it represents the whole globe, this verification is already covered
        for area in geo_areas:

            if area["east"] == 180 and area["west"] == -180 and area["south"] == -90 and area["north"] == 90:
                geo_areas.remove(area)

        if len(geo_areas):
            return geo_areas
        else:
            return None

    else:
        # Could not figure out the area
        return None
