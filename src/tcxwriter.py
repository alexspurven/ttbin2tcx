import datetime
import os
from enum import Enum, auto
from activity import Activity, TrackPoint, ActivityType
from xml.dom.minidom import getDOMImplementation, Element, Document


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

class TcxFileWriter:
    def __init__(self):
        return

    def SaveActivity(self, fileTcx: str, activity: Activity):
        if os.path.isfile(fileTcx):
            os.remove(fileTcx)
        print("Saving %s" % fileTcx)

        doc, trackElement, activityElement, roolElement = self.CreateXml(activity)
        self.AddTrackPoints(doc, trackElement, activity)
        self.AddSummary(doc, roolElement, activityElement, activity)

        with open(fileTcx, 'wb') as outfile:
            outfile.write(doc.toprettyxml(encoding="utf-8", indent=" "))
            outfile.flush()

    def AddNamespace(self, namespace: str, attribute: str):
        ret = format("%s:%s" % (namespace, attribute))
        return ret

    def FormatDate(self, dt: datetime):
        return  dt.isoformat("T", "seconds").replace("+00:00", "Z")

    def FormatFloat(self, f: float):
        return '%.2f' % f

    def FormatSport(self, activityType: ActivityType):
        if activityType == ActivityType.Running or activityType == ActivityType.Treadmill:
            return "Running"
        elif activityType == ActivityType.Cycling or activityType == ActivityType.IndoorCycling:
            return "Biking"
        else:
            return "Other"

    def CreateXml(self, activity: Activity):
        impl = getDOMImplementation()
        doc = impl.createDocument(namespaceURI=None, qualifiedName=XmlElement.TrainingCenterDatabase.name, doctype=None)
        roolElement = doc.documentElement
        roolElement.setAttribute(XmlAttribute.xmlns.name, XmlConstant.xmlns)
        roolElement.setAttribute(self.AddNamespace(XmlNamespace.xmlns.name, XmlAttribute.xsi.name),
                                 XmlConstant.xmlns_xsi)
        roolElement.setAttribute(self.AddNamespace(XmlNamespace.xmlns.name, XmlAttribute.x.name), XmlConstant.xmlns_x)
        roolElement.setAttribute(self.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.schemaLocation.name),
                                 XmlConstant.xsi_schemaLocation)

        activitiesElement = doc.createElement(XmlElement.Activities.name)
        roolElement.appendChild(activitiesElement)

        activityElement = doc.createElement(XmlElement.Activity.name)
        activityElement.setAttribute(XmlAttribute.Sport.name, self.FormatSport(activity.activityType))
        activitiesElement.appendChild(activityElement)

        idElement = doc.createElement(XmlElement.Id.name)
        idElement.appendChild(doc.createTextNode(self.FormatDate(activity.startTime)))
        activityElement.appendChild(idElement)

        lapElement = doc.createElement(XmlElement.Lap.name)
        lapElement.setAttribute(XmlAttribute.StartTime.name, self.FormatDate(activity.startTime))
        activityElement.appendChild(lapElement)

        totalTimeElement = doc.createElement(XmlElement.TotalTimeSeconds.name)
        totalTimeElement.appendChild(doc.createTextNode(str(activity.totalActiveSeconds)))
        lapElement.appendChild(totalTimeElement)

        distanceElement = doc.createElement(XmlElement.DistanceMeters.name)
        distanceElement.appendChild(doc.createTextNode(self.FormatFloat(activity.totalDistanceMeters)))
        lapElement.appendChild(distanceElement)

        if activity.maxSpeed > 0:
            maxSpeedElement = doc.createElement(XmlElement.MaximumSpeed.name)
            maxSpeedElement.appendChild(doc.createTextNode(self.FormatFloat(activity.maxSpeed)))
            lapElement.appendChild(maxSpeedElement)

        caloriesElement = doc.createElement(XmlElement.Calories.name)
        caloriesElement.appendChild(doc.createTextNode(str(activity.totalCalories)))
        lapElement.appendChild(caloriesElement)

        avgHeartRateElement = doc.createElement(XmlElement.AverageHeartRateBpm.name)
        lapElement.appendChild(avgHeartRateElement)

        valueElement = doc.createElement(XmlElement.Value.name)
        valueElement.appendChild(doc.createTextNode(self.FormatFloat(activity.avgHeartRate)))
        avgHeartRateElement.appendChild(valueElement)

        maxHeartRateElement = doc.createElement(XmlElement.MaximumHeartRateBpm.name)
        lapElement.appendChild(maxHeartRateElement)

        valueElement = doc.createElement(XmlElement.Value.name)
        valueElement.appendChild(doc.createTextNode(str(activity.maxHeartRate)))
        maxHeartRateElement.appendChild(valueElement)

        intensityElement = doc.createElement(XmlElement.Intensity.name)
        intensityElement.appendChild(doc.createTextNode(XmlConstant.Intensity))
        lapElement.appendChild(intensityElement)

        triggerElement = doc.createElement(XmlElement.TriggerMethod.name)
        triggerElement.appendChild(doc.createTextNode(XmlConstant.TriggerMethod))
        lapElement.appendChild(triggerElement)

        trackElement = doc.createElement(XmlElement.Track.name)
        lapElement.appendChild(trackElement)

        return doc, trackElement, activityElement, roolElement

    def AddTrackPoints(self, doc: Document, trackElement: Element, activity: Activity):
        for time in activity.trackPoints:
            point: TrackPoint = activity.trackPoints[time]
            pointElement = doc.createElement(XmlElement.Trackpoint.name)
            trackElement.appendChild(pointElement)

            timeElement = doc.createElement(XmlElement.Time.name)
            timeElement.appendChild(doc.createTextNode(self.FormatDate(point.time)))
            pointElement.appendChild(timeElement)

            if point.longitudeDegrees != 0 or point.latitudeDegrees != 0:
                positionElement = doc.createElement(XmlElement.Position.name)
                pointElement.appendChild(positionElement)

                latitudeElement = doc.createElement(XmlElement.LatitudeDegrees.name)
                latitudeElement.appendChild(doc.createTextNode(str(point.latitudeDegrees)))
                positionElement.appendChild(latitudeElement)

                longitudeElement = doc.createElement(XmlElement.LongitudeDegrees.name)
                longitudeElement.appendChild(doc.createTextNode(str(point.longitudeDegrees)))
                positionElement.appendChild(longitudeElement)

            if point.altitudeMeters != 0:
                altitudeElement = doc.createElement(XmlElement.AltitudeMeters.name)
                altitudeElement.appendChild(doc.createTextNode(self.FormatFloat(point.altitudeMeters)))
                pointElement.appendChild(altitudeElement)

            distanceElement = doc.createElement(XmlElement.DistanceMeters.name)
            distanceElement.appendChild(doc.createTextNode(self.FormatFloat(point.distanceMeters)))
            pointElement.appendChild(distanceElement)

            if point.heartRate > 0:
                heartRateElement = doc.createElement(XmlElement.HeartRateBpm.name)
                pointElement.appendChild(heartRateElement)

                valueElement = doc.createElement(XmlElement.Value.name)
                valueElement.appendChild(doc.createTextNode(str(point.heartRate)))
                heartRateElement.appendChild(valueElement)

            if point.speed > 0 or point.cadence > 0:
                extensionsElement = doc.createElement(XmlElement.Extensions.name)
                pointElement.appendChild(extensionsElement)

                tpxElement = doc.createElement(self.AddNamespace(XmlNamespace.x.name, XmlElement.TPX.name))
                extensionsElement.appendChild(tpxElement)

                if point.speed > 0:
                    speedElement = doc.createElement(self.AddNamespace(XmlNamespace.x.name, XmlElement.Speed.name))
                    speedElement.appendChild(doc.createTextNode(self.FormatFloat(point.speed)))
                    tpxElement.appendChild(speedElement)

                if point.cadence > 0:
                    cadenceElement = doc.createElement(self.AddNamespace(XmlNamespace.x.name, XmlElement.RunCadence.name))
                    cadenceElement.appendChild(doc.createTextNode(str(point.cadence)))
                    tpxElement.appendChild(cadenceElement)

            if point.cadence > 0:
                cadenceElement = doc.createElement(XmlElement.Cadence.name)
                cadenceElement.appendChild(doc.createTextNode(str(point.cadence)))
                pointElement.appendChild(cadenceElement)

    def AddSummary(self, doc: Document, roolElement: Element, activityElement: Element, activity: Activity):
        creatorElement = doc.createElement(XmlElement.Creator.name)
        creatorElement.setAttribute(self.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.type.name),
                      XmlConstant.xsi_device_type)
        activityElement.appendChild(creatorElement)

        nameElement = doc.createElement(XmlElement.Name.name)
        nameElement.appendChild(doc.createTextNode(XmlConstant.DeviceName))
        creatorElement.appendChild(nameElement)

        extensionsElement = doc.createElement(XmlElement.Extensions.name)
        extensionsElement.setAttribute(self.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.type.name),
                      XmlConstant.xsi_extensions_type)
        activityElement.appendChild(extensionsElement)

        xElement = doc.createElement(self.AddNamespace(XmlNamespace.x.name, XmlElement.LX.name))
        extensionsElement.appendChild(xElement)

        activeSecondsElement = doc.createElement(XmlElement.ActiveSeconds.name)
        activeSecondsElement.appendChild(doc.createTextNode(str(activity.totalActiveSeconds)))
        xElement.appendChild(activeSecondsElement)

        elapsedSecondsElement = doc.createElement(XmlElement.ElapsedSeconds.name)
        elapsedSecondsElement.appendChild(doc.createTextNode(str(activity.totalElapsedSeconds)))
        xElement.appendChild(elapsedSecondsElement)

        distanceElement = doc.createElement(XmlElement.DistanceMeters.name)
        distanceElement.appendChild(doc.createTextNode(self.FormatFloat(activity.totalDistanceMeters)))
        xElement.appendChild(distanceElement)

        avgSpeedElement = doc.createElement(XmlElement.AvgSpeed.name)
        avgSpeedElement.appendChild(doc.createTextNode(self.FormatFloat(activity.avgSpeed)))
        xElement.appendChild(avgSpeedElement)

        caloriesElement = doc.createElement(XmlElement.KiloCalories.name)
        caloriesElement.appendChild(doc.createTextNode(str(activity.totalCalories)))
        xElement.appendChild(caloriesElement)

        stepsElement = doc.createElement(XmlElement.StepCount.name)
        stepsElement.appendChild(doc.createTextNode(str(activity.totalSteps)))
        xElement.appendChild(stepsElement)

        if activity.totalAscendMeters > 0:
            climbElement = doc.createElement(XmlElement.ClimbMeters.name)
            climbElement.appendChild(doc.createTextNode(str(activity.totalAscendMeters)))
            xElement.appendChild(climbElement)

        authorElement = doc.createElement(XmlElement.Author.name)
        authorElement.setAttribute(self.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.type.name),
                                       XmlConstant.xsi_app_type)
        roolElement.appendChild(authorElement)

        nameElement = doc.createElement(XmlElement.Name.name)
        nameElement.appendChild(doc.createTextNode(XmlConstant.DeviceName))
        authorElement.appendChild(nameElement)

        landElement = doc.createElement(XmlElement.LangID.name)
        landElement.appendChild(doc.createTextNode(XmlConstant.LangID))
        authorElement.appendChild(landElement)

