#!/usr/bin/python
# -*- coding: utf-8 -*-

import hashlib, zlib


def get_file_crc32(filename):
    """Compute CRC32 checksum from a file
    """
    prev = 0
    with open(filename, 'rb') as theFile:
        for chunk in theFile:
            prev = zlib.crc32(chunk, prev)

    return "%X"%(prev & 0xFFFFFFFF)

def get_file_md5(filename):
    """Compute MD5 Hash from a file
    """
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
