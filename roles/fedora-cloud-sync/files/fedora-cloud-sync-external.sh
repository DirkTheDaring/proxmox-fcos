#!/usr/bin/bash
set -ex
DOWNLOAD_DIR=/mnt/pve/shared/images/000
URL0=https://ftp.halifax.rwth-aachen.de/fedora/linux/releases/ #/36/Cloud/x86_64/images/

FEDORA_VERSION=$(curl -s "${URL0}" |grep -Po '(?<=href=")[^"]*'|grep -P "^[0-9]+/$"|sort -Vr |head -1)
URL1=${URL0}${FEDORA_VERSION}Cloud/x86_64/images/
BASENAME=$(curl -s $URL1|grep -Po '(?<=href=")[^"]*' | grep ".qcow2$"| sort -Vr| head -1)

URL="${URL1}${BASENAME}"

TARGET_NAME=$BASENAME


if [ -f "${TARGET_NAME}" ]; then
        echo "Already exists: ${TARGET_NAME}"
	exit 0
fi

mkdir -p "${DOWNLOAD_DIR}"

CHECKSUM_BASENAME=$(basename -s .x86_64.qcow2 "${BASENAME}"|sed s/^Fedora-Cloud-Base/Fedora-Cloud/ )-x86_64-CHECKSUM
CHECKSUM_URL=${URL1}${CHECKSUM_BASENAME}
CHECKSUM_FILENAME=${DOWNLOAD_DIR}/${CHECKSUM_BASENAME}

if [ ! -f "${CHECKSUM_FILENAME}" ]; then
  curl -s -o "${CHECKSUM_FILENAME}" "${CHECKSUM_URL}"
fi

EXPECTED_SHA256SUM=$(cat $CHECKSUM_FILENAME|grep "^SHA256.*$BASENAME"|awk '{print $NF}')
if [ -z "$EXPECTED_SHA256SUM" ]; then
    echo "Removing checksum file as it does not contain a sha256 checksum:  $CHECKSUM_FILENAME"
    rm -f "${CHECKSUM_FILENAME}"
    exit 1
fi

FILENAME="${DOWNLOAD_DIR}/${BASENAME}"

if [ ! -f "${FILENAME}" ]; then
  curl -o "${FILENAME}.tmp" "$URL"
  ACTUAL_SHA256SUM=$(sha256sum ${FILENAME}.tmp|awk '{print $1}')
  if [ "$EXPECTED_SHA256SUM" != "$ACTUAL_SHA256SUM" ]; then
      rm -f ${FILENAME}.tmp
      exit 1
  fi
  mv "${FILENAME}.tmp" "${FILENAME}"
fi

# FIXME Cleanup max 3 old cheksum + qcow files

# FIXME create a SBOM entry
