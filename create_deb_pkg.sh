#!/bin/bash

# dpkg must be installed 

PACKAGE='testpackage'
VERSION='1.0'
REVISION='1'
ARCH='all'
MAINTAINER='Testcompany, Inc info@testcompany.com'
DESCRIPTION='testpackage'
PACKAGE_FULLNAME="${PACKAGE}_${VERSION}-${REVISION}_${ARCH}"

mkdir -p ${PACKAGE_FULLNAME}/home/testpackage/files
mkdir ${PACKAGE_FULLNAME}/DEBIAN

# copy files to install into directory ${PACKAGE_FULLNAME}/home/testpackage/files/

cat <<EOF > ${PACKAGE_FULLNAME}/DEBIAN/control
Package: $PACKAGE
Version: ${VERSION}-${REVISION}
Architecture: $ARCH 
Maintainer: $MAINTAINER 
Description: $DESCRIPTION 
EOF

# Do any pre/post steps in the following scripts.

#cat <<EOF > ${PACKAGE_FULLNAME}/DEBIAN/preinst
#EOF
#chmod 755 ${PACKAGE_FULLNAME}/DEBIAN/preinst

#cat <<EOF > ${PACKAGE_FULLNAME}/DEBIAN/postinst
#EOF
#chmod 755 ${PACKAGE_FULLNAME}/DEBIAN/postinst

#cat <<EOF > ${PACKAGE_FULLNAME}/DEBIAN/prerm
#EOF
#chmod 755 ${PACKAGE_FULLNAME}/DEBIAN/prerm

#cat <<EOF > ${PACKAGE_FULLNAME}/DEBIAN/postrm
#EOF
#chmod 755 ${PACKAGE_FULLNAME}/DEBIAN/postrm

dpkg-deb --build --root-owner-group $PACKAGE_FULLNAME
