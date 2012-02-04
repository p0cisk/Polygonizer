#-*- coding: iso-8859-2 -*-
"""
/***************************************************************************
PolygonizerDialog
A QGIS plugin
Creates polygons from intersecting lines
                             -------------------
begin                : 2011-01-17
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

from PyQt4.QtCore import QObject, SIGNAL, QSettings, QString, QVariant
from PyQt4.QtGui import QDialog, QFileDialog, QMessageBox
from ui_polygonizer import Ui_Form
from qgis.core import QgsFeature, QgsVectorLayer, QgsField, QgsVectorFileWriter, QgsMapLayerRegistry, QgsGeometry, QgsSpatialIndex, QgsMapLayer, QGis  

from os.path import splitext
from os.path import dirname

from shapely.ops import polygonize
from shapely.geometry import Point,MultiLineString
import sys

from time import time
from frmAbout import Ui_frmAbout

# create the dialog for plugin
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
    QObject.connect( self.ui.bAbout, SIGNAL( "clicked()" ), self.ShowAbout )

    layerList = getLayersNames()
    self.ui.cmbLayer.addItems(layerList)

  def ShowAbout(self):
    dlg = PolygonizerAboutDialog(self.iface)
    # show the dialog
    dlg.setModal(True)
    dlg.show()
    dlg.exec_()

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
    
  def SetWidgetsEnabled(self, value):
    self.ui.btnCancel.setEnabled(value)
    self.ui.btnOK.setEnabled(value)
    self.ui.cmbLayer.setEnabled(value)
    self.ui.cbGeometry.setEnabled(value)
    self.ui.eOutput.setEnabled(value)
    self.ui.btnBrowse.setEnabled(value)
    self.ui.rbNew.setEnabled(value)
    self.ui.rbOld.setEnabled(value)

  def Polygonize(self):
    if self.ui.cmbLayer.currentText() == "":
      QMessageBox.critical(self, "Polygonizer", "Select line layer first!" )
    elif getMapLayerByName(self.ui.cmbLayer.currentText()).dataProvider().featureCount() == 0:
      QMessageBox.critical(self, "Polygonizer", "Selected layer has no lines!" )
    elif self.ui.eOutput.text() == "":
      QMessageBox.critical(self, "Polygonizer", "Choose output file!" )
    else:
      sys.setcheckinterval(10000)
      setValue = self.ui.pbProgress.setValue
      self.SetWidgetsEnabled(False)

      setValue(0)

      self.t1 = time()


      if self.ui.rbNew.isChecked():
        inFeat = QgsFeature()
        outFeat = QgsFeature()
        layer = QgsVectorLayer()

        layer = getMapLayerByName(self.ui.cmbLayer.currentText())

        progress = 0.

        provider = layer.dataProvider()
        allAttrs = provider.attributeIndexes()
        provider.select(allAttrs)
        fields = provider.fields()

        provider.select()

        step = 30. / layer.featureCount()
        allLinesList = []
        allLinesListExtend = allLinesList.extend
        allLinesListAppend = allLinesList.append

        while provider.nextFeature(inFeat):
          geom = inFeat.geometry()

          if geom.isMultipart():
            allLinesListExtend(geom.asMultiPolyline() )
          else:
            allLinesListAppend(geom.asPolyline())

          progress += step
          setValue(progress)


        allLines = MultiLineString(allLinesList)
        allLines = allLines.union(Point(0,0))

        polygons = list(polygonize([allLines]))

        self.polyCount = len(polygons)
        if self.polyCount == 0:
          QMessageBox.critical(self, "Polygonizer", "Sorry, I don't see any polygon!" )
          SetWidgetsEnabled(self.ui, True)
          setValue(0)
          return
        else:
          step = 65. / self.polyCount

          setGeometry = outFeat.setGeometry
          setAttributeMap = outFeat.setAttributeMap

          if self.ui.cbGeometry.isChecked():
            fields[len(fields)] = QgsField("area",QVariant.Double,"double",16,2)
            fields[len(fields)] = QgsField("perimeter",QVariant.Double,"double",16,2)
            nrArea = len(fields)-2
            nrPerimeter = len(fields)-1

            writer = QgsVectorFileWriter(self.ui.eOutput.text(),provider.encoding(),fields,QGis.WKBPolygon,layer.srs() )

            for polygon in polygons:
              setGeometry( QgsGeometry.fromWkt( polygon.wkt ) )
              setAttributeMap({ nrArea:polygon.area, nrPerimeter:polygon.length })
              writer.addFeature( outFeat )

              progress += step
              setValue(progress)

            setValue(100)
            del writer

          else:
            writer = QgsVectorFileWriter(self.ui.eOutput.text(),provider.encoding(),fields,QGis.WKBPolygon,layer.srs() )
            for polygon in polygons:
              setGeometry( QgsGeometry.fromWkt( polygon.wkt ) )
              writer.addFeature( outFeat )

              progress += step
              setValue(progress)

            setValue(100)
            del writer


      else:
        inFeat = QgsFeature()
        inFeatB = QgsFeature()
        outFeat = QgsFeature()
        layer = QgsVectorLayer()
        layer = self.getMapLayerByName(self.ui.cmbLayer.currentText())
        progress = 0.

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

        step = 20. / float(provider.featureCount())

        #to single lines and without duplicate lines
        provider.select()
        lines = []
        while provider.nextFeature( inFeat ):

          inGeom = inFeat.geometry()
          if inFeat.geometry().isMultipart():
            for line in inFeat.geometry().asMultiPolyline():
              self.splitline(line,lines)
          else:
            self.splitline(inFeat.geometry().asPolyline(),lines)
          progress += step
          setValue(progress)


        single_lines = QgsVectorLayer("LineString","single","memory")
        single_provider = single_lines.dataProvider()

        step = 20. / float(len(lines))
        for line in lines:
          outFeat.setGeometry(QgsGeometry.fromPolyline(line))
          single_provider.addFeatures([outFeat])
          single_lines.updateExtents()
          progress += step
          setValue(progress)


        #intersections
        index = createIndex(single_provider)
        lines = []
        single_provider.select()
        step = 50. / float(single_provider.featureCount())
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
          progress += step
          setValue(progress)

        del single_lines
        del single_provider

        #create polygons

        polygons = list(polygonize( lines ))

        self.polyCount = 0
        self.polyCount = len(polygons)


        setValue(95)

        setGeometry = outFeat.setGeometry
        setAttributeMap = outFeat.setAttributeMap

        if self.ui.cbGeometry.isChecked():
          fields[len(fields)] = QgsField("area",QVariant.Double,"double",16,2)
          fields[len(fields)] = QgsField("perimeter",QVariant.Double,"double",16,2)
          nrArea = len(fields)-2
          nrPerimeter = len(fields)-1

          writer = QgsVectorFileWriter(new_path,provider.encoding(),fields,QGis.WKBPolygon,layer.srs() )

          for polygon in polygons:
            setGeometry( QgsGeometry.fromWkt( polygon.wkt ) )
            setAttributeMap({ nrArea:polygon.area,
                                      nrPerimeter:polygon.length })
            writer.addFeature( outFeat )

            progress += step
            setValue(progress)

          del writer
          setValue(100)
        else:
          writer = QgsVectorFileWriter(new_path,provider.encoding(),fields,QGis.WKBPolygon,layer.srs() )

          for polygon in polygons:
            setGeometry( QgsGeometry.fromWkt( polygon.wkt ) )
            writer.addFeature( outFeat )

            progress += step
            setValue(progress)

          del writer
          setValue(100)


      self.t2 = time()

      self.SetWidgetsEnabled(True)

      msg = QMessageBox.question(self, 'Polygonizer', 'Polygonization finished in %03.2f seconds. \n %d polygons were crested. \n Load created layer?' % ((self.t2 - self.t1), self.polyCount), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
      if msg == QMessageBox.Yes:
        new_path = self.ui.eOutput.text()
        if new_path.contains("\\"):
          out_name = new_path.right((new_path.length() - new_path.lastIndexOf("\\")) - 1)
        else:
          out_name = new_path.right((new_path.length() - new_path.lastIndexOf("/")) - 1)
        if out_name.endsWith(".shp"):
          out_name = out_name.left(out_name.length() - 4)

        self.iface.addVectorLayer(self.ui.eOutput.text(), out_name, "ogr")

      self.close()


  def getMapLayerByName(self, myName ):
    layermap = QgsMapLayerRegistry.instance().mapLayers()
    for name, layer in layermap.iteritems():
      if layer.name() == myName:
        if layer.isValid():
          return layer
        else:
          return None

  def splitline(self,line,lines):
    for i in range(1,len(line)):
      temp = line[i-1:i+1]
      revTemp = [temp[-1], temp[0]]
      if temp not in lines and revTemp not in lines: lines.append( temp )



def getMapLayerByName(myName ):
  layermap = QgsMapLayerRegistry.instance().mapLayers()
  for name, layer in layermap.iteritems():
    if layer.name() == myName:
      if layer.isValid():
        return layer
      else:
        return None


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
  extFilter = 'Shapefiles (*.shp)'
  outFilePath = QFileDialog.getSaveFileName(parent, parent.tr('Save output shapefile'), outDir, extFilter)
  outFilePath = unicode(outFilePath)
  if outFilePath:
    root, ext = splitext(outFilePath)
    if ext.upper() != '.SHP':
      outFilePath = '%s.shp' % outFilePath
    outDir = dirname(outFilePath)
    settings.setValue(key, outDir)
  return outFilePath

def createIndex( provider ):
    feat = QgsFeature()
    index = QgsSpatialIndex()
    provider.rewind()
    provider.select()
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


class PolygonizerAboutDialog(QDialog):
  def __init__(self, iface):
    QDialog.__init__(self)
    # Set up the user interface from Designer.
    self.ui = Ui_frmAbout()
    self.ui.setupUi(self)
    self.iface = iface