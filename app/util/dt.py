import pytz
from datetime import datetime, date, timedelta
from dateutil import parser


def parse_datetime_str(datetime_str):
    try:
        return datetime.strptime(datetime_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return None


def get_utc_difference():
    return 3


def get_timezone_from_utc_offset(offset):
    utc_offset = timedelta(hours=offset)
    now = datetime.utcnow()
    tzone = None
    for tz in map(pytz.timezone, pytz.all_timezones_set):
        if now.astimezone(tz).utcoffset() == utc_offset:
            tzone = tz.zone
            break
    return tzone


def week_ago():
    return date.today() - timedelta(days=7)


def week_passed(event_date):
    return (datetime.today() - event_date).days >= 7


def day_passed(event_date):
    return (date.today() - event_date).days > 0


def get_utc_timezone(timezone):
    return timezone + 3


def get_cur_time(timezone):
    return datetime.utcnow() + timedelta(hours=timezone)


def get_datetime_in_timezone(utc_datetime, timezone):
    return utc_datetime + timedelta(hours=timezone)


def is_new_week():
    return date.today().weekday() == 0


def is_end_of_week():
    return date.today().weekday() == 6


def is_new_month():
    return date.today().day == 1


def get_datetime_from_iso8601(time_str):
    time_split = time_str.split('.')[0]
    return datetime.strptime(time_split, '%Y-%m-%dT%H:%M:%S')


def get_hour_and_minute_from_time_hh_mm(time):
    time_split = time.split(':')
    return int(time_split[0]), int(time_split[1])


def get_dt_from_hh_mm(time, cur_time):
    hour, minute = get_hour_and_minute_from_time_hh_mm(time)
    return cur_time.replace(hour=hour, minute=minute, second=0, microsecond=0)


def datetime_to_str(dt):
    return dt.replace(microsecond=0).isoformat()


def timedelta_to_dict(dt, with_seconds=False):
    mm, ss = divmod(dt.seconds, 60)
    hh, mm = divmod(mm, 60)

    res_dict = {'days': dt.days, 'hours': hh, 'minutes': mm}

    if with_seconds:
        res_dict['seconds'] = ss

    return res_dict


def validate_iso8601(str_val):
    try:
        parser.parse(str_val)
        return True
    except:
        pass
    return False


def compare_hh_mm(time1, time2):
    return datetime.strptime(time1, '%H:%M') >= datetime.strptime(time2, '%H:%M')


def convert_to_timedelta(dt_dict):
    try:
        t = timedelta(**dt_dict)
        return t
    except Exception:
        return None
