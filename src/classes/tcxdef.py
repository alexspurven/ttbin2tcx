import datetime
from enum import Enum, auto
from .activity import ActivityType


class XmlNamespace(Enum):
    x = auto()
    xmlns = auto()
    xsi = auto()


class XmlElement(Enum):
    ActiveSeconds = auto()
    Activities = auto()
    Activity = auto()
    AltitudeMeters = auto()
    Author = auto()
    AverageHeartRateBpm = auto()
    AvgSpeed = auto()
    Cadence = auto()
    Calories = auto()
    ClimbMeters = auto()
    Creator = auto()
    DistanceMeters = auto()
    ElapsedSeconds = auto()
    Extensions = auto()
    HeartRateBpm = auto()
    Id = auto()
    Intensity = auto()
    KiloCalories = auto()
    LangID = auto()
    LatitudeDegrees = auto()
    LongitudeDegrees = auto()
    LX = auto()
    Lap = auto()
    MaximumHeartRateBpm = auto()
    MaximumSpeed = auto()
    Name = auto()
    Position = auto()
    RunCadence = auto()
    Speed = auto()
    StepCount = auto()
    Time = auto()
    TotalTimeSeconds = auto()
    TPX = auto()
    Track = auto()
    Trackpoint = auto()
    TrainingCenterDatabase = auto()
    TriggerMethod = auto()
    Value = auto()


class XmlAttribute(Enum):
    Sport = auto()
    StartTime = auto()
    schemaLocation = auto()
    type = auto()
    x = auto()
    xmlns = auto()
    xsi = auto()


class XmlConstant:
    DeviceName: str = "TomTom Adventurer"
    Intensity: str = "Active"
    LangID: str = "en"
    TriggerMethod: str = "Manual"
    xmlns: str = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2"
    xmlns_x: str = "http://www.garmin.com/xmlschemas/ActivityExtension/v2"
    xmlns_xsi: str = "http://www.w3.org/2001/XMLSchema-instance"
    xsi_schemaLocation: str = "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2 http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd"
    xsi_device_type: str = "Device_t"
    xsi_extensions_type: str = "Extensions_t"
    xsi_app_type: str = "Application_t"


class XmlTools:
    def AddNamespace(namespace: str, attribute: str):
        ret = format("%s:%s" % (namespace, attribute))
        return ret

    def FormatDate(dt: datetime):
        return  dt.isoformat("T", "seconds").replace("+00:00", "Z")

    def ISOStrToDate(s: str):
        return datetime.datetime.fromisoformat(s)

    def FormatFloat(f: float):
        return '%.2f' % f

    def FormatSport(activityType: ActivityType):
        if activityType == ActivityType.Running or activityType == ActivityType.Treadmill:
            return "Running"
        elif activityType == ActivityType.Cycling or activityType == ActivityType.IndoorCycling:
            return "Biking"
        else:
            return "Other"
