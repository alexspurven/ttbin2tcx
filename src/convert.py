import os
import sys
import datetime
from classes.tcxwriter import TcxFileWriter
from classes.ttbinreader import TtbinFileReader


def main():
    argcnt = len(sys.argv)
    if argcnt < 2:
        print("Wrong arguments")
        exit()

    fileOrDir = sys.argv[1]

    if os.path.isfile(fileOrDir):
        f_name, f_ext = os.path.splitext(fileOrDir)
        if f_ext.lower() == ".ttbin":
            process(fileOrDir, sys.argv)
        else:
            print("Skipped %s" % fileOrDir)

    if os.path.isdir(fileOrDir):
        files = [f for f in os.listdir(fileOrDir) if os.path.isfile(os.path.join(fileOrDir, f))]
        for f in files:
            f_name, f_ext = os.path.splitext(f)
            if f_ext.lower() == ".ttbin":
                fileTtbin = os.path.join(fileOrDir, f)
                process(fileTtbin, sys.argv)
    return 0


def process(fileTtbin: str, args: list[str]):
    reader = TtbinFileReader()
    activity = reader.LoadActivity(fileTtbin, args)

    #f_name, f_ext = os.path.splitext(fileTtbin)
    #fileTcx = f_name + ".tcx"

    dir = os.path.dirname(fileTtbin)
    dt = activity.startTime + datetime.timedelta(days=0, seconds=reader.localTimeOffset)
    fileNameTcx = "%s-%s.tcx" % (activity.activityType.name.lower(), dt.strftime("%Y%m%d%H%M%S"))
    fileTcx = os.path.join(dir, fileNameTcx)
    writer = TcxFileWriter()
    writer.SaveActivity(fileTcx, activity)


if __name__ == "__main__":
    main()
