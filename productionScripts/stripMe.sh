#!/bin/bash

### 
#
# WEIO Web Of Things Platform
# Copyright (C) 2013 Nodesign.net, Uros PETREVSKI, Drasko DRASKOVIC
# All rights reserved
#
#               ##      ## ######## ####  #######  
#               ##  ##  ## ##        ##  ##     ## 
#               ##  ##  ## ##        ##  ##     ## 
#               ##  ##  ## ######    ##  ##     ## 
#               ##  ##  ## ##        ##  ##     ## 
#               ##  ##  ## ##        ##  ##     ## 
#                ###  ###  ######## ####  #######
#
#                    Web Of Things Platform 
#
# This file is part of WEIO
# WEIO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WEIO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors : 
# Uros PETREVSKI <uros@nodesign.net>
# Drasko DRASKOVIC <drasko.draskovic@gmail.com>
#
###


# clean old file
#rm weioStripped.tar.bz2

# after all process to decompress type : tar -zxvf weioStripped.tar.gz
# make new dir for stripped version at level -1
mkdir weioStripped 

# copy all visible files, ignore unvisible git files
rsync -av --exclude=".*" --exclude="productionScripts" ../ weioStripped

# exclude production folders
rm -r weioStripped/doc
rm -r weioStripped/graphicsSource
rm -r weioStripped/openWrt
rm -r weioStripped/sandbox
rm -r weioStripped/README.md

# kill all .pyc files to leave native arch to build them
find . -name '*.pyc' -delete

# make tar archive 
tar -zcvf weioStripped.tar.gz weioStripped/

# kill weioStripped folder
rm -r weioStripped

# To decompress type : tar -zxvf weioStripped.tar.gz

echo ""
echo "Created archive weioStripped.tar.bz2"
echo ""
echo "Now do:"
echo "$ scp -r weioStripped.tar.bz2 root@weio.local:/tmp"
echo "and then in WeIO:"
echo "tar -xzvf /tmp/weioStripped.tar.gz"
