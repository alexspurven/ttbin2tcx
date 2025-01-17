import os
import xml.dom.minidom
from xml.dom.minidom import Element, Document, Node
from tcxdef import XmlTools, XmlElement


class TrackPointWrapper:

    def __init__(self, element: Element):
        self.trackPointElement = element
        self.distanceElement = None
        self.distanceMeters = 0

        for childNode in element.childNodes:
            if childNode.nodeName == XmlElement.DistanceMeters.name:
                self.distanceElement = childNode
                for childNode2 in childNode.childNodes:
                    if childNode2.nodeType == Element.TEXT_NODE:
                        self.distanceMeters = float(childNode2.data)
                        break
        return

    def CorrectDistance(self, factor: float):
        self.distanceMeters = round(self.distanceMeters * factor, 2)
        for childNode in self.distanceElement.childNodes:
            self.distanceElement.removeChild(childNode)
        self.distanceElement.appendChild(
            self.distanceElement.ownerDocument.createTextNode(XmlTools.FormatFloat(self.distanceMeters)))
        return


class TcxFileEditor:

    def __init__(self):
        self.doc = None
        return

    def LoadXml(self, fileTcx):
        print("Loading %s" % fileTcx)
        self.doc = xml.dom.minidom.parse(fileTcx)
        return

    def SaveXml(self, fileTcx):
        if os.path.isfile(fileTcx):
            os.remove(fileTcx)
        print("Saving %s" % fileTcx)

        with open(fileTcx, 'wb') as outfile:
            outfile.write(self.doc.toprettyxml(encoding="utf-8", indent=" ", newl=" "))
            outfile.flush()
        return

    def ChangeLength(self, newLen: float):
        if newLen <= 0.0:
            print("Error: new distance should be greater than zero")
            return

        # change in track points
        trackPoints = list()
        for trackPointElement in self.doc.getElementsByTagName(XmlElement.Trackpoint.name):
            trackPoint = TrackPointWrapper(trackPointElement)
            trackPoints.append(trackPoint)

        oldLen: float = 0
        for trackPoint in trackPoints:
            if trackPoint.distanceMeters > oldLen:
                oldLen = trackPoint.distanceMeters

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

        return
