import os
from activity import Activity, TrackPoint, Lap
from xml.dom.minidom import getDOMImplementation, Element, Document
from tcxdef import XmlElement, XmlAttribute, XmlConstant, XmlNamespace, XmlTools


class TcxFileWriter:
    def __init__(self):
        return

    def SaveActivity(self, fileTcx: str, activity: Activity):
        if os.path.isfile(fileTcx):
            os.remove(fileTcx)
        print("Saving %s" % fileTcx)

        doc = self.CreateXml(activity)

        with open(fileTcx, 'wb') as outfile:
            outfile.write(doc.toprettyxml(encoding="utf-8", indent=" "))
            outfile.flush()

    def CreateXml(self, activity: Activity):
        impl = getDOMImplementation()
        doc = impl.createDocument(namespaceURI=None, qualifiedName=XmlElement.TrainingCenterDatabase.name, doctype=None)
        roolElement = doc.documentElement
        roolElement.setAttribute(XmlAttribute.xmlns.name, XmlConstant.xmlns)
        roolElement.setAttribute(XmlTools.AddNamespace(XmlNamespace.xmlns.name, XmlAttribute.xsi.name),
                                 XmlConstant.xmlns_xsi)
        roolElement.setAttribute(XmlTools.AddNamespace(XmlNamespace.xmlns.name, XmlAttribute.x.name), XmlConstant.xmlns_x)
        roolElement.setAttribute(XmlTools.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.schemaLocation.name),
                                 XmlConstant.xsi_schemaLocation)

        activitiesElement = doc.createElement(XmlElement.Activities.name)
        roolElement.appendChild(activitiesElement)

        activityElement = doc.createElement(XmlElement.Activity.name)
        activityElement.setAttribute(XmlAttribute.Sport.name, XmlTools.FormatSport(activity.activityType))
        activitiesElement.appendChild(activityElement)

        idElement = doc.createElement(XmlElement.Id.name)
        idElement.appendChild(doc.createTextNode(XmlTools.FormatDate(activity.startTime)))
        activityElement.appendChild(idElement)

        currentLapIndex: int = 0
        isDefaultLap: bool = len(activity.laps) == 1
        for lap in activity.laps:
            trackElement = self.AddLap(doc, activityElement, lap, isDefaultLap, activity)
            self.AddTrackPoints(doc, trackElement, currentLapIndex, activity)
            currentLapIndex = currentLapIndex + 1

        self.AddSummary(doc, roolElement, activityElement, activity)

        return doc

    def AddLap(self, doc: Document, activityElement: Element, lap: Lap, isDefaultLap: bool, activity: Activity):
        lapElement = doc.createElement(XmlElement.Lap.name)
        lapElement.setAttribute(XmlAttribute.StartTime.name, XmlTools.FormatDate(lap.startTime))
        activityElement.appendChild(lapElement)

        totalTimeElement = doc.createElement(XmlElement.TotalTimeSeconds.name)
        totalTimeElement.appendChild(doc.createTextNode(str(lap.seconds)))
        lapElement.appendChild(totalTimeElement)

        distanceElement = doc.createElement(XmlElement.DistanceMeters.name)
        distanceElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(lap.distance)))
        lapElement.appendChild(distanceElement)

        caloriesElement = doc.createElement(XmlElement.Calories.name)
        caloriesElement.appendChild(doc.createTextNode(str(lap.calories)))
        lapElement.appendChild(caloriesElement)

        intensityElement = doc.createElement(XmlElement.Intensity.name)
        intensityElement.appendChild(doc.createTextNode(XmlConstant.Intensity))
        lapElement.appendChild(intensityElement)

        triggerElement = doc.createElement(XmlElement.TriggerMethod.name)
        triggerElement.appendChild(doc.createTextNode(XmlConstant.TriggerMethod))
        lapElement.appendChild(triggerElement)

        if isDefaultLap:
            if activity.maxSpeed > 0:
                maxSpeedElement = doc.createElement(XmlElement.MaximumSpeed.name)
                maxSpeedElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(activity.maxSpeed)))
                lapElement.appendChild(maxSpeedElement)

            avgHeartRateElement = doc.createElement(XmlElement.AverageHeartRateBpm.name)
            lapElement.appendChild(avgHeartRateElement)

            valueElement = doc.createElement(XmlElement.Value.name)
            valueElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(activity.avgHeartRate)))
            avgHeartRateElement.appendChild(valueElement)

            maxHeartRateElement = doc.createElement(XmlElement.MaximumHeartRateBpm.name)
            lapElement.appendChild(maxHeartRateElement)

            valueElement = doc.createElement(XmlElement.Value.name)
            valueElement.appendChild(doc.createTextNode(str(activity.maxHeartRate)))
            maxHeartRateElement.appendChild(valueElement)

        trackElement = doc.createElement(XmlElement.Track.name)
        lapElement.appendChild(trackElement)

        return trackElement

    def SortPointsFunc(self, point: TrackPoint):
        return point.time

    def AddTrackPoints(self, doc: Document, trackElement: Element, lapIndex: int, activity: Activity):
        lapTrackPoints = list()
        for time in activity.trackPoints:
            point: TrackPoint = activity.trackPoints[time]
            if point.lapIndex == lapIndex:
                lapTrackPoints.append(point)
        lapTrackPoints.sort(key=self.SortPointsFunc)

        for point in lapTrackPoints:
            pointElement = doc.createElement(XmlElement.Trackpoint.name)
            trackElement.appendChild(pointElement)

            timeElement = doc.createElement(XmlElement.Time.name)
            timeElement.appendChild(doc.createTextNode(XmlTools.FormatDate(point.time)))
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
                altitudeElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(point.altitudeMeters)))
                pointElement.appendChild(altitudeElement)

            distanceElement = doc.createElement(XmlElement.DistanceMeters.name)
            distanceElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(point.distanceMeters)))
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

                tpxElement = doc.createElement(XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.TPX.name))
                extensionsElement.appendChild(tpxElement)

                if point.speed > 0:
                    speedElement = doc.createElement(XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.Speed.name))
                    speedElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(point.speed)))
                    tpxElement.appendChild(speedElement)

                if point.cadence > 0:
                    cadenceElement = doc.createElement(XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.RunCadence.name))
                    cadenceElement.appendChild(doc.createTextNode(str(point.cadence)))
                    tpxElement.appendChild(cadenceElement)

            if point.cadence > 0:
                cadenceElement = doc.createElement(XmlElement.Cadence.name)
                cadenceElement.appendChild(doc.createTextNode(str(point.cadence)))
                pointElement.appendChild(cadenceElement)

    def AddSummary(self, doc: Document, roolElement: Element, activityElement: Element, activity: Activity):
        creatorElement = doc.createElement(XmlElement.Creator.name)
        creatorElement.setAttribute(XmlTools.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.type.name),
                      XmlConstant.xsi_device_type)
        activityElement.appendChild(creatorElement)

        nameElement = doc.createElement(XmlElement.Name.name)
        nameElement.appendChild(doc.createTextNode(XmlConstant.DeviceName))
        creatorElement.appendChild(nameElement)

        extensionsElement = doc.createElement(XmlElement.Extensions.name)
        extensionsElement.setAttribute(XmlTools.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.type.name),
                      XmlConstant.xsi_extensions_type)
        activityElement.appendChild(extensionsElement)

        xElement = doc.createElement(XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.LX.name))
        extensionsElement.appendChild(xElement)

        activeSecondsElement = doc.createElement(XmlElement.ActiveSeconds.name)
        activeSecondsElement.appendChild(doc.createTextNode(str(activity.totalActiveSeconds)))
        xElement.appendChild(activeSecondsElement)

        elapsedSecondsElement = doc.createElement(XmlElement.ElapsedSeconds.name)
        elapsedSecondsElement.appendChild(doc.createTextNode(str(activity.totalElapsedSeconds)))
        xElement.appendChild(elapsedSecondsElement)

        distanceElement = doc.createElement(XmlElement.DistanceMeters.name)
        distanceElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(activity.totalDistanceMeters)))
        xElement.appendChild(distanceElement)

        avgSpeedElement = doc.createElement(XmlElement.AvgSpeed.name)
        avgSpeedElement.appendChild(doc.createTextNode(XmlTools.FormatFloat(activity.avgSpeed)))
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
        authorElement.setAttribute(XmlTools.AddNamespace(XmlNamespace.xsi.name, XmlAttribute.type.name),
                                       XmlConstant.xsi_app_type)
        roolElement.appendChild(authorElement)

        nameElement = doc.createElement(XmlElement.Name.name)
        nameElement.appendChild(doc.createTextNode(XmlConstant.DeviceName))
        authorElement.appendChild(nameElement)

        landElement = doc.createElement(XmlElement.LangID.name)
        landElement.appendChild(doc.createTextNode(XmlConstant.LangID))
        authorElement.appendChild(landElement)
