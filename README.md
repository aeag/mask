mask_plugin
===========
date: 2014 06 17
AEAG Mask plugin

This is a QGIS (qgis.org) python extension, allowing a user to quickly transform a polygon selection into a map masking layer or a region of interest, following symbology choice.

The plugin allows also to spatially filter labeling of other layer, so that labels will only appear in the Region of Interest. 

If the plugin is loaded, and if a mask has been defined, It will automatically be applied to Atlas - batch map printing- use case.

Current Atlas coverage feature will be used to generate a temporary mask layer. 

This plugin requires QGIS >= 2.3

Contributors: Hugo Mercier (Oslandia), Xavier Culos (https://github.com/xcaeag), Régis Haubourg (https://github.com/haubourg)
Funded by Agence de l'eau Adour Garonne eau-adour-garonne.fr   https://github.com/aeag


/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
