import datetime

import sys # for cli args

import gpxpy
from geopy.distance import geodesic
from geographiclib.geodesic import Geodesic

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.course_message import CourseMessage
from fit_tool.profile.messages.course_point_message import CoursePointMessage
from fit_tool.profile.messages.event_message import EventMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.profile_type import FileType, Manufacturer, Sport, Event, EventType, CoursePoint

def print_coordinate(coordinate):
    if coordinate:
        (lat,long) = coordinate
        return (("%.5f" % lat), ("%.5f" % long))
    else:
        return None
    
def get_bearing2(lat1, long1, lat2, long2):
    brng = Geodesic.WGS84.Inverse(lat1, long1, lat2, long2)['azi1']
    if brng < 0: brng+= 360
    return round(brng)

def get_bearing_details(richting):
    add_point = True
    type = None
    if 30 <= richting < 60:
        richting_text = "Slight right"
        type = CoursePoint.SLIGHT_RIGHT
    elif 60 <= richting < 120:
        richting_text = "Right"
        type = CoursePoint.RIGHT
    elif 120 <= richting < 170:
        richting_text = "Sharp right"
        type = CoursePoint.SHARP_RIGHT
    elif 170 <= richting < 190:
        richting_text = "Turn back"
        type = CoursePoint.U_TURN
    elif 190 <= richting < 240:
        richting_text = "Sharp left"
        type = CoursePoint.SHARP_LEFT
    elif 240 <= richting < 300:
        richting_text = "Left"
        type = CoursePoint.LEFT
    elif 300 <= richting < 330:
        richting_text = "Slight left"
        type = CoursePoint.SLIGHT_LEFT
    else:
        richting_text = ""
        add_point = False
    print ("getbearingdetails", richting, add_point,richting_text, type)
    return (add_point,richting_text, type)

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
    #distance_prev_cp = 0.0
    timestamp = start_timestamp

    course_records = []  # track points
    course_waypoints = []  # waypoints
    prev_coordinate = None
    prev_bearing = None
    delta = 0.0
    bearing_min = 20 # only set coursepoints when the distance is over bearing_min
    trackpointindex = 0
    # richting_distance = 0
    distance_since_last_direction = 0
    ## FOR
    print("Total GPS points: ", len(gpx.tracks[0].segments[0].points))
    for track_point in gpx.tracks[0].segments[0].points:
        current_coordinate = (track_point.latitude, track_point.longitude)

        if trackpointindex > 0:
            prev_coordinate = (gpx.tracks[0].segments[0].points[trackpointindex-1].latitude, gpx.tracks[0].segments[0].points[trackpointindex-1].longitude)
        if trackpointindex < len(gpx.tracks[0].segments[0].points)-1:
            # If last point then next_coordinate is not updated (still last point, not set to NULL), so delta will become 0
            next_coordinate = (gpx.tracks[0].segments[0].points[trackpointindex+1].latitude, gpx.tracks[0].segments[0].points[trackpointindex+1].longitude)
        # If a previous coordinate is set (ie not first point in track)
        # if prev_coordinate:
        delta = geodesic(current_coordinate, next_coordinate).meters
        # (lat1, lon1) = prev_coordinate
        # (lat2, lon2) = current_coordinate
        (lat1, lon1) = current_coordinate
        (lat2, lon2) = next_coordinate
        bearing = get_bearing2(lat1,lon1,lat2,lon2)
        print ("TP: ", trackpointindex,
               "deltadistance: ", round(delta),
               "(prev) bearing: ", prev_bearing, bearing,
               "total distance: ", round(distance),
            #    "prev", print_coordinate(prev_coordinate),
               "curr", print_coordinate(current_coordinate),
            #    "next", print_coordinate(next_coordinate),
                )

        if prev_bearing is not None:

            richting = round(bearing - prev_bearing)

            if richting < 0:
                richting += 360

            print("Richting: ", richting)

            # FIXME waarom gebruik je richting_distance? En waarom distance-richting_distance? Je doet vlak daarna nog een check? Alleen om te checken of delta bestaat?
            # if (distance - richting_distance) > bearing_min or richting_distance == 0:
            wp_message = CoursePointMessage() # Create here, so we can set wp_message.type
            (add_point,richting_text,wp_message.type) = get_bearing_details(richting)
            # FIXME je wilt niet message onderdrukken bij korte afstanden.. je wilt vooral geen berichten als je er net 1 hebt gehad
            if add_point == True and distance_since_last_direction > bearing_min and delta > 0:
                wp_message.timestamp = timestamp
                wp_message.position_lat = track_point.latitude
                wp_message.position_long = track_point.longitude
                wp_message.distance = distance

                distance_since_last_direction = 0

                # Moet dit niet buiten deze if-statements?
                # richting_distance = distance
                print("WP added")
                course_waypoints.append(wp_message)

        distance_since_last_direction += delta
        prev_bearing = bearing

        for wp in gpx.waypoints:
            if (wp.latitude == track_point.latitude and wp.longitude == track_point.longitude) or (prev_coordinate and (prev_coordinate[0] <= wp.latitude <= current_coordinate[0] and prev_coordinate[1] <= wp.longitude <= current_coordinate[1])):
                print(wp.name)
                wp_message = CoursePointMessage()
                wp_message.timestamp = timestamp
                wp_message.position_lat = wp.latitude
                wp_message.position_long = wp.longitude
                wp_message.distance = distance
                wp_message.type = CoursePoint.GENERIC
                wp_message.course_point_name = wp.name
                if distance != 0.0:
                    course_waypoints.append(wp_message)
                    gpx.waypoints.remove(wp)

        distance += delta

        message = RecordMessage()
        message.position_lat = track_point.latitude
        message.position_long = track_point.longitude
        message.distance = distance
        message.timestamp = timestamp
        message.enhanced_altitude = 0 # FIXME Als er een elevation is, toevoegen, anders op nul laten
        course_records.append(message)

        timestamp += 10000
        prev_coordinate = current_coordinate  # FIXME : je set deze ook al bovenin de functie, dus of deze of die ander kan weg
        trackpointindex += 1
    ## ENDFOR

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

