import datetime

isoDateTimeFormat = "%Y-%m-%d %H:%M:%S.%f"


def datetime_to_iso_string(dt) :
    return dt.strftime(isoDateTimeFormat) if dt else None


def iso_string_to_date_time(dtStr):
    return datetime.datetime.strptime(dtStr, isoDateTimeFormat) if dtStr else None
