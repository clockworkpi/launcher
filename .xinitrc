session=${1:-gameshell}

case $session in
hdmi )
	feh --bg-center ~/launcher/sys.py/gameshell/wallpaper/desktopbg.jpg
	exec ~/launcher/load.sh &
	exec ~/launcher/sys.py/gsnotify/gsnotify-arm daemon &
	#exec /usr/bin/twm -f ~/launcher/.twmrc
	exec ~/launcher/dwm-mod
	;;
gameshell ) 
	feh --bg-center ~/launcher/sys.py/gameshell/wallpaper/loading.png
	exec ~/launcher/load.sh &
	exec ~/launcher/sys.py/gsnotify/gsnotify-arm &
	#exec awesome -c ~/launcher/awesome/rc.lua
	exec ~/launcher/dwm-mod -w
	;;
*) 
	exec $1;;
esac

