#!/bin/sh


# w 3.10
dstdir=W:/QGIS310/profil/.qgis3/profiles/default/python/plugins
# r
#dstdir=//share/appdata2008/culos/AppData/Roaming/.qgis3r/profiles/xcu/python/plugins
# ltr
#dstdir=//share/appdata2008/culos/AppData/Roaming/.qgisltr/profiles/xcu/python/plugins
# dev
#dstdir=//share/appdata2008/culos/AppData/Roaming/.qgis3dev/profiles/xcu/python/plugins

dstname="mask"

rm -rf $dstdir/$dstname

mkdir $dstdir/$dstname
cp ./*.py $dstdir/$dstname/
cp ./metadata.txt $dstdir/$dstname/

for dir in ui resources logic doc i18n
do
    mkdir $dstdir/$dstname/$dir
    cp ./$dir/* $dstdir/$dstname/$dir/
done

# pylupdate5 -noobsolete -verbose plugin_translation.pro
# lrelease -compress i18n/fr.ts
