import math
import datetime
from enum import Enum


class ArgConstant:
    HRZones: str = "-hrzones" # like 130;140;150;160;170;180;


class ActivityType(Enum):
    Running = 0x00
    Cycling = 0x01
    Swimming = 0x02
    Treadmill = 0x07
    Freestyle = 0x08
    Gym = 0x09
    Hiking = 0x0A
    IndoorCycling = 0x0B
    TrailRunning = 0x0E
    Skiing = 0x0F
    Snowboarding = 0x10


# one piece of data
class TrackPoint:
    time: datetime
    heartRate: int
    distanceMeters: float
    speed: float
    latitudeDegrees: float
    longitudeDegrees: float
    altitudeMeters: int
    steps: int
    cadence: int
    lapIndex: int

    def __init__(self, time: datetime, lapIndex: int):
        self.time = time
        self.lapIndex = lapIndex
        self.heartRate = 0
        self.distanceMeters = 0
        self.speed = 0 # m/s
        self.latitudeDegrees = 0
        self.longitudeDegrees = 0
        self.altitudeMeters = 0
        self.steps = 0
        self.cadence = 0

    def GetPointSeconds(self):
        tm = self.time
        sec = datetime.timedelta(days=tm.day, hours=tm.hour, minutes=tm.minute, seconds=tm.second).total_seconds()
        return sec


class Lap:
    seconds: int
    distance: float
    calories: int
    startTime: datetime

    def __init__(self, seconds: int, distance: float, calories: int):
        self.seconds = seconds
        self.distance = distance
        self.calories = calories
        self.startTime = datetime.datetime.now(datetime.timezone.utc)


# recorded activity
class Activity(object):
    activityType: ActivityType
    startTime: datetime
    totalActiveSeconds: int
    totalElapsedSeconds: int
    totalDistanceMeters: float
    totalCalories: int
    totalSteps: int
    totalAscendMeters: int
    totalDescendMeters: int
    avgSpeed: float
    maxSpeed: float
    batteryLevelMin: int
    batteryLevelMax: int
    batteryLevels: list
    avgHeartRate: int
    maxHeartRate: int
    heartRatesByZone: dict # key = maxHR in zone, value = number of points
    currentLapIndex: int
    trackPoints: dict # key = time, value = TrackPoint
    trackPointsWaitingAltitude: list # track points waiting altitude measurement
    laps: list
    defaultYear: int = 1970 # sometimes get 1969 year from TTBin

    def __init__(self):
        self.activityType = ActivityType.Running
        self.startTime = datetime.datetime.today()
        self.totalActiveSeconds = 0
        self.totalElapsedSeconds = 0
        self.totalDistanceMeters = 0
        self.totalCalories = 0
        self.totalSteps = 0
        self.totalAscendMeters = 0
        self.totalDescendMeters = 0
        self.avgSpeed = 0
        self.maxSpeed = 0
        self.batteryLevelMin = 0
        self.batteryLevelMax = 0
        self.batteryLevels = list()
        self.trackPoints = dict()
        self.trackPointsWaitingAltitude = list()
        self.avgHeartRate = 0
        self.maxHeartRate = 0
        self.heartRatesByZone = dict()
        self.laps = list()
        self.currentLapIndex = 0

    def LogBatteryLevel(self, level: int):
        self.batteryLevels.append(level)
        if self.batteryLevelMin == 0:
            self.batteryLevelMin = level
        if self.batteryLevelMax == 0:
            self.batteryLevelMax = level
        if self.batteryLevelMin > level:
            self.batteryLevelMin = level
        if self.batteryLevelMax < level:
            self.batteryLevelMax = level

    # creates if necessary and returns a trackpoint at specified time
    # returns null for default date
    def GetTrackPointAt(self, time: datetime):
        point: TrackPoint

        if time.year < self.defaultYear:
            return None

        if time in self.trackPoints:
            point = self.trackPoints[time]
        else:
            point = TrackPoint(time, self.currentLapIndex)
            self.trackPoints[time] = point
            self.trackPointsWaitingAltitude.append(point)

        return point

    def LogHeartRate(self, time: datetime, heartRate: int):
        point = self.GetTrackPointAt(time)
        if point is not None:
            point.heartRate = heartRate
        self.AddToHRZones(heartRate)

    def LogSteps(self, time: datetime, totalSteps: int, distance: float):
        point = self.GetTrackPointAt(time)
        if point is not None:
            point.steps = totalSteps - self.totalSteps
            self.totalSteps = totalSteps
            point.distanceMeters = distance

    def LogElevation(self, altitude: int, ascend: int, descend: int):
        self.totalAscendMeters = ascend
        self.totalDescendMeters = descend

        for point in self.trackPointsWaitingAltitude:
            point.altitudeMeters = altitude
        self.trackPointsWaitingAltitude.clear()

    def LogGps(self, time: datetime, latitude: float, longitude: float, speed: float, steps: int, distance: float):
        point = self.GetTrackPointAt(time)
        if point is not None:
            point.steps = steps
            point.speed = speed
            point.latitudeDegrees = latitude
            point.longitudeDegrees = longitude
            point.distanceMeters = distance
            self.totalSteps = self.totalSteps + steps

    def PostLoad(self):
        # calculate cadence
        groupBySec = 10.0
        cyclesByXXSec = dict()

        for time in self.trackPoints:
            point = self.trackPoints[time]
            sec = point.GetPointSeconds()
            groupTime = math.floor(sec / groupBySec)
            cyclesByXXSec[groupTime] = cyclesByXXSec.get(groupTime, 0) + point.steps

        for groupTime in cyclesByXXSec:
            cyclesByXXSec[groupTime] = cyclesByXXSec[groupTime] * 60.0 / groupBySec / 2.0

        if self.activityType == ActivityType.Treadmill:
            # correcting distance for treadmill
            maxDistanceFromPoints: float = 0
            for time in self.trackPoints:
                point: TrackPoint = self.trackPoints[time]
                if point.distanceMeters > maxDistanceFromPoints:
                    maxDistanceFromPoints = point.distanceMeters
            if  maxDistanceFromPoints > 0:
                factor: float = self.totalDistanceMeters / maxDistanceFromPoints
                for time in self.trackPoints:
                    point: TrackPoint = self.trackPoints[time]
                    point.distanceMeters = point.distanceMeters * factor

        prevPoint = None
        for time in sorted(self.trackPoints):
            point: TrackPoint = self.trackPoints[time]
            if self.activityType == ActivityType.Treadmill:
                point.speed = 0
            if prevPoint is not None:
                # correcting zero distance
                if point.distanceMeters == 0:
                    point.distanceMeters = prevPoint.distanceMeters

                # correcting speed for treadmill
                if self.activityType == ActivityType.Treadmill:
                    timeDiff = (point.time - prevPoint.time).seconds * 1000.0 \
                        + (point.time - prevPoint.time).microseconds
                    distDiff = point.distanceMeters - prevPoint.distanceMeters
                    if timeDiff > 0:
                        point.speed = distDiff * 1000.0 / timeDiff

            prevPoint = point

        # max and avg speed, max and avg heart rate
        self.maxSpeed = 0
        self.maxHeartRate = 0
        heartRatePoints = 0
        heartRateSum = 0
        for time in self.trackPoints:
            point: TrackPoint = self.trackPoints[time]
            sec = point.GetPointSeconds()
            groupTime = math.floor(sec / groupBySec)
            point.cadence = cyclesByXXSec[groupTime]
            if point.speed > self.maxSpeed:
                self.maxSpeed = point.speed
            if point.heartRate > self.maxHeartRate:
                self.maxHeartRate = point.heartRate
            if point.heartRate > 0:
                heartRatePoints = heartRatePoints + 1
                heartRateSum = heartRateSum + point.heartRate
        self.avgSpeed = 0
        if self.totalActiveSeconds > 0:
            self.avgSpeed = self.totalDistanceMeters / self.totalActiveSeconds
        self.avgHeartRate = 0
        if heartRatePoints > 0:
            self.avgHeartRate = heartRateSum / heartRatePoints

        # creating default or trailing lap
        if self.currentLapIndex == len(self.laps):
            self.LogLap(self.totalActiveSeconds, self.totalDistanceMeters, self.totalCalories)
        # finding laps start time
        for time in self.trackPoints:
            point: TrackPoint = self.trackPoints[time]
            lap = self.laps[point.lapIndex]
            if lap.startTime > point.time:
                lap.startTime = point.time

        # linear trend for battery levels
        if len(self.batteryLevels) > 0:
            # filtering out outliers
            mean = sum(self.batteryLevels) / len(self.batteryLevels)
            squared_diffs = [(x - mean) ** 2 for x in self.batteryLevels]
            variance = sum(squared_diffs) / len(self.batteryLevels)
            std_dev = variance ** 0.5
            self.batteryLevels = [x for x in self.batteryLevels if abs(x - mean) <= 2 * std_dev]
            # trend for rest
            avgX = (len(self.batteryLevels) + 1) / 2
            avgY = sum(self.batteryLevels) / len(self.batteryLevels)
            sumXDif = 0
            sumYDif = 0
            sumXdifYdif = 0
            sumXdifXdif = 0
            for idx, lvl in enumerate(self.batteryLevels):
                sumXDif = sumXDif + (idx - avgX)
                sumYDif = sumYDif + (lvl - avgY)
                sumXdifYdif = sumXdifYdif + (idx - avgX) * (lvl - avgY)
                sumXdifXdif = sumXdifXdif + (idx - avgX) * (idx - avgX)
            if sumXdifXdif != 0:
                a = sumXdifYdif / sumXdifXdif
                b = avgY - a * avgX
                #self.batteryLevelMax = a * 1 + b
                self.batteryLevelMin = (len(self.batteryLevels) + 1) * a + b

        print("   Distance: %s m" % (round(self.totalDistanceMeters)))
        print("   Max pace: %s min/km" % (self.FormatPaceMinPerKm(self.maxSpeed)))
        print("   Avg pace: %s min/km" % (self.FormatPaceMinPerKm(self.avgSpeed)))

        # heart rate zones info
        print("   Max heart rate: %s" % (round(self.maxHeartRate)))
        print("   Avg heart rate: %s" % (round(self.avgHeartRate)))
        totalHRpoints: int = 0
        for maxZoneHeartRate in self.heartRatesByZone:
            totalHRpoints = totalHRpoints + self.heartRatesByZone[maxZoneHeartRate]
        if totalHRpoints > 0:
            for idx, maxZoneHeartRate in enumerate(self.heartRatesByZone):
                zone: int = idx + 1
                percent: int =  round(self.heartRatesByZone[maxZoneHeartRate] / totalHRpoints * 100)
                bar: str = "".join([char * round(percent / 3) for char in "#"])
                heartRateRange: str
                if idx == 0:
                    heartRateRange = "...-%s" % maxZoneHeartRate
                elif idx == len(self.heartRatesByZone) - 1:
                    heartRateRange = "%s-..." % (list(self.heartRatesByZone)[idx - 1] + 1)
                else:
                    heartRateRange = "%s-%s" % (list(self.heartRatesByZone)[idx - 1] + 1, maxZoneHeartRate)
                if len(bar) > 0:
                    print("   Zone %s (%s): %s %s%%" % (zone, heartRateRange, bar, percent))
                else:
                    print("   Zone %s (%s): %s%%" % (zone, heartRateRange, percent))

        print("   Battery level: %s%% -> %s%%" % (round(self.batteryLevelMax), round(self.batteryLevelMin)))
        print("   Steps: %s" % (round(self.totalSteps)))
        print("   Calories: %s" % (round(self.totalCalories)))
        return

    def FormatPaceMinPerKm(self, speedMPerMin: float):
        if speedMPerMin == 0:
            return "0:00"
        pace: float = 1000.0 / speedMPerMin / 60.0
        paceMin: float = math.floor(pace)
        paceSec = round(60.0 * (pace - paceMin))
        return "%d:%02d" % (paceMin, paceSec)

    def LogLap(self, seconds: int, distance: float, calories: int):
        # there are accumulated values are passed here
        # calculating values just for this lap
        sumSeconds: int = 0
        sumDistance = 0
        sumCalories = 0
        for lap in self.laps:
            sumSeconds = sumSeconds + lap.seconds
            sumDistance = sumDistance + lap.distance
            sumCalories = sumCalories + lap.calories
        lap = Lap(seconds - sumSeconds, distance - sumDistance, calories - sumCalories)
        self.laps.append(lap)
        self.currentLapIndex = self.currentLapIndex + 1
        return

    def BuildHRZones(self, args: list[str]):
        self.heartRatesByZone.clear()
        for idx, arg in enumerate(args):
            if arg == ArgConstant.HRZones and len(args) > idx + 1:
                self.ParseHRZones(args[idx + 1])
                return
        return

    def ParseHRZones(self, zones: str):
        if len(zones) == 0:
            print("Wrong heart rate zones parameter %s" % zones)
            return

        zoneList = zones.split(";")
        for zoneStr in zoneList:
            zoneMax = int(zoneStr)
            self.heartRatesByZone[zoneMax] = 0
        self.heartRatesByZone[999] = 0
        return

    def AddToHRZones(self, heartRate: int):
        for maxZoneHeartRate in self.heartRatesByZone:
            if maxZoneHeartRate >= heartRate:
                self.heartRatesByZone[maxZoneHeartRate] = self.heartRatesByZone[maxZoneHeartRate] + 1
                return
        return
