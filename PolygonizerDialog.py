#-*- coding: iso-8859-2 -*-
"""
/***************************************************************************
PolygonizerDialog
A QGIS plugin
Creates polygons from intersecting lines
                             -------------------
begin                : 2011-01-17
copyright            : (C) 2011 by Piotr Pociask
email                : opengis84 (at) gmail (dot) com
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

from PyQt4.QtCore import QObject, SIGNAL, QSettings, QString, QVariant, QThread
from PyQt4.QtGui import QDialog, QFileDialog, QMessageBox
from ui_polygonizer import Ui_Form
from qgis.core import QgsFeature, QgsVectorLayer, QgsField, QgsVectorFileWriter, QgsMapLayerRegistry, QgsGeometry, QgsSpatialIndex, QgsMapLayer, QGis  

from os.path import splitext
from os.path import dirname

from shapely.ops import polygonize
from shapely.geometry import Point,MultiLineString

from time import time

global polyCount

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

  def outFile(self):
    """Open a file save dialog and set the output file path."""
    outFilePath = saveDialog(self)
    if not outFilePath:
      return
    self.ui.eOutput.setText((QString(outFilePath)))

  def closeForm(self):
    ''' Stop polygonization process or close window '''
    if self.ui.btnCancel.text() == 'Cancel':
      msg = QMessageBox.question(self, 'Polygonizer', 'Stop process?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
      if msg == QMessageBox.No:
        return

      QObject.disconnect(self.polygonizeThread,SIGNAL("finished()"), self.threadFinished)
      QObject.disconnect(self.layer,SIGNAL("editingStarted()"), self.startEditing)

      self.polygonizeThread.terminate()
      self.SetWidgetsEnabled(True)
      self.ui.pbProgress.setValue(0)
    else:
      self.close()

  def SetWidgetsEnabled(self, value):
    '''
    Sets wigdets disabled while calculating  
    value: True (enable) or False (disable)
    '''
    self.ui.btnOK.setEnabled(value)
    self.ui.cmbLayer.setEnabled(value)
    self.ui.cbGeometry.setEnabled(value)
    self.ui.cbTable.setEnabled(value)
    self.ui.rbNew.setEnabled(value)
    self.ui.rbOld.setEnabled(value)
    self.ui.cbOutput.setEnabled(value)
    self.ui.eOutput.setEnabled(self.ui.cbOutput.isChecked() and value )
    self.ui.btnBrowse.setEnabled(self.ui.cbOutput.isChecked() and value)

    if not value:
      self.ui.btnCancel.setText('Cancel')
    else:
      self.ui.btnCancel.setText('Close')


  def threadFinished(self):
    '''
    run when calculation ends
    ask to load created shapefile
    '''
    self.t2 = time()

    if self.ui.cbOutput.isChecked():
      msg = QMessageBox.question(self, 'Polygonizer', 'Polygonization finished in %03.2f seconds. \n %d polygons were crested. \n Load created layer?' % ((self.t2 - self.t1), polyCount), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
      if msg == QMessageBox.Yes:
        new_path = self.ui.eOutput.text()
        if new_path.contains("\\"):
          out_name = new_path.right((new_path.length() - new_path.lastIndexOf("\\")) - 1)
        else:
          out_name = new_path.right((new_path.length() - new_path.lastIndexOf("/")) - 1)
        if out_name.endsWith(".shp"):
          out_name = out_name.left(out_name.length() - 4)

        self.iface.addVectorLayer(self.ui.eOutput.text(), out_name, "ogr")
    else:
      QgsMapLayerRegistry().instance().addMapLayer(self.mLayer)
      QMessageBox.information(self, 'Polygonizer', 'Polygonization finished in %03.2f seconds. \n %d polygons were crested.' % ((self.t2 - self.t1), polyCount))

    QObject.disconnect(self.layer,SIGNAL("editingStarted()"), self.startEditing)
    QObject.disconnect(self.polygonizeThread, SIGNAL("progress"), self.setProgress)
    self.close()


  def startEditing(self):
    '''Disable editing line layer while calculating'''
    QMessageBox.critical(self, "Polygonizer", "You can't edit layer while polygonizing!" )
    self.layer.rollBack()


  def noPolygons(self):
    '''reset GUI when no polygons where created by polygonize process'''
    QMessageBox.critical(self, "Polygonizer", "No polygons were created!" )
    self.SetWidgetsEnabled(True)
    self.ui.pbProgress.setValue(0)


  def Polygonize(self):
    '''start calculation'''
    if self.ui.cmbLayer.currentText() == "":
      QMessageBox.critical(self, "Polygonizer", "Select line layer first!" )
      return
    elif getMapLayerByName(self.ui.cmbLayer.currentText()).dataProvider().featureCount() == 0:
      QMessageBox.critical(self, "Polygonizer", "Selected layer has no lines!" )
      return

    self.SetWidgetsEnabled(False)
    self.t1 = time()

    self.polygonizeThread = polygonizeThread(self, self.ui.rbNew.isChecked() )

    #thread finished
    QObject.connect(self.polygonizeThread,SIGNAL("finished()"), self.threadFinished)
    #set progress bar value
    QObject.connect(self.polygonizeThread, SIGNAL("progress"), self.setProgress)
    #show info and reset GUI when no polygons where created by polygonize process
    QObject.connect(self.polygonizeThread, SIGNAL("noPolygons"), self.noPolygons)

    self.polygonizeThread.start()


  def setProgress(self, value):
    '''
    set progress bar value
    value: value to set
    '''
    self.ui.pbProgress.setValue(value)



class polygonizeThread(QThread):
  def __init__(self, parent, useUnion):
      '''
      initilize thread which do calculation
      parent: PolygonizerDialog class instance
      useUnion: True if user choose new method of calculation 
      '''
      super(polygonizeThread, self).__init__(parent)
      self.parent = parent
      self.ui = parent.ui
      self.useUnion = useUnion

  def run(self):
    '''start calculation'''
    if self.useUnion:
      self.union()
    else:
      self.split()

  def union(self):
    '''new method using Union function'''
    global polyCount
    inFeat = QgsFeature()

    progress = 0.

    self.emit(SIGNAL('progress'), 0)

    self.parent.layer = getMapLayerByName(self.ui.cmbLayer.currentText())
    provider = self.parent.layer.dataProvider()
    #user can't toggle edit mode of line layer while polygonizing, plugin automatically turn it off 
    QObject.connect(self.parent.layer,SIGNAL("editingStarted()"), self.parent.startEditing)
    allAttrs = provider.attributeIndexes()
    provider.select(allAttrs)

    provider.select()

    step = 45. / self.parent.layer.featureCount()
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
      self.emit(SIGNAL('progress'), progress)

    allLines = MultiLineString(allLinesList)
    allLines = allLines.union(Point(0,0))

    polygons = list(polygonize([allLines]))

    polyCount = len(polygons)
    #if no polygons where created then exit from thread
    if polyCount == 0:
      QObject.disconnect(self.parent.polygonizeThread,SIGNAL("finished()"), self.parent.threadFinished)
      self.emit(SIGNAL('noPolygons'))
      return
    else:
      if self.ui.cbOutput.isChecked():
        self.saveAsFile(polygons, progress)
      else:
        self.saveInMemory(polygons, progress)

  def split(self):
    '''old method'''
    global polyCount
    inFeat = QgsFeature()
    inFeatB = QgsFeature()
    outFeat = QgsFeature()

    progress = 0.

    self.parent.layer = getMapLayerByName(self.ui.cmbLayer.currentText())
    provider = self.parent.layer.dataProvider()
    #user can't toggle edit mode of line layer while polygonizing, plugin automatically turn it off
    QObject.connect(self.parent.layer,SIGNAL("editingStarted()"), self.parent.startEditing)
    allAttrs = provider.attributeIndexes()
    provider.select(allAttrs)

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
          splitline(line,lines)
      else:
        splitline(inFeat.geometry().asPolyline(),lines)
      progress += step
      self.emit(SIGNAL('progress'), progress)

    single_lines = QgsVectorLayer("LineString","single","memory")
    single_provider = single_lines.dataProvider()

    step = 20. / float(len(lines))
    for line in lines:
      outFeat.setGeometry(QgsGeometry.fromPolyline(line))
      single_provider.addFeatures([outFeat])
      single_lines.updateExtents()
      progress += step
      self.emit(SIGNAL('progress'), progress)

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
      self.emit(SIGNAL('progress'), progress)

    del single_lines
    del single_provider

    #create polygons
    polygons = list(polygonize( lines ))
    polyCount = len(polygons)
    self.emit(SIGNAL('progress'), 95)

    if self.ui.cbOutput.isChecked():
      self.saveAsFile(polygons, progress)
    else:
      self.saveInMemory(polygons, progress)

  def saveAsFile(self, polygons, progress):
    '''
    save output polygon layer as Shapefile
    polygons: list of polygons created by Polygonize function
    progress: progress bar value
    '''
    global polyCount
    outFeat = QgsFeature()

    setGeometry = outFeat.setGeometry
    setAttributeMap = outFeat.setAttributeMap

    if self.ui.cbTable.isChecked():
      fields = self.parent.layer.dataProvider().fields()
    else:
      fields = {}
    polyCount = len(polygons)
    step = 50. / polyCount
    new_path = self.ui.eOutput.text()

    if self.ui.cbGeometry.isChecked():    
      fields[len(fields)] = QgsField("area",QVariant.Double,"double",16,2)
      fields[len(fields)] = QgsField("perimeter",QVariant.Double,"double",16,2)
      nrArea = len(fields)-2
      nrPerimeter = len(fields)-1
      writer = QgsVectorFileWriter(new_path,self.parent.layer.dataProvider().encoding(),fields,QGis.WKBPolygon,self.parent.layer.srs() )

      for polygon in polygons:
        setGeometry( QgsGeometry.fromWkt( polygon.wkt ) )
        setAttributeMap({ nrArea:QVariant(polygon.area), nrPerimeter:QVariant(polygon.length) })
        writer.addFeature( outFeat )

        progress += step
        self.emit(SIGNAL('progress'), progress)
    else:
      writer = QgsVectorFileWriter(new_path,self.parent.layer.dataProvider().encoding(),fields,QGis.WKBPolygon,self.parent.layer.srs() )

      for polygon in polygons:
        setGeometry( QgsGeometry.fromWkt( polygon.wkt ) )
        writer.addFeature( outFeat )

        progress += step
        self.emit(SIGNAL('progress'), progress)

    del writer
    self.emit(SIGNAL('progress'), 100)

  def saveInMemory(self, polygons, progress):
    '''
    save output polygon as memory layer
    polygons: list of polygons created by Polygonize function
    progress: progress bar value
    '''
    global polyCount
    outFeat = QgsFeature()

    setGeometry = outFeat.setGeometry
    setAttributeMap = outFeat.setAttributeMap

    if self.ui.cbTable.isChecked():
      fields = self.parent.layer.dataProvider().fields()
    else:
      fields = {}
    polyCount = len(polygons)
    step = 50. / polyCount

    mLayer = QgsVectorLayer("Polygon", '%s_polygons' % self.ui.cmbLayer.currentText(), "memory")
    provider = mLayer.dataProvider()
    if self.ui.cbGeometry.isChecked():
      fields[len(fields)] = QgsField("area",QVariant.Double,"double",16,2)
      fields[len(fields)] = QgsField("perimeter",QVariant.Double,"double",16,2)
      nrArea = len(fields)-2
      nrPerimeter = len(fields)-1

      provider.addAttributes([fields[i] for i in range(len(fields))])
      for polygon in polygons:
        setGeometry(QgsGeometry.fromWkt(polygon.wkt))
        setAttributeMap({ nrArea:polygon.area, nrPerimeter:polygon.length })
        provider.addFeatures([outFeat])

        progress += step
        self.emit(SIGNAL('progress'), progress)
    else:
      provider.addAttributes([fields[i] for i in range(len(fields))])
      for polygon in polygons:
        setGeometry(QgsGeometry.fromWkt(polygon.wkt))
        provider.addFeatures([outFeat])

        progress += step
        self.emit(SIGNAL('progress'), progress)

    mLayer.updateExtents()
    mLayer.updateFieldMap()
    self.parent.mLayer = mLayer
    self.emit(SIGNAL('progress'), 100)


def splitline(line,lines):
  '''
  split line into segments
  @param line: input line
  @param lines: output list containing two point segments
  '''
  for i in range(1,len(line)):
    temp = line[i-1:i+1]
    revTemp = [temp[-1], temp[0]]
    if temp not in lines and revTemp not in lines: lines.append( temp )


def getMapLayerByName(myName ):
  '''
  return pointer to line layer by name in layer list
  @param myName: name of layer
  '''
  layermap = QgsMapLayerRegistry.instance().mapLayers()
  for name, layer in layermap.iteritems():
    if layer.name() == myName:
      if layer.isValid():
        return layer
      else:
        return None


def getLayersNames():
  '''
  return list of line layers loaded into QGIS
  '''
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
  '''
  return Spatial Index of line layer features
  @param provider: QgsDataProvider
  '''
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
  '''
  return distance between two points
  @param point1: first point
  @param point2: second point
  '''
  x1 = point1[0]
  y1 = point1[1]

  x2 = point2[0]
  y2 = point2[1]

  sqrDist = (x1-x2)**2 + (y1-y2)**2
  return sqrDist