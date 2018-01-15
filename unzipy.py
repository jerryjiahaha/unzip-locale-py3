#!/usr/bin/env python3

"""Something like unzip, but support locale encodings"""

import zipfile
from pathlib import Path
import sys, os
import argparse

# https://docs.python.org/3.6/library/codecs.html#standard-encodings
# WinZip interprets all file names as encoded in CP437, also known as DOS Latin.
def encodeName(name, encoding):
    fname = name.encode("cp437").decode(encoding)
    # Note u'\u3000' is full-width space
    return fname.replace(u'\u0000', ' ')

def extractZip(zfile: zipfile.ZipFile, zf: zipfile.ZipInfo, encoding: str, \
        dst_path=Path(".")):
    new_name = encodeName(zf.filename, encoding)
    new_path = dst_path.joinpath(new_name)
    print("new_path:", new_path)
    if zf.is_dir():
        new_path.mkdir(exist_ok=True, parents=True)
    else:
        new_path.parent.mkdir(exist_ok=True, parents=True)
        with new_path.open(mode='wb') as newf:
            newf.write(zfile.read(zf.filename))

def detectSubdir(zfile: zipfile.ZipFile):
    """Auto detect whether the zip file has root dir
        return True if has top directory
    """
    names = zfile.namelist()
    files = zfile.infolist()
    if len(names) == 1:
        testf = Path(names[0])
        if len(testf.parents) > 1 or files[0].is_dir():
            return True
    return any(map(lambda x: names[0] in x, names))


#def getTopdir(zfile: zipfile.ZipFile):
#    """Get top dir of the file
#    """
#    files = zfile.infolist()
#    testf = Path(files[0])
#    if len(testf.parents) > 1 and not files[0].is_dir():
#        # file with parent dir
#        return testf.parent
#    return testf


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--encode", help="encoding of input file", default="sjis")
    parser.add_argument("-d", "--dest", help="destination dir", default=".")
    parser.add_argument("-p", "--password", help="set password", default=None)
    parser.add_argument("-s", "--subdir-detect", action="store_true", \
            help="auto create dir if no top dir found", default=False)
    parser.add_argument("filename")
#    parser.add_argument("list", nargs="?")
    args = parser.parse_args()
    print(args)

    dst_path = Path(args.dest)
    zfile = Path(args.filename)
    with zipfile.ZipFile(zfile) as zf:
        if args.subdir_detect and not detectSubdir(zf):
            dst_path = dst_path.joinpath(\
                encodeName(zf.filename, args.encode))
            print("No top top dir, will create top dir:", dst_path)
        if args.password is not None:
            zf.setpassword(args.password)
        dst_path.mkdir(parents=True, exist_ok=True)
        for zf_one in zf.infolist():
            extractZip(zf, zf_one, args.encode, dst_path=dst_path)
    
