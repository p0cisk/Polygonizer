"""
/***************************************************************************
LayerManagerDialog
A QGIS plugin
Creates polygons from intersecting lines
                             -------------------
begin                : 2011-01-17 
copyright            : (C) 2011 by Piotr Pociask
email                : p0cisk (at) o2.pl 
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_polygonizer import Ui_Form
from qgis.core import *
from qgis.gui import *

from os.path import splitext
from itertools import groupby
from os.path import basename
from os.path import dirname

import shapely
from shapely.ops import polygonize

# create the dialog for zoom to point
class PolygonizerDialog(QDialog):
  def __init__(self, iface): 
    QDialog.__init__(self) 
    # Set up the user interface from Designer. 
    self.ui = Ui_Form()
    self.ui.setupUi(self) 
    self.iface = iface

    QObject.connect( self.ui.btnBrowse, SIGNAL( "clicked()" ), self.outFile )
    QObject.connect( self.ui.btnCancel, SIGNAL( "clicked()" ), self.closeForm )
    QObject.connect( self.ui.btnOK, SIGNAL( "clicked()" ), self.Polygonize )

    layerList = getLayersNames()
    self.ui.cmbLayer.addItems(layerList)
    #QInputDialog.getText( self.iface.mainWindow(), "m", "e",   QLineEdit.Normal, str( layerList ) )

  def outFile(self):
    """Open a file save dialog and set the output file path."""
    outFilePath = saveDialog(self)
    if not outFilePath:
      return
    self.setOutFilePath(QString(outFilePath))

  def setOutFilePath(self, outFilePath):
    """Set the output file path."""
    self.ui.eOutput.setText(outFilePath)

  def closeForm(self):
    self.close()

  def Polygonize(self):
    #start
    #self.Form.setWindowTitle("jakis tekst")
    inFeat = QgsFeature()
    inFeatB = QgsFeature()
    outFeat = QgsFeature()
    layer = QgsVectorLayer()
    layer = self.getMapLayerByName(self.ui.cmbLayer.currentText())

    #layer = self.iface.activeLayer()
    provider = layer.dataProvider()

    allAttrs = provider.attributeIndexes()
    provider.select(allAttrs)
    fields = provider.fields()

    new_path = self.ui.eOutput.text()
    if new_path.contains("\\"):
      out_name = new_path.right((new_path.length() - new_path.lastIndexOf("\\")) - 1)
    else:
      out_name = new_path.right((new_path.length() - new_path.lastIndexOf("/")) - 1)
    if out_name.endsWith(".shp"):
      out_name = out_name.left(out_name.length() - 4)

    #split lines into single segments
    split_lines = QgsVectorLayer("LineString","split","memory")
    splitID = QgsMapLayerRegistry.instance().addMapLayer(split_lines).getLayerID()
    split_provider = split_lines.dataProvider()


    while provider.nextFeature( inFeat ):
      inGeom = inFeat.geometry()

      if inFeat.geometry().isMultipart():
        for line in inFeat.geometry().asMultiPolyline():
          self.splitline(line,split_provider,split_lines)
      else:
        self.splitline(inFeat.geometry().asPolyline(),split_provider,split_lines)


    #remove duplicate lines
    lineFeat = QgsFeature()
    lines = []

    split_provider.select()
    while split_provider.nextFeature( lineFeat ):
      temp = lineFeat.geometry().asPolyline()
      revTemp = [temp[-1], temp[0]]
      if temp not in lines and revTemp not in lines: lines.append( lineFeat.geometry().asPolyline() )

    QgsMapLayerRegistry.instance().removeMapLayer(splitID)
    del split_lines
    del split_provider
    #QMessageBox.critical(self.iface.mainWindow(), "d", str(len(lines)))
    #QgsMapLayerRegistry.instance().removeMapLayer(layerID)
    single_lines = QgsVectorLayer("LineString","single","memory")
    singleID = QgsMapLayerRegistry.instance().addMapLayer(single_lines).getLayerID() 
    single_provider = single_lines.dataProvider()

    for line in lines:
      outFeat.setGeometry(QgsGeometry.fromPolyline(line))
      single_provider.addFeatures([outFeat])
      single_lines.updateExtents()

    #intersections
    index = createIndex(single_provider)
    lines = []
    single_provider.select()

    while single_provider.nextFeature(inFeat):
      pointList = []
      inGeom = inFeat.geometry()
      lineList = index.intersects( inGeom.boundingBox())
      if len(lineList) > 0:
        for i in lineList:
          single_provider.featureAtId( int(i), inFeatB, True, allAttrs)
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

    QgsMapLayerRegistry.instance().removeMapLayer(singleID)
    del single_lines
    del single_provider

    #create polygons
    polygons = polygonize( lines )

    #fields.extend([QgsField("area",QVariant.Double),QgsField("perimiter",QVariant.Double)])
    #QMessageBox.critical(self.iface.mainWindow(), "d", str(fields))
    fields[len(fields)] = QgsField("area",QVariant.Double,"double",16,2)
    writer = QgsVectorFileWriter(new_path,provider.encoding(),fields,QGis.WKBPolygon,layer.srs() )
    for polygon in polygons:

      outFeat.setGeometry( QgsGeometry.fromWkt( str(polygon) ) )
      nr = len(fields)-1
      outFeat.setAttributeMap({ nr:outFeat.geometry().area() })
      writer.addFeature( outFeat )

    del writer

    self.iface.addVectorLayer(new_path, out_name, "ogr")

    self.close()
  #stop

  def getMapLayerByName(self, myName ):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layermap.iteritems():
      if layer.name() == myName:
        if layer.isValid():
          return layer
        else:
          return None

  def splitline(self,line,outfile,vlayer):
    for i in range(1,len(line)):
      newfeature=QgsFeature()
      newfeature.setGeometry(QgsGeometry.fromPolyline(line[i-1:i+1]))
      outfile.addFeatures([newfeature])
      vlayer.updateExtents()

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
  return sqrDist

def getLayersNames():
  layermap = QgsMapLayerRegistry.instance().mapLayers()
  layerlist = []
  for name, layer in layermap.iteritems():
    if layer.type() == QgsMapLayer.VectorLayer:
      if layer.geometryType() == QGis.Line:
        layerlist.append( unicode( layer.name() ) )

  return layerlist

def saveDialog(parent):
  """Shows a save file dialog and return the selected file path."""
  settings = QSettings()
  key = '/UI/lastShapefileDir'
  outDir = settings.value(key).toString()
  filter = 'Shapefiles (*.shp)'
  outFilePath = QFileDialog.getSaveFileName(parent, parent.tr('Save output shapefile'), outDir, filter)
  outFilePath = unicode(outFilePath)
  if outFilePath:
    root, ext = splitext(outFilePath)
    if ext.upper() != '.SHP':
      outFilePath = '%s.shp' % outFilePath
    outDir = dirname(outFilePath)
    settings.setValue(key, outDir)
  return outFilePath