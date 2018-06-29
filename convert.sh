export map_path=Poa4
cd Agents
mkdir $map_path
wget https://overpass-api.de/api/map?bbox=-51.2246,-30.0407,-51.2098,-30.0206 -O $map_path/map
netconvert --guess-ramps --remove-edges.by-vclass hov,taxi,bus,delivery,transport,lightrail,cityrail,rail_slow,rail_fast,motorcycle,bicycle,pedestrian --geometry.remove --remove-edges.isolated --try-join-tls --verbose --osm-files $map_path/map --output-file $map_path/poa.net.xml
exit

export map_path=Poa4
cd Agents
$SUMO_HOME/tools/randomTrips.py -n $map_path/poa.net.xml -o $map_path/poa.trips.xml --validate
./genRoute.py -n $map_path/poa.net.xml -t $map_path/poa.trips.xml -o $map_path/poa.rou.xml -i 3
./runner.py -c $map_path/poa.sumocfg -t $map_path/tripinfo.xml --nogui


netedit $map_path/poa.net.xml
sumo-gui -c $map_path/poa.sumocfg --tripinfo-output $map_path/tripinfo2.xml
/opt/sumo/tools/assign/networkStatistics.py -t $map_path/tripinfo.xml -o $map_path/statistics.xml


$SUMO_HOME/tools/createVehTypeDistributions.py


docker rm $(docker ps -f ancestor=py-ptvsd -a -q) $(docker ps -f ancestor=sumo -a -q); docker run -it -v ${pwd}:/app -p 3000:3000 --name ptest sumo bash
docker rm $(docker ps -f ancestor=py-ptvsd -a -q) $(docker ps -f ancestor=sumo -a -q) ; docker run -it -v ${pwd}:/app -p 3000:3000 --name ptest py-ptvsd bash

--netstate-dump 

python plot_dump_net.py -v -n bs.net.xml \
 --xticks 7000,14001,2000,16 --yticks 9000,16001,1000,16 \
 --measures entered,entered --xlabel [m] --ylabel [m] \
 --default-width 1 -i base-jr.xml,base-jr.xml \
 --xlim 7000,14000 --ylim 9000,16000 -\
 --default-width .5 --default-color #606060 \
 --min-color-value -1000 --max-color-value 1000 \
 --max-width-value 1000 --min-width-value -1000  \
 --max-width 3 --min-width .5 \
 --colormap #0:#0000c0,.25:#404080,.5:#808080,.75:#804040,1:#c00000


./runner.py -c $map_path/poa.sumocfg -t $map_path/tripinfo.xml -d $map_path/poa.dum.xml -l $map_path/poa.link.xml --nogui

export DISPLAY=10.0.75.1:0

--additional-files


./runner.py -n $map_path/poa.net.xml -r $map_path/1per10.poa.rou.xml -t $map_path/1per10.tripinfo.xml  --nogui
python ./distributePriorityVehicles.py


$SUMO_HOME/tools/randomTrips.py -n $map_path/poa.net.xml -o $map_path/poa.trips.xml --validate
./genRoute.py -n $map_path/poa.net.xml -t $map_path/poa.trips.xml -o $map_path/poa.rou.xml -i 3

sumo --help | net
sumo --help | grep net
sumo --help | grep rou

python plot_tripinfo_distributions.py \
 -i mo.xml,dido.xml,fr.xml,sa.xml,so.xml \
 -o tripinfo_distribution_duration.png -v -m duration \
 --minV 0 --maxV 3600 --bins 10 --xticks 0,3601,360,14 \
 --xlabel "duration [s]" --ylabel "number [#]" \
 --title "duration distribution" \
 --yticks 14 --xlabelsize 14 --ylabelsize 14 --titlesize 16 \
 -l mon,tue-thu,fri,sat,sun --adjust .14,.1 --xlim 0,3600


./runner.py -n $map_path/poa.net.xml -r $map_path/1per10.poa.rou.xml -t $map_path/1per10.tripinfo.xml  --nogui
./runner.py -n $map_path/poa.net.xml -r $map_path/poa.rou.xml -t $map_path/1per10.tripinfo.xml  --nogui
sumo -c $map_path/poa.sumocfg --tripinfo-output $map_path/1per10.tripinfo.xml
./runner.py -n $map_path/poa.net.xml -r $map_path/1per10.poa.rou.xml -t $map_path/1per10.tripinfo.xml  --nogui
sumo-gui -c $map_path/poa.sumocfg --tripinfo-output $map_path/1per10.tripinfo.xml
./runner.py -c $map_path/poa.sumocfg -t $map_path/1per10.tripinfo.xml
ls $SUMO_HOME/
ls $SUMO_HOME/docs/tutorial/traci_tls/
cat runner.py
cat $SUMO_HOME/docs/tutorial/traci_tls/runner.py
./runner.py -c $map_path/1per10.poa.sumocfg -t $map_path/1per10.tripinfo.xml
./runner.py -c $map_path/1per10.poa.sumocfg -t $map_path/1per10.tripinfo.xml --nogui
ls $SUMO_HOME/docs/tutorial/traci_tls/
ls $SUMO_HOME/docs/tutorial/traci_tls/data/
cat $SUMO_HOME/docs/tutorial/traci_tls/data/cross.netccfg
cat $SUMO_HOME/docs/tutorial/traci_tls/data/cross.netccfg
cat $SUMO_HOME/docs/tutorial/traci_tls/data/cross.sumocfg
cat $SUMO_HOME/docs/tutorial/traci_tls/data/cross.con.xml
cat $SUMO_HOME/docs/tutorial/traci_tls/data/cross.det.xml
cat $SUMO_HOME/docs/tutorial/traci_tls/data/cross.nod.xml
cat $SUMO_HOME/docs/tutorial/traci_tls/data/cross.edg.xml
./runner.py -c $map_path/poa.sumocfg -t $map_path/1per10.tripinfo.xml --nogui