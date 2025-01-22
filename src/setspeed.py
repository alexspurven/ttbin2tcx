import os
import sys
from tcxeditor import TcxFileEditor


def main():
    argcnt = len(sys.argv)
    if argcnt != 3:
        print("Wrong arguments")
        exit()

    fileTcx = sys.argv[1]
    intervals = sys.argv[2].strip().lower()
    # intervals mode definition:
    #   interval1;interval2;...
    # where interval is:
    #   "distance of interval in meters"m"speed km/h"
    # or
    #   "time of interval in seconds"s"speed km/h"
    # example:
    #   400m12;60s9.5;5000m10.0
    #
    # laps mode definition:
    #  l"speed for lap 1 km/h";"speed for lap2 km/h"; ...
    # example:
    #   l9;12;9;12;10
    process(fileTcx, intervals)

    return 0


def process(fileTcx: str, intervals: str):
    dir, f_name = os.path.split(fileTcx)
    f_name = "s-%s" % f_name
    fileTcxOut = os.path.join(dir, f_name)

    editor = TcxFileEditor()
    editor.LoadXml(fileTcx)
    if editor.ChangeSpeed(intervals):
        editor.SaveXml(fileTcxOut)


if __name__ == "__main__":
    main()
