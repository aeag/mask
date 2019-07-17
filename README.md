mask
===========

This is a QGIS (qgis.org) python extension, allowing a user to quickly transform a polygon selection into a map masking layer or a region of interest, following symbology choice.

The plugin allows also to spatially filter labeling of other layer, so that labels will only appear in the Region of Interest.

If the plugin is loaded, and if a mask has been defined, It will automatically be applied to Atlas - batch map printing- use case.

Current Atlas coverage feature will be used to generate a temporary mask layer.

This plugin requires QGIS >= 3.4

Contributors : Hugo Mercier (Oslandia - https://github.com/mhugo), Xavier Culos (Agence de l'eau Adour-Garonne - https://github.com/xcaeag), Régis Haubourg (Oslandia - https://github.com/haubourg) Funded by Agence de l'eau Adour Garonne eau-adour-garonne.fr https://github.com/aeag

This program is free software ; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation ; either version 2 of the License, or (at your option) any later version.                               


An alternative, to combine mask and Atlas without plugin (3.x)
--

The principle is to use the renderer "inverted polygons" + "Rule-based" to filter the current mask feature, with the style "Shapeburst fill".

The 'mask' filter of the rule :
`attribute($currentfeature, 'the_primary_key_field') = attribute(@atlas_feature , 'the_primary_key_field')`

The label layer filter if neaded :
`contains(@atlas_geometry, $geometry)`

![tuto-mask](https://user-images.githubusercontent.com/7790344/49210169-ad32f800-f3bc-11e8-865d-c00dd9b77b76.gif)
