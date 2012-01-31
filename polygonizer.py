"""
/***************************************************************************
Polygonizer
A QGIS plugin
Creates polygons from intersecting lines
                             -------------------
begin                : 2011-01-20 
copyright            : (C) 2011 by Piotr Pociask
email                : p0cisk (at) o2 pl 
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import * 
from PyQt4.QtGui import *
from qgis.core import *
# Initialize Qt resources from file resources.py
import resources
#form
from PolygonizerDialog import PolygonizerDialog

import shapely
from shapely.ops import polygonize

class Polygonizer: 

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

  def initGui(self):  
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/polygonizer/icon.png"), \
        "Polygonizer", self.iface.mainWindow())
    # connect the action to the run method
    QObject.connect(self.action, SIGNAL("triggered()"), self.run) 

    # Add toolbar button and menu item
    self.iface.addToolBarIcon(self.action)
    self.iface.addPluginToMenu("&Polygonizer", self.action)

  def unload(self):
    # Remove the plugin menu item and icon
    self.iface.removePluginMenu("&Polygonizer",self.action)
    self.iface.removeToolBarIcon(self.action)

  # run method that performs all the real work
  def run(self):

    dlg = PolygonizerDialog(self.iface) 
    # show the dialog
    dlg.show()
    result = dlg.exec_() 
    # See if OK was pressed
    if result == 1: 
      # do something useful (delete the line containing pass and
      # substitute with your code
      pass 

    """inFeat = QgsFeature()
    inFeatB = QgsFeature()
    outFeat = QgsFeature()

    layer = self.iface.activeLayer()
    provider = layer.dataProvider()

    allAttrs = provider.attributeIndexes()
    provider.select(allAttrs)
    fields = provider.fields()

    new_path = layer.source()[:-4] + "_polygon.shp"
    writer = QgsVectorFileWriter(new_path,provider.encoding(),fields,QGis.WKBLineString,layer.srs())

    #split lines into single segments
    while provider.nextFeature( inFeat ):
      inGeom = inFeat.geometry()

      if inFeat.geometry().isMultipart():
        for line in inFeat.geometry().asMultiPolyline():
          self.splitline(line,outfile)
      else:
        self.splitline(inFeat.geometry().asPolyline(),writer)

    del writer

    line_layer = QgsVectorLayer(new_path, "tmp", "ogr")
    layerID = QgsMapLayerRegistry.instance().addMapLayer(line_layer).getLayerID()
    line_provider = line_layer.dataProvider()
    lineFeat = QgsFeature()
    lines = []
    #remove duplicate lines
    while line_provider.nextFeature( lineFeat ):
      temp = lineFeat.geometry().asPolyline()
      revTemp = [temp[-1], temp[0]]
      if temp not in lines and revTemp not in lines: lines.append( lineFeat.geometry().asPolyline() )

    QgsMapLayerRegistry.instance().removeMapLayer(layerID)
    del line_layer
    del line_provider

    writer = QgsVectorFileWriter(new_path,provider.encoding(),fields,QGis.WKBLineString,layer.srs())
    for line in lines:
      outFeat.setGeometry(QgsGeometry.fromPolyline(line))
      writer.addFeature(outFeat)

    del writer

    line_layer = QgsVectorLayer(new_path, "tmp", "ogr")
    layerID = QgsMapLayerRegistry.instance().addMapLayer(line_layer).getLayerID()
    line_provider = line_layer.dataProvider()

    index = createIndex(line_provider)

    lines = []
    #intersections
    while line_provider.nextFeature(inFeat):
      pointList = []
      inGeom = inFeat.geometry()
      lineList = index.intersects( inGeom.boundingBox())
      if len(lineList) > 0:
        for i in lineList:
          line_provider.featureAtId( int(i), inFeatB, True, allAttrs)
          tmpGeom = QgsGeometry( inFeatB.geometry() )
          if inGeom.intersects(tmpGeom):
            pointGeom = inGeom.intersection(tmpGeom)
            if pointGeom.type() == QGis.Point:
              if pointGeom.asPoint() not in pointList: 
                pointList.append(pointGeom.asPoint())
        linePoints = []
        linePoints = inGeom.asPolyline()
        s = [i for i in pointList+linePoints if i not in linePoints]
        if len(s)>1:
          l = sortPoints(linePoints[0],s)
        else: l = s

        tempLine = []
        tempLine.append(linePoints[0])
        tempLine.extend(l)
        tempLine.append(linePoints[1])

        countSubLines = len(tempLine)-1
        for p in range(countSubLines):
          lines.append([tempLine[p],tempLine[p+1]])

    QgsMapLayerRegistry.instance().removeMapLayer(layerID)
    del line_layer
    del line_provider

    #create polygons
    polygons = polygonize( lines )

    writer = QgsVectorFileWriter(new_path,provider.encoding(),fields,QGis.WKBPolygon,layer.srs() )
    for polygon in polygons:

      outFeat.setGeometry( QgsGeometry.fromWkt( str(polygon) ) )
      writer.addFeature( outFeat )

    del writer

    if new_path.contains("\\"):
      out_name = new_path.right((new_path.length() - new_path.lastIndexOf("\\")) - 1)
    else:
      out_name = new_path.right((new_path.length() - new_path.lastIndexOf("/")) - 1)
    if out_name.endsWith(".shp"):
      out_name = out_name.left(out_name.length() - 4)

    self.iface.addVectorLayer(new_path, out_name, "ogr")

  def splitline(self,line,outfile):
    for i in range(1,len(line)):
      newfeature=QgsFeature()
      newfeature.setGeometry(QgsGeometry.fromPolyline(line[i-1:i+1]))
      outfile.addFeature(newfeature)

def createIndex( provider ):
    feat = QgsFeature()
    index = QgsSpatialIndex()
    provider.rewind()
    while provider.nextFeature( feat ):
        index.insertFeature( feat )
    return index

#sorts point along line
def sortPoints(firstPoint, pointList ):
  newList = []
  for point in pointList:
    if point == None: continue
    dist = sqrPointsDist(firstPoint, point)
    newList.append((dist,point))

  sortedList = sorted(newList, key=lambda point: point[0])

  sortedPoints = []

  if len(sortedList) == 0:
    sortedPoints = []
  elif len(sortedPoints) == 1:
    sortedPoints = newList
  else:
    for item in sortedList:
      sortedPoints.append(item[1])

  return sortedPoints

def sqrPointsDist(point1, point2):
  x1 = point1[0]
  y1 = point1[1]

  x2 = point2[0]
  y2 = point2[1]

  sqrDist = (x1-x2)**2 + (y1-y2)**2
  return sqrDist"""