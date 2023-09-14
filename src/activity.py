import math
import datetime
from enum import Enum


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

    def __init__(self, time: datetime):
        self.time = time
        self.heartRate = 0
        self.distanceMeters = 0
        self.speed = 0
        self.latitudeDegrees = 0
        self.longitudeDegrees = 0
        self.altitudeMeters = 0
        self.steps = 0
        self.cadence = 0

    def GetPointSeconds(self):
        tm = self.time
        sec = datetime.timedelta(days=tm.day, hours=tm.hour, minutes=tm.minute, seconds=tm.second).total_seconds()
        return sec


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
    avgHeartRate: int
    maxHeartRate: int

    trackPoints: dict # key = time, value = TrackPoint
    trackPointsWaitingAltitude: list # track points waiting altitude measurement

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
        self.trackPoints = dict()
        self.trackPointsWaitingAltitude = list()
        self.avgHeartRate = 0
        self.maxHeartRate = 0

    def LogBatteryLevel(self, level: int):
        if self.batteryLevelMin == 0:
            self.batteryLevelMin = level
        if self.batteryLevelMax == 0:
            self.batteryLevelMax = level
        if self.batteryLevelMin > level:
            self.batteryLevelMin = level
        if self.batteryLevelMax < level:
            self.batteryLevelMax = level

    def GetTrackPointAt(self, time: datetime):
        point: TrackPoint
        if time in self.trackPoints:
            point = self.trackPoints[time]
        else:
            point = TrackPoint(time)
            self.trackPoints[time] = point
            self.trackPointsWaitingAltitude.append(point)
        return point

    def LogHeartRate(self, time: datetime, heartRate: int):
        point = self.GetTrackPointAt(time)
        point.heartRate = heartRate

    def LogSteps(self, time: datetime, totalSteps: int, distance: float):
        point = self.GetTrackPointAt(time)
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

        prevPoint: TrackPoint = None
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

        print("   Distance: %s m" % (round(self.totalDistanceMeters)))
        print("   Max heart rate: %s" % (round(self.maxHeartRate)))
        print("   Avg heart rate: %s" % (round(self.avgHeartRate)))
        print("   Max pace: %s min/km" % (self.FormatPaceMinPerKm(self.maxSpeed)))
        print("   Avg pace: %s min/km" % (self.FormatPaceMinPerKm(self.avgSpeed)))
        print("   Battery level: %s%% -> %s%%" % (self.batteryLevelMax, self.batteryLevelMin))

    def FormatPaceMinPerKm(self, speedMPerMin: float):
        if speedMPerMin == 0:
            return "0:00"
        pace: float = 1000.0 / speedMPerMin / 60.0
        paceMin: float = math.floor(pace)
        paceSec = round(60.0 * (pace - paceMin))
        return "%d:%02d" % (paceMin, paceSec)