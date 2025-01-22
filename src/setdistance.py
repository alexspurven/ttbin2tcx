import os
import sys
from tcxeditor import TcxFileEditor


def main():
    argcnt = len(sys.argv)
    if argcnt != 3:
        print("Wrong arguments")
        exit()

    fileTcx = sys.argv[1]
    newLen = float(sys.argv[2])
    process(fileTcx, newLen)

    return 0


def process(fileTcx: str, newLen: float):
    dir, f_name = os.path.split(fileTcx)
    f_name = "d-%s" % f_name
    fileTcxOut = os.path.join(dir, f_name)

    editor = TcxFileEditor()
    editor.LoadXml(fileTcx)
    if editor.ChangeLength(newLen):
        editor.SaveXml(fileTcxOut)


if __name__ == "__main__":
    main()
