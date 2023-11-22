
import sys # for cli args
from fit_tool.fit_file import FitFile

from fit_tool.fit_file_builder import FitFileBuilder
from fit_tool.profile.messages.course_message import CourseMessage
from fit_tool.profile.messages.course_point_message import CoursePointMessage
from fit_tool.profile.messages.event_message import EventMessage
from fit_tool.profile.messages.file_id_message import FileIdMessage
from fit_tool.profile.messages.lap_message import LapMessage
from fit_tool.profile.messages.record_message import RecordMessage
from fit_tool.profile.profile_type import FileType, Manufacturer, Sport, Event, EventType, CoursePoint


def main():
    """ The following code reads all the bytes from a FIT formatted file and then decodes these bytes to
        create a FIT file object. We then convert the FIT data to a human-readable CSV file.
    """
    if len(sys.argv) == 1:
        print("Geef FIT file mee")
        exit(1)

    path = sys.argv[1]
    fit_file = FitFile.from_file(path)

    out_path = sys.argv[1] + '.csv'
    fit_file.to_csv(out_path)


if __name__ == "__main__":
    main()
