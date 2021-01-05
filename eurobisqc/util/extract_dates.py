import xmltodict


def find_dates(xml_input):
    """ This may be not generic enough, must verify within the eml.xml specs
        It is used as a last resort if the dataset records do not contain time inf
        :returns A string, representing an interval or None
    """

    dict_input = xmltodict.parse(xml_input)

    res = None

    dates = []

    if 'coverage' in dict_input['eml:eml']['dataset']:
        if 'temporalCoverage' in dict_input['eml:eml']['dataset']['coverage']:
            if isinstance(dict_input['eml:eml']['dataset']['coverage']['temporalCoverage'], dict):
                # To test...
                if 'rangeOfDates' in dict_input['eml:eml']['dataset']['coverage']['temporalCoverage']:
                    element = dict_input['eml:eml']['dataset']['coverage']['temporalCoverage']['rangeOfDates']
                    dates.append(element['beginDate']['calendarDate'])
                    dates.append(element['endDate']['calendarDate'])

    if len(dates):
        start_date = dates[0]
        end_date = dates[1]
        res = f"{start_date}/{end_date}"

    return res
