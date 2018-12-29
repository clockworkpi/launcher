#!/bin/bash

BAT_PNT=`upower -i $(upower -e | grep 'battery') | grep -E "state|to\ full|percentage" | awk '/perc/{print $2}' | cut -d % -f1 `

if [ "$BAT_PNT" -lt "20" ]; then

	if [ "$BAT_PNT" -lt "5" ]; then
		echo '{"type":"once","content":"Low Battery: 5% of battery remaining"}'
	elif [ "$BAT_PNT" -lt "10" ]; then
		echo '{"type":"once","content":"Low Battery: 10% of battery remaining"}'
	fi

else
	echo $BAT_PNT
fi
