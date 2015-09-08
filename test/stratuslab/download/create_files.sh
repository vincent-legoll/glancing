#! /bin/bash

SL_MARKETPLACE_URL_BASE='https://marketplace.stratuslab.eu/marketplace/metadata/'

VMID_LIST="\
KqU_1EZFVGCDEhX9Kos9ckOaNjB \
PIDt94ySjKEHKKvWrYijsZtclxU \
JcqGhHxmTRAEpHMmRF-xhSTM3TO"

# Not there any more
#~ BtSKdXa2SvHlSVTvgFgivIYDq--
#~ ME4iRTemHRwhABKV5AgrkQfDerA

for vmid in ${VMID_LIST}; do
    wget -O ${vmid}.xml ${SL_MARKETPLACE_URL_BASE}${vmid}?media=xml
    if [ $? -eq 0 ]; then
	wget -O ${vmid}.json ${SL_MARKETPLACE_URL_BASE}${vmid}?media=json
    else
	rm ${vmid}.xml
    fi
done
