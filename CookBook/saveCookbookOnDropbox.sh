#!/bin/bash
#
CURRENTDATE=`date +"%Y-%m-%d %T"`
CURRENTDATEONLY=`date +"%d%b%Y"`
saved_version='/UnSync/Les Recettes de Coat Tanguy/cookbook_version_'${CURRENTDATEONLY}'.pdf'
echo $saved_version
dropbox_uploader.sh upload cookbook.pdf "$saved_version"
