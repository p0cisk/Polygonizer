"""
/***************************************************************************
Polygonizer
A QGIS plugin
Creates polygons from intersecting lines
                             -------------------
begin                : 2011-01-20
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QIcon, QAction, QDialog, QMessageBox

# Initialize Qt resources from file resources.py
import resources
#form
from PolygonizerDialog import PolygonizerDialog, getLayersNames
from frmAbout import Ui_frmAbout


class Polygonizer:

  def __init__(self, iface):
    # Save reference to the QGIS interface
    self.iface = iface

  def initGui(self):
    # Create action that will start plugin configuration
    self.action = QAction(QIcon(":/plugins/polygonizer/icon.png"), "Polygonizer", self.iface.mainWindow())
    self.actionAbout = QAction( QIcon( ":/about.png" ), "About", self.iface.mainWindow() )
    # connect the action to the run method
    QObject.connect(self.action, SIGNAL("triggered()"), self.run)
    QObject.connect( self.actionAbout, SIGNAL( "triggered()" ), self.showAbout )

    # Add toolbar button and menu item
    if hasattr(self.iface, "addPluginToRasterMenu"): 
      # new menu available so add both actions into PluginName submenu 
      # under Raster menu 
      self.iface.addPluginToVectorMenu( "&Polygonizer", self.action )  
      self.iface.addPluginToVectorMenu( "&Polygonizer", self.actionAbout )
      # and add Run button to the Raster panel 
      self.iface.addVectorToolBarIcon( self.action )
             
    else: 
      self.iface.addToolBarIcon(self.action)
      self.iface.addPluginToMenu("&Polygonizer", self.action)
      self.iface.addPluginToMenu("&Polygonizer", self.actionAbout)

  def unload(self):
    # Remove the plugin menu item and icon
    if hasattr(self.iface, "addPluginToRasterMenu"): 
      # new menu used, remove submenus from main Raster menu 
      self.iface.removePluginVectorMenu( "&Polygonizer",self.action)
      self.iface.removePluginVectorMenu( "&Polygonizer",self.actionAbout)
      # also remove button from Raster toolbar 
      self.iface.removeVectorToolBarIcon( self.action ) 
    else: 
      # Plugins menu used, remove submenu and toolbar button 
      self.iface.removePluginMenu("&Polygonizer",self.action)
      self.iface.removePluginMenu("&Polygonizer",self.actionAbout)
      self.iface.removeToolBarIcon(self.action)

  def showAbout(self):
    dlg = PolygonizerAboutDialog(self.iface)
    # show the dialog
    dlg.setModal(True)
    dlg.show()
    dlg.exec_()
    
  # run method that performs all the real work
  def run(self):

    dlg = PolygonizerDialog(self.iface)
    
    #load line layers to ComboBox
    layerList = getLayersNames()
    if not layerList:
      QMessageBox.critical(None, 'Polygonizer', 'No line layers loaded into QGIS', buttons=QMessageBox.Ok)
      return
    dlg.ui.cmbLayer.addItems(layerList)
    
    # show the dialog
    dlg.show()
    result = dlg.exec_()
    # See if OK was pressed
    if result == 1:
      # do something useful (delete the line containing pass and
      # substitute with your code
      pass
  
  
class PolygonizerAboutDialog(QDialog):
  def __init__(self, iface):
    QDialog.__init__(self)
    # Set up the user interface from Designer.
    self.ui = Ui_frmAbout()
    self.ui.setupUi(self)
    self.iface = iface