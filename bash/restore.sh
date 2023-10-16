#!/bin/bash
dd if=sda.mbr of=/dev/sda
sfdisk /dev/sda < sda-ext.sf
lz4cat sda1.fat32.lz4 | partclone.fat32 --restore --output /dev/sda1
lz4cat sda2.ext4.lz4 | partclone.ext4 --restore  --output /dev/sda2
