#:coding=utf-8:
from icalendar.prop import vRecur

import pytz
import icalendar
from datetime import datetime

from django.test import TestCase
from django.test.client import RequestFactory
from django_ical.ical_utils import build_rrule

from django_ical.feedgenerator import ICal20Feed
from django_ical.views import ICalFeed


class TestICalFeed(ICalFeed):
    feed_type = ICal20Feed
    title = "Test Feed"
    description = "Test ICal Feed"
    items = []


class TestItemsFeed(ICalFeed):
    feed_type = ICal20Feed
    title = "Test Feed"
    description = "Test ICal Feed"

    def items(self):
        return [{
            'title': 'Title1',
            'description': 'Description1',
            'link': '/event/1',
            'start': datetime(2012, 5, 1, 18, 00),
            'end': datetime(2012, 5, 1, 20, 00),
            'geolocation': (37.386013, -122.082932),
            'rrule': build_rrule(freq='WEEKLY', until=datetime.now(), wkst='SU', byday='MO,TU'),
            'organizer': 'john.doe@example.com',
        }, {
            'title': 'Title2',
            'description': 'Description2',
            'link': '/event/2',
            'start': datetime(2012, 5, 6, 18, 00),
            'end': datetime(2012, 5, 6, 20, 00),
            'geolocation': (37.386013, -122.082932),
            'rrule': build_rrule(freq='WEEKLY', until=datetime.now(), wkst='MO', byday='MO,TU,WE'),
            'organizer': {
                'cn': 'John Doe',
                'email': 'john.doe@example.com',
                'role': 'CHAIR'
            },
        }]

    def item_title(self, obj):
        return obj['title']

    def item_description(self, obj):
        return obj['description']

    def item_start_datetime(self, obj):
        return obj['start']

    def item_end_datetime(self, obj):
        return obj['end']

    def item_link(self, obj):
        return obj['link']

    def item_geolocation(self, obj):
        return obj.get('geolocation', None)

    def item_organizer(self, obj):
        organizer_dic = obj.get('organizer', None)
        if organizer_dic:
            if isinstance(organizer_dic, dict):
                organizer = icalendar.vCalAddress('MAILTO:%s' % organizer_dic['email'])
                for key, val in organizer_dic.iteritems():
                    if key is not 'email':
                        organizer.params[key] = icalendar.vText(val)
            else:
                organizer = icalendar.vCalAddress('MAILTO:%s' % organizer_dic)
            return organizer


class TestFilenameFeed(ICalFeed):
    feed_type = ICal20Feed
    title = "Test Filename Feed"
    description = "Test ICal Feed"

    def get_object(self, request):
        return {
            'id': 123,
        }

    def items(self, obj):
        return [obj]

    def file_name(self, obj):
        return "%s.ics" % obj['id']

    def item_link(self, item):
        return ''  # Required by the syndication framework


class ICal20FeedTest(TestCase):
    def test_basic(self):
        request = RequestFactory().get("/test/ical")
        view = TestICalFeed()

        response = view(request)
        calendar = icalendar.Calendar.from_ical(response.content)
        self.assertEquals(calendar['X-WR-CALNAME'], "Test Feed")
        self.assertEquals(calendar['X-WR-CALDESC'], "Test ICal Feed")

    def test_items(self):
        request = RequestFactory().get("/test/ical")
        view = TestItemsFeed()

        response = view(request)

        calendar = icalendar.Calendar.from_ical(response.content)
        self.assertEquals(len(calendar.subcomponents), 2)

        self.assertEquals(calendar.subcomponents[0]['SUMMARY'], 'Title1')
        self.assertEquals(calendar.subcomponents[0]['DESCRIPTION'], 'Description1')
        self.assertTrue(calendar.subcomponents[0]['URL'].endswith('/event/1'))
        self.assertEquals(calendar.subcomponents[0]['DTSTART'].to_ical(), '20120501T180000')
        self.assertEquals(calendar.subcomponents[0]['DTEND'].to_ical(), '20120501T200000')
        self.assertEquals(calendar.subcomponents[0]['GEO'].to_ical(), "37.386013;-122.082932")
        self.assertEquals(calendar.subcomponents[0]['ORGANIZER'].to_ical(),
                          "MAILTO:john.doe@example.com")

        self.assertEquals(calendar.subcomponents[1]['SUMMARY'], 'Title2')
        self.assertEquals(calendar.subcomponents[1]['DESCRIPTION'], 'Description2')
        self.assertTrue(calendar.subcomponents[1]['URL'].endswith('/event/2'))
        self.assertEquals(calendar.subcomponents[1]['DTSTART'].to_ical(), '20120506T180000')
        self.assertEquals(calendar.subcomponents[1]['DTEND'].to_ical(), '20120506T200000')
        self.assertEquals(calendar.subcomponents[1]['GEO'].to_ical(), "37.386013;-122.082932")
        self.assertEquals(calendar.subcomponents[0]['ORGANIZER'].to_ical(),
                          "MAILTO:john.doe@example.com")

    def test_wr_timezone(self):
        """
        Test for the x-wr-timezone property.
        """
        class TestTimezoneFeed(TestICalFeed):
            timezone = "Asia/Tokyo"

        request = RequestFactory().get("/test/ical")
        view = TestTimezoneFeed()

        response = view(request)
        calendar = icalendar.Calendar.from_ical(response.content)
        self.assertEquals(calendar['X-WR-TIMEZONE'], "Asia/Tokyo")

    def test_timezone(self):
        tokyo = pytz.timezone('Asia/Tokyo')
        us_eastern = pytz.timezone('US/Eastern')

        class TestTimezoneFeed(TestItemsFeed):
            def items(self):
                return [{
                    'title': 'Title1',
                    'description': 'Description1',
                    'link': '/event/1',
                    'start': datetime(2012, 5, 1, 18, 00, tzinfo=tokyo),
                    'end': datetime(2012, 5, 1, 20, 00, tzinfo=tokyo),

                }, {
                    'title': 'Title2',
                    'description': 'Description2',
                    'link': '/event/2',
                    'start': datetime(2012, 5, 6, 18, 00, tzinfo=us_eastern),
                    'end': datetime(2012, 5, 6, 20, 00, tzinfo=us_eastern),
                }]

        request = RequestFactory().get("/test/ical")
        view = TestTimezoneFeed()

        response = view(request)
        calendar = icalendar.Calendar.from_ical(response.content)
        self.assertEquals(len(calendar.subcomponents), 2)

        self.assertEquals(calendar.subcomponents[0]['DTSTART'].to_ical(), '20120501T180000')
        self.assertEquals(calendar.subcomponents[0]['DTSTART'].params['TZID'], 'Asia/Tokyo')

        self.assertEquals(calendar.subcomponents[0]['DTEND'].to_ical(), '20120501T200000')
        self.assertEquals(calendar.subcomponents[0]['DTEND'].params['TZID'], 'Asia/Tokyo')

        self.assertEquals(calendar.subcomponents[1]['DTSTART'].to_ical(), '20120506T180000')
        self.assertEquals(calendar.subcomponents[1]['DTSTART'].params['TZID'], 'US/Eastern')

        self.assertEquals(calendar.subcomponents[1]['DTEND'].to_ical(), '20120506T200000')
        self.assertEquals(calendar.subcomponents[1]['DTEND'].params['TZID'], 'US/Eastern')

    def test_file_name(self):
        request = RequestFactory().get("/test/ical")
        view = TestFilenameFeed()

        response = view(request)

        self.assertIn('Content-Disposition', response)
        self.assertEqual(response['content-disposition'], 'attachment; filename="123.ics"')


class TestUtils(TestCase):
    def test_parse_rrule_empty(self):
        self.assertEqual(build_rrule(), {})

    def test_parse_rrule_freq_invalid(self):
        try:
            build_rrule(freq='invalid')
            self.fail('Value error was expected')
        except ValueError:
            pass

    def test_parse_rrule_all_values(self):
        rrule = build_rrule(
            count=1,
            interval=2,
            bysecond=3,
            byminute=4,
            byhour=5,
            byweekno=6,
            bymonthday=7,
            byyearday=8,
            bymonth=9,
            until=datetime(2015, 1, 13, 14, 15, 16),
            bysetpos=10,
            wkst='MO',
            byday='TU',
            freq='WEEKLY',
        )

        # expected length
        self.assertEqual(len(rrule), 14)
        # testing that function created keys for each key in vRecur:
        self.assertEqual(sorted(rrule.keys()), sorted(vRecur.types.keys()))
        #expected values:
        self.assertEqual(rrule['COUNT'], 1)
        self.assertEqual(rrule['INTERVAL'], 2)
        self.assertEqual(rrule['BYSECOND'], 3)
        self.assertEqual(rrule['BYMINUTE'], 4)
        self.assertEqual(rrule['BYHOUR'], 5)
        self.assertEqual(rrule['BYWEEKNO'], 6)
        self.assertEqual(rrule['BYMONTHDAY'], 7)
        self.assertEqual(rrule['BYYEARDAY'], 8)
        self.assertEqual(rrule['BYMONTH'], 9)
        self.assertEqual(rrule['UNTIL'], datetime(2015, 1, 13, 14, 15, 16))
        self.assertEqual(rrule['BYSETPOS'], 10)
        self.assertEqual(rrule['WKST'], 'MO')
        self.assertEqual(rrule['BYDAY'], 'TU')
        self.assertEqual(rrule['FREQ'], 'WEEKLY')
