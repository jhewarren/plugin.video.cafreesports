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

import xbmcplugin, xbmcgui, xbmcaddon
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
        rtmp_stream = my_tsn.getRTMPStream(stream_page[1])
        if rtmp_stream == None:
            print "No RTMP stream for '" + stream_page[1]
            continue

        title = stream_page[0].title()
        
        li = xbmcgui.ListItem(title)
        li.setInfo( type="Video", infoLabels={"Title" : title})
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                    url=rtmp_stream + " live=true",
                                    listitem=li,
                                    isFolder=False)
        
    # Finish listing streams
    xbmcplugin.endOfDirectory(handle=int(sys.argv[1]))


# if the second argument is empty this is the main menu
if (len(sys.argv[2]) == 0):
    createMainMenu()
elif sys.argv[2] == '?id=tsn':
    createTSNMenu()