#! /bin/bash

SL_MARKETPLACE_URL_BASE='https://marketplace.stratuslab.eu/marketplace/metadata/'

VMID_LIST="\
KqU_1EZFVGCDEhX9Kos9ckOaNjB \
PIDt94ySjKEHKKvWrYijsZtclxU \
JcqGhHxmTRAEpHMmRF-xhSTM3TO"

function get_one()
{
    wget -O $1 $2
    RET=$?
    if [ ${RET} -eq 0 ]; then
	[ -f ../$1 ] || ln -s download/$1 ..
    else
	rm $1
    fi
    return ${RET}
}

for vmid in ${VMID_LIST}; do
    get_one ${vmid}.xml ${SL_MARKETPLACE_URL_BASE}${vmid}?media=xml
    #~ if [ $? -eq 0 ]; then
	#~ get_one ${vmid}.json ${SL_MARKETPLACE_URL_BASE}${vmid}?media=json
    #~ fi
done
