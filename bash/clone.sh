#!/bin/bash
dd if=/dev/sda of=sda.mbr count=1 bs=512
sfdisk -d /dev/sda > sda-ext.sf
partclone.fat32 --clone --source /dev/sda1 | lz4 > sda1.fat32.lz4
partclone.ext4 --clone --source /dev/sda2 | lz4 > sda2.ext4.lz4
