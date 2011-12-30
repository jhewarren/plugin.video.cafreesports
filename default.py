'''
@author: Micah Galizia <micahgalizia@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''

import xbmcplugin, xbmcgui, xbmcaddon, urllib
import tsn


def createMainMenu():
    """
    This main menu just adds all the source channels to the main menu
    """
    
    # Add TSN
    li = xbmcgui.ListItem("TSN")
    li.setInfo( type="Video", infoLabels={"Title" : "TSN"})
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                url=sys.argv[0] + "?id=tsn",
                                listitem=li,
                                isFolder=True)
    
    # Finish listing channels
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
    return None


def createTSNMenu():
    """
    Create a Menu containing the TSN streams
    """
    
    my_tsn = tsn.TSN()

    stream_pages = my_tsn.getLiveStreamPage()
    if len(stream_pages) == 0:
        print "No TSN stream pages linked"
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        return
    
    for stream_page in stream_pages:
        
        item_url = None
        is_folder = False
        
        rtmp_stream = my_tsn.getRTMPStream(stream_page[1])
        if rtmp_stream != None:
            item_url = rtmp_stream + " live=true"
        else:
            http_smil = my_tsn.getHTTPSMIL(stream_page[1])
            item_url = sys.argv[0] + "?id=smil_tsn&smil=" + urllib.quote_plus(http_smil)
            is_folder = True

        title = stream_page[0].title()
        
        li = xbmcgui.ListItem(title)
        li.setInfo( type="Video", infoLabels={"Title" : title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=item_url,
                                    listitem=li,
                                    isFolder=is_folder)
        
    # Finish listing streams
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
    return


def createTSNSMILMenu(smil_uri):
    """
    Load a TSN smil file and add the stream options to the list
    """
    print "SMIL URI IS '" + smil_uri + "'"
    
    my_tsn = tsn.TSN()
    streams = my_tsn.getHTTPStreams(smil_uri)
    
    if streams == None:
        print "Unable to parse SMIL files."
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
        return
        
    for stream in streams:
        title = stream[0]
        item_url = stream[1]
        
        li = xbmcgui.ListItem(title)
        li.setInfo( type="Video", infoLabels={"Title" : title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=item_url,
                                    listitem=li,
                                    isFolder=False)

        
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))
    return

#?id=smil_tsn&smil=http%3A%2F%2Fmanifest.ctv.ca.edgesuite.net%2FManifest%2F2011%2F12%2F29%2FDenVrsCanGeo2.smil
# if the second argument is empty this is the main menu

if (len(sys.argv[2]) == 0):
    createMainMenu()
elif sys.argv[2] == '?id=tsn':
    createTSNMenu()
elif sys.argv[2][:12] == "?id=smil_tsn":
    createTSNSMILMenu(urllib.unquote(sys.argv[2][18:len(sys.argv[2])]))