#!/bin/bash
#
CURRENTDATE=`date +"%Y-%m-%d %T"`
CURRENTDATEONLY=`date +"%d%b%Y"`
saved_version='/UnSync/Les Recettes de Coat Tanguy/cookbook_marge_version_'${CURRENTDATEONLY}'.pdf'
echo $saved_version
dropbox_uploader.sh upload cookbook_marge.pdf "$saved_version"
dropbox_uploader.sh share "$saved_version"
