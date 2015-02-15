from icalendar.prop import vRecur

__author__ = 'Michal'


def build_rrule(count=None, interval=None, bysecond=None, byminute=None, byhour=None, byweekno=None,
                bymonthday=None, byyearday=None, bymonth=None, until=None, bysetpos=None, wkst=None, byday=None, freq=None):
    """
    Builds rrule dictionary for vRecur class
    :param count: int
    :param interval: int
    :param bysecond: int
    :param byminute: int
    :param byhour: int
    :param byweekno: int
    :param bymonthday: int
    :param byyearday: int
    :param bymonth: int
    :param until: datetime
    :param bysetpos: int
    :param wkst: str, two-letter weekday
    :param byday: weekday
    :param freq: str, frequency name ('WEEK', 'MONTH', etc)
    :return: dict
    """
    result = {}

    if count is not None:
        result['COUNT'] = count

    if interval is not None:
        result['INTERVAL'] = interval

    if bysecond is not None:
        result['BYSECOND'] = bysecond

    if byminute is not None:
        result['BYMINUTE'] = byminute

    if byhour is not None:
        result['BYHOUR'] = byhour

    if byweekno is not None:
        result['BYWEEKNO'] = byweekno

    if bymonthday is not None:
        result['BYMONTHDAY'] = bymonthday

    if byyearday is not None:
        result['BYYEARDAY'] = byyearday

    if bymonth is not None:
        result['BYMONTH'] = bymonth

    if until is not None:
        result['UNTIL'] = until

    if bysetpos is not None:
        result['BYSETPOS'] = bysetpos

    if wkst is not None:
        result['WKST'] = wkst

    if byday is not None:
        result['BYDAY'] = byday

    if freq is not None:
        if freq not in vRecur.frequencies:
            raise ValueError('Frequency value should be one of: %s' % vRecur.frequencies)
        result['FREQ'] = freq

    return result