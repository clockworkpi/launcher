session=${1:-gameshell}

case $session in
hdmi )
	exec ~/launcher/aria2c --conf-path=/home/cpi/launcher/aria2.conf &
	feh --bg-center ~/launcher/sys.py/gameshell/wallpaper/desktopbg.jpg
        cd ~/launcher/sys.py/ ; python appinstaller.py > /tmp/appinstaller.log & cd ~/
	exec ~/launcher/load.sh &
	exec ~/launcher/sys.py/gsnotify/gsnotify-arm daemon &
	#exec /usr/bin/twm -f ~/launcher/.twmrc
	exec ~/launcher/dwm-mod
	;;
gameshell )
	exec ~/launcher/aria2c --conf-path=/home/cpi/launcher/aria2.conf & 
	feh --bg-center ~/launcher/sys.py/gameshell/wallpaper/loading.png
        cd ~/launcher/sys.py/ ; python appinstaller.py > /tmp/appinstaller.log  & cd ~/
	exec ~/launcher/load.sh &
	exec ~/launcher/sys.py/gsnotify/gsnotify-arm &
	#exec awesome -c ~/launcher/awesome/rc.lua
	exec ~/launcher/dwm-mod -w
	;;
*) 
	exec $1;;
esac

