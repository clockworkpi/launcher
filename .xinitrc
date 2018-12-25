session=${1:-gameshell}

case $session in
hdmi )
	feh --bg-center ~/launcher/sys.py/gameshell/wallpaper/desktopbg.jpg
	exec ~/launcher/load.sh &
	exec ~/launcher/sys.py/gsnotify/gsnotify-arm daemon &
	exec /usr/bin/twm -f ~/launcher/.twmrc
	;;
gameshell ) 
	feh --bg-center ~/launcher/sys.py/gameshell/wallpaper/loading.png
	exec ~/launcher/load.sh &
	exec ~/launcher/sys.py/gsnotify/gsnotify-arm &
	exec awesome -c ~/launcher/awesome/rc.lua
	;;
*) 
	exec $1;;
esac

