#!/bin/bash

FIRM=`cat /proc/driver/brcmf_fw`

if [[ $FIRM =~ .*a0.* ]]
then
	brcm_patchram_plus --patchram /lib/firmware/brcm/bcm43438a0.hcd --enable_hci --bd_addr B0:F1:EC:2D:07:5B --no2bytes --tosleep 5000 /dev/ttyS1 &
else
	brcm_patchram_plus --patchram /lib/firmware/brcm/bcm43438a1.hcd --enable_hci --bd_addr B0:F1:EC:2D:07:5B --no2bytes --tosleep 5000 /dev/ttyS1 &
fi
