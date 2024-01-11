#!/bin/sh

#Bootstrap File für ycast docker container
#Variables
#RS_VERSION version of radio-streams software
#RS_STREAMS path an name of the indiviudual streams.json e.g. /radio-streams/streams.json
#RS_DEBUG turn ON or OFF debug output of ycast server else only start /bin/sh
#RS_PORT port ycast server listens to, e.g. 8080

if [ "$RS_DEBUG" = "OFF" ]; then
	/usr/bin/stream-proxy --port $RS_PORT --address 0.0.0.0 $RS_STREAMS
elif [ "$RS_DEBUG" = "ON" ]; then
	/usr/bin/stream-proxy --port $RS_PORT --address 0.0.0.0 $RS_STREAMS -v
else
	/bin/sh
fi
