import datetime

import sys # for cli args

import gpxpy
from geopy.distance import geodesic

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.course_message import CourseMessage
from fit_tool.profile.messages.course_point_message import CoursePointMessage
from fit_tool.profile.messages.event_message import EventMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.profile_type import FileType, Manufacturer, Sport, Event, EventType, CoursePoint


def main():
    # Set auto_define to true, so that the builder creates the required Definition Messages for us.
    builder = FitFileBuilder(auto_define=True, min_string_size=50)

    if len(sys.argv) == 1:
        print("Geef arg mee")
        exit(1)

    # Read position data from a GPX file
    gpx_file = open(sys.argv[1], 'r')
    gpx = gpxpy.parse(gpx_file)

    if len(gpx.tracks) == 0:
        print("No track found in GPX")
        exit(1)

    if len(gpx.waypoints) == 0:
        print("No track found in GPX")
        exit(1)

    message = FileIdMessage()
    message.type = FileType.COURSE
    message.manufacturer = Manufacturer.DEVELOPMENT.value
    message.product = 0
    message.time_created = round(datetime.datetime.now().timestamp() * 1000)
    message.serial_number = 0x12345678
    message.number = 1
    builder.add(message)

    # Every FIT course file MUST contain a Course message
    message = CourseMessage()
    message.course_name = gpx.tracks[0].name
    message.sport = Sport.WALKING
    builder.add(message)

    start_timestamp = round(datetime.datetime.now().timestamp() * 1000)

    distance = 0.0
    timestamp = start_timestamp

    course_records = []  # track points
    course_waypoints = []  # waypoints
    prev_coordinate = None

    for track_point in gpx.tracks[0].segments[0].points:
        current_coordinate = (track_point.latitude, track_point.longitude)

        # calculate distance from previous coordinate and accumulate distance
        if prev_coordinate:
            delta = geodesic(prev_coordinate, current_coordinate).meters
        else:
            delta = 0.0
        distance += delta

        for wp in gpx.waypoints:
            if wp.latitude == track_point.latitude and wp.longitude == track_point.longitude:
                wp_message = CoursePointMessage()
                wp_message.timestamp = timestamp
                #wp_message.timestamp = int(wp.time.timestamp() * 1000)
                wp_message.position_lat = wp.latitude
                wp_message.position_long = wp.longitude
                wp_message.distance = distance
                wp_message.type = CoursePoint.GENERIC
                wp_message.course_point_name = wp.name
                if distance != 0.0:
                    course_waypoints.append(wp_message)

        message = RecordMessage()
        message.position_lat = track_point.latitude
        message.position_long = track_point.longitude
        message.distance = distance
        message.timestamp = timestamp
        message.enhanced_altitude = 0
        course_records.append(message)

        timestamp += 10000
        prev_coordinate = current_coordinate

    # Every FIT course file MUST contain a Lap message
    elapsed_time = timestamp - start_timestamp
    message = LapMessage()
    message.timestamp = timestamp
    message.start_time = start_timestamp
    message.total_distance = course_records[-1].distance
    builder.add(message)

    # Timer Events are REQUIRED for FIT course files
    message = EventMessage()
    message.event = Event.TIMER
    message.event_type = EventType.START
    message.timestamp = start_timestamp
    message.event_group = 0
    builder.add(message)

    builder.add_all(course_records)

    #  Add start and end course points (i.e. way points)
    #
    message = CoursePointMessage()
    message.timestamp = course_records[0].timestamp
    message.position_lat = course_records[0].position_lat
    message.position_long = course_records[0].position_long
    message.type = CoursePoint.SEGMENT_START
    message.course_point_name = 'start'
    builder.add(message)

    builder.add_all(course_waypoints)

    message = CoursePointMessage()
    message.timestamp = course_records[-1].timestamp
    message.position_lat = course_records[-1].position_lat
    message.position_long = course_records[-1].position_long
    message.type = CoursePoint.SEGMENT_END
    message.course_point_name = 'end'
    builder.add(message)

    # stop event
    message = EventMessage()
    message.event = Event.TIMER
    message.event_type = EventType.STOP_DISABLE_ALL
    message.timestamp = timestamp
    message.event_group = 0
    builder.add(message)

    # Finally build the FIT file object and write it to a file
    fit_file = builder.build()

    out_path = sys.argv[1] + '.fit'
    fit_file.to_file(out_path)
    csv_path = sys.argv[1] + '.csv'
    fit_file.to_csv(csv_path)


if __name__ == "__main__":
    main()

