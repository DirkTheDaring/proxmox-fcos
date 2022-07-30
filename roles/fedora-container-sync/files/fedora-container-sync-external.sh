#!/usr/bin/env bash
set -e
TARGET_DIR="/var/lib/vz/template/cache"
MAX=3
URL0=https://kojipkgs.fedoraproject.org/packages/Fedora-Container-Base/

FEDORA_VERSION=$(curl -s "${URL0}" |grep -Po '(?<=href=")[^"]*'|grep -P "^[0-9]+/$"|sort -Vr |head -1)
URL1=${URL0}${FEDORA_VERSION}
LATEST=$(curl -s $URL1|grep -Po '(?<=href=")2[^"]*'|sort -Vr |head -1)
URL2="${URL1}${LATEST}images/"
BASENAME=$(curl -s "$URL2"|grep -Po '(?<=href=")[^"]*'|grep -E "\\.x86_64\\.tar\\.xz$"|sort -Vr|head -1)
URL="${URL2}${BASENAME}"

mkdir -p "${TARGET_DIR}"

FILENAME="${TARGET_DIR}/${BASENAME}"
if [ ! -f "${FILENAME}" ]; then
  echo "* Download ${FILENAME}"
  curl -s -o "${FILENAME}" "$URL"
fi

find "${TARGET_DIR}" -type f -name "*.x86_64.tar.xz"\
| sort -Vr | awk -v MAX=${MAX} '{ if ( NR > MAX ) print }'\
| while read -r FILENAME; do rm -f "${FILENAME}" ; done

