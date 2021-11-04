#!/bin/bash
#
CURRENTDATE=`date +"%Y-%m-%d %T"`
CURRENTDATEONLY=`date +"%d%b%Y"`

saved_version='/UnSync/Les Recettes de Coat Tanguy/cookbook_version_'${CURRENTDATEONLY}'.pdf'
echo $saved_version
dropbox_uploader.sh upload cookbook.pdf "$saved_version"
dropbox_uploader.sh share "$saved_version"

saved_version='/UnSync/Les Recettes de Coat Tanguy/cookbook_NoMarge_version_'${CURRENTDATEONLY}'.pdf'
echo $saved_version
dropbox_uploader.sh upload cookbook_Nomarge.pdf "$saved_version"
dropbox_uploader.sh share "$saved_version"

