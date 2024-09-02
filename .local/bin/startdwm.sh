# /bin/sh

setxkbmap -layout "us,ru" -option "grp:caps_toggle"
/home/lesha/.local/bin/newlook
xcompmgr &

while true; do 
	dwm 2> ~/.dwm.log
done
