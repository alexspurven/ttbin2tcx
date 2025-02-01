import os
import re
import datetime
import xml.dom.minidom
from enum import Enum, auto
from xml.dom.minidom import Element
from .tcxdef import XmlTools, XmlElement, XmlAttribute, XmlNamespace


class IntervalDef(Enum):
    l = auto()
    m = auto()
    s = auto()


class TrackPointWrapper:
    def __init__(self, element: Element):
        self.trackPointElement = element
        self.distanceElement = None
        self.distanceMeters = 0
        self.timeElement = None
        self.time = datetime.datetime.now(datetime.timezone.utc)

        for childNode in element.childNodes:
            if childNode.nodeName == XmlElement.DistanceMeters.name:
                self.distanceElement = childNode
                for childNode2 in childNode.childNodes:
                    if childNode2.nodeType == Element.TEXT_NODE:
                        self.distanceMeters = float(childNode2.data)
                        break
                break

        for childNode in element.childNodes:
            if childNode.nodeName == XmlElement.Time.name:
                self.timeElement = childNode
                for childNode2 in childNode.childNodes:
                    if childNode2.nodeType == Element.TEXT_NODE:
                        self.time = XmlTools.ISOStrToDate(childNode2.data)
                        break
                break
        return

    def CorrectDistance(self, factor: float):
        self.distanceMeters = round(self.distanceMeters * factor, 2)
        for childNode in self.distanceElement.childNodes:
            self.distanceElement.removeChild(childNode)
        self.distanceElement.appendChild(
            self.distanceElement.ownerDocument.createTextNode(XmlTools.FormatFloat(self.distanceMeters)))
        self.RemoveSpeedNode()
        return

    def SetDistance(self, distance: float):
        self.distanceMeters = round(distance, 4)
        self.CorrectDistance(1.0)
        return

    def RemoveSpeedNode(self):
        for childNode in self.trackPointElement.childNodes:
            if childNode.nodeName == XmlElement.Extensions.name:
                for childNode2 in childNode.childNodes:
                    if childNode2.nodeName == XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.TPX.name):
                        for childNode3 in childNode2.childNodes:
                            if childNode3.nodeName == XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.Speed.name):
                                childNode2.removeChild(childNode3)
                                break
                        break
                break
        return

    def AddSpeedNode(self, speed: float):
        extensionNode = None
        tpxNode = None
        speedNode = None
        for childNode in self.trackPointElement.childNodes:
            if childNode.nodeName == XmlElement.Extensions.name:
                extensionNode = childNode
                for childNode2 in childNode.childNodes:
                    if childNode2.nodeName == XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.TPX.name):
                        tpxNode = childNode2
                        for childNode3 in childNode2.childNodes:
                            if childNode3.nodeName == XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.Speed.name):
                                speedNode = childNode3
                                break
                        break
                break

        if extensionNode is None:
            extensionNode = self.trackPointElement.ownerDocument.createElement(XmlElement.Extensions.name)
            self.trackPointElement.appendChild(extensionNode)
        if tpxNode is None:
            tpxNode = self.trackPointElement.ownerDocument.createElement(
                XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.TPX.name))
            extensionNode.appendChild(tpxNode)
        if speedNode is None:
            speedNode = self.trackPointElement.ownerDocument.createElement(
                XmlTools.AddNamespace(XmlNamespace.x.name, XmlElement.Speed.name))
            tpxNode.appendChild(speedNode)

        for childNode in speedNode.childNodes:
            speedNode.removeChild(childNode)
        speedNode.appendChild(
            self.trackPointElement.ownerDocument.createTextNode(XmlTools.FormatFloat(speed / 3.6)))

        return

    def GetLapElement(self):
        return self.trackPointElement.parentNode.parentNode


class Interval:
    def __init__(self, interval: str, startTime: datetime):
        self.seconds = 0.0
        self.speed = 0.0
        self.meters = 0.0
        self.interval = interval
        self.hasData = False

        matches = re.findall(r"([\d.]+)([ms])([\d.]+)", interval.strip())
        if len(matches) == 0:
            return
        match = matches[0]
        if len(match) != 3:
            return

        self.speed = float(match[2])
        if match[1] == IntervalDef.m.name:
            self.meters = float(match[0])
            if self.speed != 0:
                self.seconds = self.meters * 3.6 / self.speed
        else:
            self.seconds = float(match[0])
            self.meters = self.seconds * self.speed / 3.6

        if self.speed == 0:
            self.meters = 0.0  # can't make a distance by standing
        if self.meters == 0:
            self.speed = 0.0   # no distance => no speed

        self.startTime = startTime
        self.endTime = startTime + datetime.timedelta(seconds=self.seconds)
        self.hasData = True
        return

    def WithinInterval(self, time: datetime):
        return time >= self.startTime and time <= self.endTime

class TcxFileEditor:
    def __init__(self):
        self.doc = None
        return

    def LoadXml(self, fileTcx):
        print("Loading %s" % fileTcx)
        self.doc = xml.dom.minidom.parse(fileTcx)
        self.CleanEmptyTextNodes(self.doc.childNodes[0])
        return

    def CleanEmptyTextNodes(self, node: Element):
        remove_list = []
        for child in node.childNodes:
            if child.nodeType == Element.TEXT_NODE and not child.data.strip():
                remove_list.append(child)
            elif child.hasChildNodes():
                self.CleanEmptyTextNodes(child)
        for node in remove_list:
            node.parentNode.removeChild(node)
        return

    def SaveXml(self, fileTcx):
        if os.path.isfile(fileTcx):
            os.remove(fileTcx)
        print("Saving %s" % fileTcx)

        with open(fileTcx, 'wb') as outfile:
            outfile.write(self.doc.toprettyxml(encoding="utf-8", indent=" "))
            outfile.flush()
        return

    def ChangeLength(self, newLen: float):
        if newLen <= 0.0:
            print("Error: new distance should be greater than zero")
            return False

        # change in track points
        trackPoints = self.ExtractTrackPoints()
        oldLen = self.GetFullDistance(trackPoints)

        print("Old distance: %s m" % oldLen)
        print("New distance: %s m" % newLen)

        factor: float = newLen / oldLen
        for trackPoint in trackPoints:
            trackPoint.CorrectDistance(factor)

        # change in other places
        for distanceElements in self.doc.getElementsByTagName(XmlElement.DistanceMeters.name):
            if distanceElements.parentNode.tagName != XmlElement.Trackpoint.name:
                otherPoint = TrackPointWrapper(distanceElements.parentNode)
                otherPoint.CorrectDistance(factor)

        return True

    def ExtractTrackPoints(self):
        trackPoints = list()
        for trackPointElement in self.doc.getElementsByTagName(XmlElement.Trackpoint.name):
            trackPoint = TrackPointWrapper(trackPointElement)
            trackPoints.append(trackPoint)
        return trackPoints

    def ParseIntervals(self, intervals: str, startTime: datetime):
        if len(intervals) == 0:
            print("Wrong interval parameter %s" % intervals)
            return list()
        if intervals[0] == IntervalDef.l.name: # laps mode
            return self.ParseLapIntervals(intervals);

        intervalList = intervals.split(";")
        intervalObjects = list()
        intervalStartTime = startTime
        for intervalStr in intervalList:
            intervalObject = Interval(intervalStr, intervalStartTime)
            if intervalObject.hasData == True:
                intervalObjects.append(intervalObject)
                intervalStartTime = intervalObject.endTime + datetime.timedelta(seconds=1)
            else:
                print("Can't parse interval %s" % intervalStr)
        return intervalObjects

    def ParseLapIntervals(self, intervals: str):
        intervalList = intervals.removeprefix(IntervalDef.l.name).split(";")
        intervalObjects = list()
        i = 0
        for lapElement in self.doc.getElementsByTagName(XmlElement.Lap.name):
            timeStr = lapElement.getAttribute(XmlAttribute.StartTime.name)
            lapStartTime = XmlTools.ISOStrToDate(timeStr)
            for childNode in lapElement.childNodes:
                if childNode.nodeName == XmlElement.TotalTimeSeconds.name:
                    for childNode2 in childNode.childNodes:
                        if childNode2.nodeType == Element.TEXT_NODE:
                            lapSeconds = int(childNode2.data)
                            intervalStr = "%ss%s" % (lapSeconds, intervalList[i])
                            intervalObject = Interval(intervalStr, lapStartTime)
                            intervalObjects.append(intervalObject)
                            break
                    break

            i = i + 1
            if i >= len(intervalList):
                break
        return intervalObjects

    def GetActivityStartTime(self):
        startTime = None
        for lapElement in self.doc.getElementsByTagName(XmlElement.Lap.name):
            timeStr = lapElement.getAttribute(XmlAttribute.StartTime.name)
            time = XmlTools.ISOStrToDate(timeStr)
            if startTime is None or time < startTime:
                startTime = time
        return startTime

    def GetIntervalForTime(self, intervalList: list, time: datetime):
        for interval in intervalList:
            if interval.WithinInterval(time):
                return interval
        return None

    def GetFullDistance(self, trackPoints: list):
        oldLen = 0.0
        for trackPoint in trackPoints:
            if trackPoint.distanceMeters > oldLen:
                oldLen = trackPoint.distanceMeters
        return oldLen

    def CalculateDistanceByLap(self, trackPoints: list):
        lapsElements = dict()
        for trackPoint in trackPoints:
            lapElement = trackPoint.GetLapElement()
            if lapElement not in lapsElements:
                lapsElements[lapElement] = list()
            lapsElements[lapElement].append(trackPoint)

        for lapElement in lapsElements:
            minDistance = None
            maxDistance = None
            for trackPoint in lapsElements[lapElement]:
                if minDistance is None or trackPoint.distanceMeters < minDistance:
                    minDistance = trackPoint.distanceMeters
                if maxDistance is None or trackPoint.distanceMeters > maxDistance:
                    maxDistance = trackPoint.distanceMeters
            lapDistance = 0.0
            if minDistance is not None and maxDistance is not None:
                lapDistance = maxDistance - minDistance
            lapPoint = TrackPointWrapper(lapElement) # to set DistanceMeters
            lapPoint.SetDistance(lapDistance)

        return

    def ChangeSpeed(self, intervals: str):
        startTime = self.GetActivityStartTime()
        intervalList = self.ParseIntervals(intervals, startTime)
        if len(intervalList) == 0:
            print("Wrong interval definition")
            return False

        trackPoints = self.ExtractTrackPoints()
        oldLen = self.GetFullDistance(trackPoints)
        trackPointsByTime = dict() # key - time, value - trackPoint
        for trackPoint in trackPoints:
            trackPointsByTime[trackPoint.time] = trackPoint
        trackPointsTime = sorted(trackPointsByTime)

        currentDistance = 0.0
        currentTime = startTime
        currentSpeed = 0.0
        smoothFirstPoints = smoothRest = 5
        for trackPointTime in trackPointsTime:
            trackPoint = trackPointsByTime[trackPointTime]
            interval = self.GetIntervalForTime(intervalList, trackPointTime)
            if interval is not None:
                currentSpeed = interval.speed
            timeFromPrev = (trackPointTime - currentTime).total_seconds()
            if smoothRest > 0: # smooth start
                currentSpeed = currentSpeed * (1 - smoothRest / smoothFirstPoints)
                smoothRest = smoothRest - 1
            currentDistance = currentDistance + timeFromPrev * currentSpeed / 3.6
            currentTime = trackPointTime
            trackPoint.SetDistance(currentDistance)
            # doesn't make any difference # trackPoint.AddSpeedNode(currentSpeed)

        newLen = self.GetFullDistance(trackPoints)

        print("Original distance: %s m" % oldLen)
        print("Calculated distance: %s m. Changing back" % newLen)

        factor: float = oldLen / newLen
        for trackPoint in trackPoints:
            trackPoint.CorrectDistance(factor)

        self.CalculateDistanceByLap(trackPoints)

        return True

