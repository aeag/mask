# {{ title }} - Documentation

> **Author and contributors:** {{ author }}
>
> **Version:** {{ version }}
>
> **Source code:** {{ repo_url }}

```{toctree}
---
maxdepth: 1
caption: Others
---
```

## English version

### **About**

That tool is designed to help users to quickly generate cartographic masking layer to enlight an area of interest.  
  
Please notify any issue or enhancement request [here](https://github.com/aeag/mask_plugin/issues/)

### **How to use it ?**

When one or more objects are selected, activating the plugin generates a new layer containing a "mask" geometry.

Then you can modifies the mask layer properties:

  - style options (default is inverted polygon renderer + border shading)
  - buffer around mask
  - filter labels of features falling outside area of interest (achieved by a **in_mask(SRID)** function filter on labeling placement options)
  choose mask layer format (Memory or any OGR datasource)
      
### **Mask and labels**

### **Mask and Atlas generation**

### **Advanced usage**

You can trigger the creation of masks from the python console, or from a other plugin.

```python
# import plugin
from mask import aeag_mask
# Classic call : mask the selected features
aeag_mask.do()

# advanced call : custom geometry
sr = QgsCoordinateReferenceSystem()
sr.createFromSrid(2154)
geom = QgsGeometry.fromWkt("POLYGON((356419 6120047, 1051423 6120047, 1051423 6595985, 356419 6595985, 356419 6120047))")
aeag_mask.do(sr, { geom }, "MyMask")
```
## En Français

### **À propos**

Cet outil a été développé pour aider les utilisateurs à générer rapidement des couches de masque pour mettre en évidence une zone d'intérêt.

Merci de notifier tout problème ou demande d'évolution [ici](https://github.com/aeag/mask_plugin/issues/)

### **Comment l'utiliser ?**

Lorsqu'un ou plusieurs polygones sont sélectionnés, l'activation du masque est rendue possible (l'icône s'active), pour créer une nouvelle couche de masque.

Vous pouvez alors modifier les propriétés du masque :

  - options de style (par défaut: polygone inversé avec bords flous)
  - tampon autour du masque
  - filtre des étiquettes pour les entités qui sont à l'intérieur de la zone d'intérêt (obtenu via la fonction filtre booléenne **in_mask(SRID)** sur les options de positionnement des étiquettes)
  - choix du format de la couche de masque (couche mémoire ou OGR)

### **Le masque et les étiquettes**

### **Le masque et la production d'atlas**

### **Usage avancé**

La création d'un masque peut s'effectuer par un appel à la fonction do_mask, de sorte que la génération de masque peut être pilotée par d'autres plugins.

```python
# import du plugin
from mask import aeag_mask
# Appel simple afin de masquer les entités sélectionnées
aeag_mask.do()

# Construction d'un masque de forme personnalisée
sr = QgsCoordinateReferenceSystem()
sr.createFromSrid(2154)
geom = QgsGeometry.fromWkt("POLYGON((356419 6120047, 1051423 6120047, 1051423 6595985, 356419 6595985, 356419 6120047))")
aeag_mask.do(sr, { geom }, "MyMask")
