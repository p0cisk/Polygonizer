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
 This script initializes the plugin, making it known to QGIS.
"""
def name(): 
  return "Polygonizer" 
def description():
  return "Creates polygons from intersecting lines (requires shapely library)"
def version(): 
  return "Version 0.1" 
def icon():
  return "icon.png"
def qgisMinimumVersion():
  return "1.0"
def classFactory(iface): 
  # load Polygonizer class from file Polygonizer
  from polygonizer import Polygonizer 
  return Polygonizer(iface)


