import datetime
import io

import vobject

text = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//Example Corp.//CalDAV Client//EN\r\n"
    "BEGIN:VTODO\r\n"
    "UID:20070313T123432Z-456553@example.com\r\n"
    "DTSTAMP:20070313T123432Z\r\n"
    "DUE;VALUE=DATE:20070501\r\n"
    "SUMMARY:Submit Quebec Income Tax Return for 2006\r\n"
    "CLASS:CONFIDENTIAL\r\n"
    "CATEGORIES:FAMILY,FINANCE\r\n"
    "STATUS:NEEDS-ACTION\r\n"
    "END:VTODO\r\n"
    "END:VCALENDAR\r\n"
)


def test_vtodo():
    """
    Test VTodo
    """
    obj = vobject.readOne(io.StringIO(text))
    obj.vtodo.add("completed")
    obj.vtodo.completed.value = datetime.datetime(2015, 5, 5, 13, 30)
    assert obj.vtodo.completed.serialize()[0:23] == "COMPLETED:20150505T1330"

    obj = vobject.readOne(obj.serialize())
    assert obj.vtodo.completed.value == datetime.datetime(2015, 5, 5, 13, 30)


apple_location_alarm = (
    "BEGIN:VCALENDAR\r\n"
    "VERSION:2.0\r\n"
    "PRODID:-//Apple Inc.//iOS 18.7.10//EN\r\n"
    "BEGIN:VTODO\r\n"
    "UID:41698F95-30E4-4F10-B41B-5DED0BF1FA39\r\n"
    "DTSTAMP:20261022T160855Z\r\n"
    "SUMMARY:Location test\r\n"
    "BEGIN:VALARM\r\n"
    "ACTION:DISPLAY\r\n"
    "DESCRIPTION:Reminder\r\n"
    "TRIGGER;VALUE=DATE-TIME:19760401T005545Z\r\n"
    "X-APPLE-PROXIMITY:ARRIVE\r\n"
    "X-APPLE-STRUCTURED-LOCATION;VALUE=URI;X-APPLE-RADIUS=100;X-TITLE=Office:geo:48.1,11.5\r\n"
    "END:VALARM\r\n"
    "END:VTODO\r\n"
    "END:VCALENDAR\r\n"
)


def test_uri_value_keeps_commas():
    """
    A comma in a VALUE=URI property is data, not a TEXT list separator.
    """
    obj = vobject.readOne(apple_location_alarm)
    location = obj.vtodo.valarm.contents["x-apple-structured-location"][0]
    assert location.value == "geo:48.1,11.5"

    serialized = obj.serialize().replace("\r\n ", "")
    assert "X-TITLE=Office:geo:48.1,11.5\r\n" in serialized

    roundtrip = vobject.readOne(serialized)
    assert roundtrip.vtodo.valarm.contents["x-apple-structured-location"][0].value == "geo:48.1,11.5"


def test_text_value_still_unescaped():
    """
    Unknown properties without VALUE=URI keep the TEXT behaviour.
    """
    obj = vobject.readOne(apple_location_alarm.replace("X-APPLE-PROXIMITY:ARRIVE", "X-FOO:a\\,b"))
    assert obj.vtodo.valarm.contents["x-foo"][0].value == "a,b"
    assert "X-FOO:a\\,b\r\n" in obj.serialize()
