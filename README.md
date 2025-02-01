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

   ***(path to python)python.exe (path to src)convert.py (path to ttbin file or to a folder with ttbin files)***

   Example how to to convert all TTBIN files in a folder:

   ***"c:\Program Files\Python311\python.exe" "C:/Users/User/GitHub/ttbin2tcx/src/convert.py" "c:\Users\User\OneDrive\tomtom all\ttbin2tcx\test3"***

   Example how to to convert a single TTBIN file:

   ***"c:\Program Files\Python311\python.exe" "C:/Users/User/GitHub/ttbin2tcx/src/convert.py" "c:\Users\User\OneDrive\tomtom all\ttbin2tcx\test3\Running_17-54-17.ttbin"***

   TCX files are created in the same folder where TTBIN are, file names are in "activityType-yyyyMMddhhmmss" format.

   ![](/res/console.png)

4. Upload TCX files to your favorite fitness service.

## Changing distance tool for Treadmill activities

Changes tracked distance in tcx files. Works only for Treadmill activities. Total time is not changed.
Output files are created with the "d-" prefix in the same folder where source files are.

Using:

***(path to python)python.exe (path to src)setdistance.py (path to tcx file) (new distance in meters)***
	
Example:
	
***"c:\Program Files\Python311\python.exe" "C:/Users/User/GitHub/ttbin2tcx/src/setdistance.py" "c:\Users\User\OneDrive\treadmill-20250131191034.tcx" 5000***
	
## Changing speed tool for Treadmill activities

Applies speed specification for tcx files for Treadmill activities. Total time and distance are not changed.
Output files are created with the "s-" prefix in the same folder where source files are.

![](/res/speed.png)

Using:

***(path to python)python.exe (path to src)setspeed.py (path to tcx file) (speed specification)***
	
Example:
	
***"c:\Program Files\Python311\python.exe" "C:/Users/User/GitHub/ttbin2tcx/src/setspeed.py" "c:\Users\User\OneDrive\treadmill-20250130180916.tcx" L10;10.2;10.4;10.6;10.8;11;11.2;11.4;11.6;11.8;12***

Speed specification for laps (can't be mixed with specification for intervals):

***L(speed for lap 1 in km/h)(speed for lap 2 in km/h);...***

Example:

***L10;10.2;10.4;10.6;10.8***

Speed specification for intervals:

***(distance in meters for interval 1)m(speed in km/h) or (time in seconds for interval 1)m(speed in km/h);...***

Examples:

***5000m10***
***1000m10;300s12;1000m10;300s12;1000m10***
***300s10.5;100s12;300s10.5;100s12;300s10.5***