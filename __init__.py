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
Changelog:
0.3
-fix error -> polygonize only visible lines if whole layer isn't displayed in map window
-temp layers aren't visible

0.2
-add progress bar
-add geometry columns creation (area and perimeter)

0.1
-first release
****************************************************************************/

 This script initializes the plugin, making it known to QGIS.
"""
def name(): 
  return "Polygonizer" 
def description():
  return "Creates polygons from intersecting lines (requires shapely library)"
def version(): 
  return "Version 0.3" 
def icon():
  return "icon.png"
def qgisMinimumVersion():
  return "1.5"
def classFactory(iface): 
  # load Polygonizer class from file Polygonizer
  from polygonizer import Polygonizer 
  return Polygonizer(iface)


