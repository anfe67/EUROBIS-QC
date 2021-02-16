import datetime
import re
from eurobisqc import qc_flags


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
    except (ValueError, TypeError):
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
    """ Very simplistic helper function for dynamic properties
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


# Modify to take into account QC masks and not error masks
def do_xylookup(records):
    """ derived from equivalent in obis-qc - takes a list of records already QCd
        for LAT - LON presence and validity - QC field must
        be present
        :param - records IMPORTANT - with VALID LAT, LON
        :returns - a list of result records as retrieved from pyxylookup for each point """

    import pyxylookup as pxy  # and then use pyxylookup.lookup

    output = [None] * len(records)
    indices = []
    coordinates = []
    for i in range(len(records)):
        record = records[i]
        # The record has been already checked LAT LON validity, but verify anyway...
        if "decimalLongitude" in record and \
                "decimalLatitude" in record and \
                "qc" in record and \
                record["qc"] & qc_flags.QCFlag.GEO_LAT_LON_VALID.bitmask and \
                record["qc"] & qc_flags.QCFlag.GEO_LAT_LON_PRESENT.bitmask:
            indices.append(i)
            lon = check_float(record["decimalLongitude"])["float"]
            lat = check_float(record["decimalLatitude"])["float"]

            coordinates.append([lon, lat])

    if len(coordinates) > 0:
        xy = pxy.lookup(coordinates, shoredistance=True, grids=True, areas=True)
        for i in range(len(indices)):
            output[indices[i]] = xy[i]
    return output


def split_list(a, n):
    """ Splits a list in n chunks """

    k, m = divmod(len(a), n)
    result = list(a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n))
    return result

def split_list_optimized(a, n, numbers):
    """ Splits a list in n chunks """
    """ n = cpus """
    """ a (ids | names) """

    sum = 0
    k, m = divmod(len(a), n)
    for i in range(0, len(numbers)):
        sum = sum + numbers[i]
    result = []
    pool = []
    averagesize = sum / n
    i_record_count = 0
    for teller in range(n):
        sum_records_pool = 0
        while sum_records_pool < averagesize and i_record_count < len(numbers):
             pool.append(a[i_record_count])
             sum_records_pool += numbers[i_record_count]
             i_record_count += 1
        result.append(pool)
        pool = []
    return result


def split_in_chunks(a_list, a_size):
    return [a_list[offs:offs + a_size] for offs in range(0, len(a_list), a_size)]


def is_clean_for_sql(field):
    """ Avoid to manipulate strings that may make a sql update query fail """
    if "'" in field or '"' in field:
        return False
    else:
        return True

# Use existing SQL function instead as per answer by Bart
# def build_event_date(end_year,
#                      end_month,
#                      end_day,
#                      end_time,
#                      start_year,
#                      start_month,
#                      start_day,
#                      start_time,
#                      time_zone,
#                      year_collected,
#                      month_collected,
#                      day_collected,
#                      time_of_day,
#                      eml):
#     """ Attempts to build a parseable ISO format date - to keep consistency with DwCA processing
#         The values are the fields of the database, they are integer for the date components,
#         float for the time and string for the timezone. The eml is the last resort """
#
#     from math import modf, trunc
#
#     event_date_string_start = None
#     event_date_string_end = None
#     event_date_string = None
#
#     start_time_hours = None,
#     start_time_minutes = None
#     end_time_hours = None
#     end_time_minutes = None
#     time_hours = None
#     time_minutes = None
#
#     if start_time is not None:
#         start_time_minutes, start_time_hours = modf(start_time)
#         start_time_minutes = trunc(start_time_minutes * 100 / 60)
#
#     if end_time is not None:
#         end_time_minutes, end_time_hours = modf(end_time)
#         end_time_minutes = trunc(end_time_minutes * 100 / 60)
#
#     if time_of_day is not None:
#         time_minutes, time_hours = modf(time_of_day)
#         time_minutes = trunc(time_minutes * 100 / 60)
#
#     # We need at least the year - Start Date
#     if start_year is not None:
#         event_date_string_start = str(start_year)
#
#     if event_date_string_start is not None:
#         if start_month is not None:
#             event_date_string_start += f"-{str(start_month).zfill(2)}"
#             if start_day is not None:
#                 event_date_string_start += f"-{str(start_day).zfill(2)}"
#                 if start_time is not None:
#                     event_date_string_start += f"T{str(start_time_hours).zfill(2)}:{str(start_time_minutes).zfill(2)}"
#                     if time_zone is not None:
#                         event_date_string_start += f":{time_zone}"
#
#     # End Date
#     if end_year is not None:
#         event_date_string_end = str(end_year)
#     if event_date_string_end is not None:
#         if end_month is not None:
#             event_date_string_end += f"-{str(end_month).zfill(2)}"
#             if end_day is not None:
#                 event_date_string_end += f"-{str(end_day).zfill(2)}"
#                 if end_time is not None:
#                     event_date_string_end += f"T{str(end_time_hours).zfill(2)}:{str(end_time_minutes).zfill(2)}"
#                     if time_zone is not None:
#                         event_date_string_end += f":{time_zone}"
#
#     if event_date_string_start is not None:
#         event_date_string += event_date_string_start
#
#     if event_date_string_end is not None:
#         if event_date_string is not None:
#             event_date_string += f"/{event_date_string_start}"
#         else:
#             event_date_string = event_date_string_end
#
#     # looking at the collection date / time
#     if event_date_string is None:
#         if year_collected is not None:
#             event_date_string = str(year_collected)
#             if month_collected is not None:
#                 event_date_string += f"-{str(month_collected).zfill(2)}"
#                 if day_collected is not None:
#                     event_date_string += f"-{str(day_collected).zfill(2)}"
#                     if time_of_day is not None:
#                         # split the time as above
#                         event_date_string += f"T{str(time_hours).zfill(2)}:{str(time_minutes).zfill(2)}"
#                         if time_zone is not None:
#                             event_date_string_end += f":{time_zone}"
#
#     # Still no luck? Attempt extraction from EML
#     # if event_date_string is None:
#     #     event_date_string = extract_dates.find_dates(eml)
#
#     # And that's it for the eventDate, no more looking
#     return event_date_string
