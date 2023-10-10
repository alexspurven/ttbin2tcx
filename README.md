# ttbin2tcx

TomTom's sport watch TTBIN format to Garmin's TCX format converter.

Goal is allow sport watches using after [TomTom Sports discontinuation](https://help.tomtom.com/hc/en-us/articles/11748276052370).

## Status

Currently supported **Running**, **Treadmill** and **Gym** activities from **Adventurer** watches.

Supported distance correction for Treadmill activities.

Cadence is calculated for Running and Treadmill activities.

Added laps support.

## How to use

1. Use [TomTomWatch](https://github.com/scubajorgen/TomTomWatch) tool from [Studio Blue Planet](https://blog.studioblueplanet.net/software/tomtomwatch) to extract TTBIN files from the watches.
These files are not synchronized actities and temporary saved within watches (syncronization with TomTom will remove them).

2. Optional: copy loaded TTBIN files into some folder.

3. Run a command for convertion:

   ***(path to python)python.exe (path to src)main.py (path to ttbin file or to a folder with ttbin files)***

   Example how to to convert all TTBIN files in a folder:

   ***"c:\Program Files\Python311\python.exe" "C:/Users/User/GitHub/ttbin2tcx/src/main.py" "c:\Users\User\OneDrive\tomtom all\ttbin2tcx\test3"***

   Example how to to convert a single TTBIN file:

   ***"c:\Program Files\Python311\python.exe" "C:/Users/User/GitHub/ttbin2tcx/src/main.py" "c:\Users\User\OneDrive\tomtom all\ttbin2tcx\test3\Running_17-54-17.ttbin"***

   TCX files are created in the same folder where TTBIN are, file names are in "activityType-yyyyMMddhhmmss" format.

   ![](/res/console.png)

4. Upload TCX files to your favorite fitness service.
