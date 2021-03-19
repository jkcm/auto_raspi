
echo "16" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio16/direction
echo "1" > /sys/class/gpio/gpio16/value
sleep 5
echo "0" > /sys/class/gpio/gpio16/value
#date1=`date +%n`; while true; do 
#   echo -ne "$(date -u --date @$((`date +%n` - $date1)) +%H:%M:%S:%N)\r";
#done

date1=`date +%s%N`; while true; do     echo "$(((`date +%s%N` - $date1)/1000000))"; done
