#!/usr/bin/python

import tsn, sys

my_tsn = tsn.TSN()

stream_pages = my_tsn.getLiveStreamPage()
print stream_pages
if stream_pages == None:
    print "Currently, there appear to be no live streams"
    sys.exit(1)

for stream_page in stream_pages:
    
    rtmp_stream = my_tsn.getRTMPStream(stream_page[1])
    if rtmp_stream != None:
        print "RTMP available at '" + rtmp_stream + "'"
        continue
    
    http_smil = my_tsn.getHTTPSMIL(stream_page[1])
    if http_smil != None:
        print "SMIL availabele at '" + http_smil + "'"
        
        streams = my_tsn.getHTTPStreams(http_smil)
        if streams != None:
            for stream in streams:
                print stream
        else:
            print "ERROR: Unable to get streams from smil"
        continue
    
    print "\n"

sys.exit(0)
