import datetime
from enum import Enum
from struct import Struct
from typing import BinaryIO
from .activity import Activity, ActivityType


class TtbinFileRecordTag(Enum):
    FileHeader = 0x20
    Status = 0x21
    Gps = 0x22
    ExtendedGps = 0x23
    HeartRate = 0x25
    Summary = 0x27
    # PoolSize = 0x2a
    # WheelSize = 0x2b
    TrainingSetup = 0x2d
    Lap = 0x2f
    WaitGps = 0x30
    # CyclingCadence = 0x31
    Treadmill = 0x32
    # Swim = 0x34
    # GoalProgress = 0x35
    x37 = 0x37
    # IntervalSetup = 0x39
    # IntervalStart = 0x3a
    # IntervalFinish = 0x3b
    # RaceSetup = 0x3c
    # RaceResult = 0x3d
    # AltitudeUpdate = 0x3e
    HeartRateRecovery = 0x3f
    # IndoorCycling = 0x40
    Gym = 0x41
    Movement = 0x42
    RouteDescription1 = 0x43
    RouteDescription2 = 0x44
    Elevation = 0x47
    x48 = 0x48
    Battery = 0x49
    FitnessPoints = 0x4a
    x4b = 0x4b
    # Workout = 0x4c


class TtbinFileReader:
    localTimeOffset: int

    def __init__(self):
        self.localTimeOffset = 0

    def LoadActivity(self, fileTtbin: str, args: list[str]):
        print("Loading %s" % fileTtbin)
        activity = Activity()
        activity.BuildHRZones(args)

        with open(fileTtbin, "rb") as ttbinfile:
            while True:
                pos: int = ttbinfile.tell()
                tg = ttbinfile.read(1)
                if len(tg) == 0:
                    #print("   EOF")
                    break

                #if tg[0] in TtbinFileRecordTag._value2member_map_:
                #    print("   Tag: 0x%s %s Pos: 0x%s" \
                #          % (format(tg[0], '02x'), TtbinFileRecordTag(tg[0]), format(pos, '02x')))

                if not self.ExtractRecord(activity, tg[0], ttbinfile):
                    print("   Tag: 0x%s Pos: 0x%s is not implemented. Exiting" \
                          % (format(tg[0], '02x'), format(pos, '02x')))
                    break

        activity.PostLoad()
        return activity

    # reads single record
    def ExtractRecord(self, activity: Activity, tag: int, file: BinaryIO):
        if tag == TtbinFileRecordTag.FileHeader.value:
            return self.ReadHeaderx20(activity, file)
        elif tag == TtbinFileRecordTag.Status.value:
            return self.ReadStatusx21(activity, file)
        elif tag == TtbinFileRecordTag.Gps.value:
            return self.ReadGpsx22(activity, file)
        elif tag == TtbinFileRecordTag.ExtendedGps.value:
            return self.ReadExtendedGpsx23(activity, file)
        elif tag == TtbinFileRecordTag.HeartRate.value:
            return self.ReadHeartRatex25(activity, file)
        elif tag == TtbinFileRecordTag.Summary.value:
            return self.ReadSummaryx27(activity, file)
        elif tag == TtbinFileRecordTag.TrainingSetup.value:
            return self.ReadTrainingSetupx2d(activity, file)
        elif tag == TtbinFileRecordTag.Lap.value:
            return self.ReadLapx2f(activity, file)
        elif tag == TtbinFileRecordTag.WaitGps.value:
            return self.ReadWaitGpsx30(activity, file)
        elif tag == TtbinFileRecordTag.Treadmill.value:
            return self.ReadTreadmillx32(activity, file)
        elif tag == TtbinFileRecordTag.x37.value:
            return self.Readx37(activity, file)
        elif tag == TtbinFileRecordTag.HeartRateRecovery.value:
            return self.ReadHeartRateRecoveryx3f(activity, file)
        elif tag == TtbinFileRecordTag.Gym.value:
            return self.ReadGymx41(activity, file)
        elif tag == TtbinFileRecordTag.Movement.value:
            return self.ReadMovementx42(activity, file)
        elif tag == TtbinFileRecordTag.RouteDescription1.value:
            return self.ReadRouteDescriptionx43(activity, file)
        elif tag == TtbinFileRecordTag.RouteDescription2.value:
            return self.ReadRouteDescriptionx44(activity, file)
        elif tag == TtbinFileRecordTag.Elevation.value:
            return self.ReadElevationx47(activity, file)
        elif tag == TtbinFileRecordTag.x48.value:
            return self.Readx48(activity, file)
        elif tag == TtbinFileRecordTag.Battery.value:
            return self.ReadBatteryLevelx49(activity, file)
        elif tag == TtbinFileRecordTag.FitnessPoints.value:
            return self.ReadFitnessPointsx4a(activity, file)
        elif tag == TtbinFileRecordTag.x4b.value:
            return self.Readx4b(activity, file)
        return False

    def ParseDate(self, secondsSince1970: int, includeOffset: int):
        sec = secondsSince1970
        if includeOffset:
            sec = sec - self.localTimeOffset
        date = datetime.datetime(year=1970, month=1, day=1, tzinfo=datetime.timezone.utc) + datetime.timedelta(days=0, seconds=sec)
        return date

    def ReadHeaderx20(self, activity: Activity, file: BinaryIO):
        headerDef = Struct("<s7shl16s80sllss")
        data = file.read(headerDef.size)
        if len(data) != headerDef.size:
            return False

        fVersion, fFirmwareVersion, fProductId, fStartTime, fSoftwareVersion, \
            fGpsFirmwareVersion, fWatchTime, fLocalTimeOffset, fReserved, fArrayLen \
            = headerDef.unpack(data)
        file.read(fArrayLen[0] * 3)

        self.localTimeOffset = fLocalTimeOffset
        activity.startTime = self.ParseDate(fStartTime, includeOffset=True)
        return True

    def ReadSomething(self, file: BinaryIO, dataLen: int):
        data = file.read(dataLen)
        return len(data) == dataLen

    def Readx48(self, activity: Activity, file: BinaryIO):
        return self.ReadSomething(file, dataLen=14)

    def ReadBatteryLevelx49(self, activity: Activity, file: BinaryIO):
        batteryDef = Struct("<s3s")
        data = file.read(batteryDef.size)
        if len(data) != batteryDef.size:
            return False

        fLevel, fUnknown = batteryDef.unpack(data)
        activity.LogBatteryLevel(fLevel[0])
        #print("      Battery level: %s %%" % fLevel[0])
        return True

    def ReadStatusx21(self, activity: Activity, file: BinaryIO):
        statusDef = Struct("<ssl")
        data = file.read(statusDef.size)
        if len(data) != statusDef.size:
            return False

        #fStatus, fActivityCode, fTime = statusDef.unpack(data)
        #print("      Status: %s" % fStatus[0])
        return True

    def ReadFitnessPointsx4a(self, activity: Activity, file: BinaryIO):
        pointsDef = Struct("<lhh")
        data = file.read(pointsDef.size)
        if len(data) != pointsDef.size:
            return False

        #fTime, fPoints1, fPoints2 = pointsDef.unpack(data)
        #print("      Fitness points: %s" % fPoints1)
        return True

    def Readx4b(self, activity: Activity, file: BinaryIO):
        x4bDef = Struct("<h")
        data = file.read(x4bDef.size)
        if len(data) != x4bDef.size:
            return False

        fTuple = x4bDef.unpack(data)
        return self.ReadSomething(file, fTuple[0])

    def ReadGymx41(self, activity: Activity, file: BinaryIO):
        gymDef = Struct("<lhl")
        data = file.read(gymDef.size)
        if len(data) != gymDef.size:
            return False

        fTime, fCalories, fSteps = gymDef.unpack(data)
        time = self.ParseDate(fTime, includeOffset=True)
        #print("      Calories: %s" % fCalories)
        activity.LogSteps(time, fSteps, distance=0)
        return True

    def ReadMovementx42(self, activity: Activity, file: BinaryIO):
        movementDef = Struct("<s")
        data = file.read(movementDef.size)
        if len(data) != movementDef.size:
            return False

        #fTuple = movementDef.unpack(data)
        #print("      Movement status: %s" % fTuple[0][0])
        return True

    def ReadHeartRatex25(self, activity: Activity, file: BinaryIO):
        heartRateDef = Struct("<ssl")
        data = file.read(heartRateDef.size)
        if len(data) != heartRateDef.size:
            return False

        fHeartRate, fExternal, fTime = heartRateDef.unpack(data)
        time = self.ParseDate(fTime, includeOffset=True)
        activity.LogHeartRate(time, fHeartRate[0])
        return True

    def ReadSummaryx27(self, activity: Activity, file: BinaryIO):
        summaryDef = Struct("<sflhhl")
        data = file.read(summaryDef.size)
        if len(data) != summaryDef.size:
            return False

        fActivityCode, fDistance, fDuration, fCalories, fUnknown, fDuration2 = summaryDef.unpack(data)
        activity.activityType = ActivityType(fActivityCode[0])
        activity.totalActiveSeconds = fDuration
        activity.totalElapsedSeconds = fDuration2
        activity.totalDistanceMeters = fDistance
        activity.totalCalories = fCalories
        return True

    def ReadTreadmillx32(self, activity: Activity, file: BinaryIO):
        treadmillDef = Struct("<lfhlh")
        data = file.read(treadmillDef.size)
        if len(data) != treadmillDef.size:
            return False

        fTime, fDistance, fCalories, fSteps, fStepLen = treadmillDef.unpack(data)
        time = self.ParseDate(fTime, includeOffset=True)
        activity.LogSteps(time, fSteps, fDistance)
        return True

    def ReadWaitGpsx30(self, activity: Activity, file: BinaryIO):
        waitGpsDef = Struct("<h")
        data = file.read(waitGpsDef.size)
        if len(data) != waitGpsDef.size:
            return False

        #fTuple = waitGpsDef.unpack(data)
        return True

    def ReadGpsx22(self, activity: Activity, file: BinaryIO):
        gpsDef = Struct("<llhhlhffs")
        data = file.read(gpsDef.size)
        if len(data) != gpsDef.size:
            return False

        fLatitude, fLongitude, fHeading, fSpeed, fTime, fCalories, \
            fFilteredSpeed, fDistance, fCycles = gpsDef.unpack(data)
        time = self.ParseDate(fTime, includeOffset=False)
        activity.LogGps(time, fLatitude / 10000000.0, fLongitude / 10000000.0, fFilteredSpeed, fCycles[0], fDistance)
        return True

    def ReadExtendedGpsx23(self, activity: Activity, file: BinaryIO):
        return self.ReadSomething(file, dataLen=23)

    def Readx37(self, activity: Activity, file: BinaryIO):
        return self.ReadSomething(file, dataLen=1)

    def ReadElevationx47(self, activity: Activity, file: BinaryIO):
        elevationDef = Struct("<shhhhh")
        data = file.read(elevationDef.size)
        if len(data) != elevationDef.size:
            return False

        fStatus, fAltitude, fElevation2, fAscend, fDescend, fUnknown = elevationDef.unpack(data)
        #print("      Elevation status: %s Elevation: %s" % (fStatus[0], fElevation1))
        if fAltitude != fUnknown:
            activity.LogElevation(fAltitude, fAscend, fDescend)
        return True

    def ReadRouteDescriptionx43(self, activity: Activity, file: BinaryIO):
        return self.ReadSomething(file, dataLen=14)

    def ReadRouteDescriptionx44(self, activity: Activity, file: BinaryIO):
        return self.ReadSomething(file, dataLen=100)
        
    def ReadHeartRateRecoveryx3f(self, activity: Activity, file: BinaryIO):
        recoveryDef = Struct("<ll")
        data = file.read(recoveryDef.size)
        if len(data) != recoveryDef.size:
            return False
        
        #fScore, fHeartRate = recoveryDef.unpack(data)
        return True

    def ReadTrainingSetupx2d(self, activity: Activity, file: BinaryIO):
        setupDef = Struct("<sff")
        data = file.read(setupDef.size)
        if len(data) != setupDef.size:
            return False

        fGoal, fMinimum, fMaximum = setupDef.unpack(data)
        return True

    def ReadLapx2f(self, activity: Activity, file: BinaryIO):
        lapDef = Struct("<lfh")
        data = file.read(lapDef.size)
        if len(data) != lapDef.size:
            return False

        fSeconds, fDistance, fCalories = lapDef.unpack(data)
        activity.LogLap(fSeconds, fDistance, fCalories)
        return True
