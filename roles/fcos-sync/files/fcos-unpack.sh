#!/usr/bin/env bash
set -e
SOURCE_DIR=$1
TARGET_DIR=$2

function echo_stderr {
  echo "$@" 1>&2; 
}

if [ -z "$1" ]; then
  echo_stderr "please provide source dir."
  exit 1
fi

if [ -z "$2" ]; then
  echo_stderr "please provide target dir."
  exit 1
fi

SOURCE_DIR=$1
TARGET_DIR=$2

if [ ! -d "$SOURCE_DIR" ]; then
  echo_stderr "source dir does not exist: $SOURCE_DIR"
  exit 1
fi

if [ ! -d "$TARGET_DIR" ]; then
  #echo_stderr "target dir does not exist: $TARGET_DIR"
  #exit 1
  mkdir -p "$TARGET_DIR"
fi


echo_stderr "* Unpack from '$SOURCE_DIR' to '$TARGET_DIR'"
# Remove any leftover tmp files
#find "${TARGET_DIR}" -type f -name '*.tmp' -exec rm -f {} \;

for IMAGE in "$SOURCE_DIR/"*-qemu.x86_64.qcow2.xz; do
  UNPACKED_IMAGE=$(basename -s .xz $IMAGE)
  if [ -f "$TARGET_DIR/$UNPACKED_IMAGE" ] ; then
	  continue
  fi
  TARGET="$TARGET_DIR/$UNPACKED_IMAGE"
  echo_stderr "  Unpacking '$IMAGE' to '$TARGET'"
  cat $IMAGE | xz -d >"$TARGET.tmp"
  mv "$TARGET.tmp" "$TARGET"
done 

MAX=3
PATTERN="fedora-coreos-*-qemu.x86_64.qcow2"
echo_stderr "* Cleanup $PATTERN max $MAX files"
find "${TARGET_DIR}" -maxdepth 1 -name "$PATTERN"| sort -Vr | awk -v MAX=$MAX '{ if ( NR > MAX ) print }' \
| while read -r FILENAME; do rm -f "${FILENAME}" ; done


