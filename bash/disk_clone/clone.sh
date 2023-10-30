#!/bin/ash

mount /dev/sda2 /mnt
sleep 2
rm -f /etc/cloud/cloud.cfg.d/*.cfg
rm -Rf /mnt/var/lib/cloud/*
cp 10-cloud.cfg /mnt/etc/cloud/cloud.cfg.d/
cp 05_logging.cfg /mnt/etc/cloud/cloud.cfg.d/
sync
umount /mnt

fsck.ext2 /dev/sda2
dd if=/dev/sda of=sda.mbr count=1 bs=512
sfdisk -d /dev/sda > sda-ext.sf
partclone.fat32 --clone --source /dev/sda1 | lz4 > sda1.fat32.lz4
partclone.ext4 --clone --source /dev/sda2 | lz4 > sda2.ext4.lz4
