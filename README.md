# MATLCOBGT
todo script to generate routes:<br/>
    - cd data2/routes<br/>
    - $SUMO_HOME/tools/randomTrips.py -n ../mulcross.net.xml -e 500 <br/>
    - $SUMO_HOME/tools/assign/duaIterate.py -n ../mulcross.net.xml -t trips.trips.xml -l 3<br/>
    - cd ../..
