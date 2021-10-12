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
On QGIS Plugins repository <https://plugins.qgis.org/plugins/mask/>
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

The configuration interface allows you to fine-tune the filtering of the labels, by adding for you the expression 'in_mask ()' in the property 'show label' of the corresponding layers.

![tuto-labels](https://raw.githubusercontent.com/aeag/mask/master/docs/static/mask-labels.gif)

### **Mask and Atlas generation**

When a mask is defined, the cover layer used by atlas (cf. layouts) uses it, the geometry of the mask then takes the form of the current entity.
Warning: It can be confusing when you close the 'layout' window.

Remember to define extent 'controlled by the atlas', on the map object.

Warning: when creating a layout, the mask is not synchronized with atlas. It will be during the following openings.

![tuto-atlas](https://raw.githubusercontent.com/aeag/mask/master/docs/static/mask-atlas.gif)

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

# or with parameter keep_layer=True to keep previous layer id (map theme use case).
```

### **An alternative, to combine mask and Atlas without plugin (3.x)**

The principle is to use the renderer "inverted polygons" + "Rule-based" to filter the current mask feature, with the style "Shapeburst fill".

The 'mask' filter of the rule :
`attribute($currentfeature, 'the_primary_key_field') = attribute(@atlas_feature , 'the_primary_key_field')`

The label layer filter if neaded :
`contains(@atlas_geometry, $geometry)`

## En Français

### **À propos**

Cet outil a été développé pour aider les utilisateurs à générer rapidement des couches de masque pour mettre en évidence une zone d'intérêt.

Merci de notifier tout problème ou demande d'évolution [ici](https://github.com/aeag/mask_plugin/issues/)

### **Comment l'utiliser ?**

Lorsqu'un ou plusieurs polygones sont sélectionnés, l'activation du masque est rendue possible (l'icône s'active), pour créer une nouvelle couche de masque.

Vous pouvez alors modifier les propriétés du masque :

  - options de style (par défaut: polygone inversé avec bords flous)
  - tampon autour du masque
  - filtre des étiquettes pour les entités qui sont à l'intérieur de la zone (avec la fonction filtre booléenne **in_mask(SRID)** sur les options de positionnement des étiquettes)
  - choix du format de la couche de masque (couche mémoire ou OGR)

### **Le masque et les étiquettes**

L'interface de configuration vous permet de régler finement le filtrage des étiquettes, en ajoutant pour vous l'expression 'in_mask()' dans la propriété 'montrer l'étiquette' des couches correspondantes.

![tuto-labels](https://raw.githubusercontent.com/aeag/mask/master/docs/static/mask-labels.gif)

### **Le masque et la production d'atlas**

Lorsqu'un masque est défini, la couche de couverture exploitée par l'atlas (cf. les mises en page) exploite celui-ci, la géométrie du masque prend alors la forme de l'entité courante.  
Attention : Cela peut être déroutant lorsque vous fermez la fenêtre 'mise en page'.

Pensez à définir une emprise 'contrôlée par l'atlas', au niveau de l'objet carte.

Attention : à la création d'une mise en page, le masque n'est pas synchronisé avec l'atlas. Il le sera lors des ouvertures suivantes.

![tuto-atlas](https://raw.githubusercontent.com/aeag/mask/master/docs/static/mask-atlas.gif)

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

# avec le paramètre keep_layer=True pour conserver l'identifiant du masque précédent (peut ainsi persister avec l'utilisation de thème de carte)

```

### **Une alternative, pour utiliser le masque avec un atlas, sans ce plugin**

Le principe est d'utiliser le rendu 'polygone inversé' sur une couche qui nous servira de couverture d'atlas et de masque, de filtrer selon des règles...

Le filtrage des entité :
`attribute($currentfeature, 'nom_de_colonne_cle_primaire') = attribute(@atlas_feature , 'nom_de_colonne_cle_primaire')`

Le filtrage des étiquettes si besoin :
`contains(@atlas_geometry, $geometry)`
