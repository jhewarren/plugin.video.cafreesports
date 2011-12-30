import urllib, urllib2, time, random, re, xml.dom.minidom

class TSN:
    """
    Class to scrape TSN for a live stream of sports. Usually hockey
    
    @todo getVideoURL could check the JSON err variable return for further
          validation
    """

    def __init__(self):
        """
        Initialize the TSN Live Scrapper
        """
        self.LIVE_STRING = 'click here to watch'
        self.MAIN_PAGE = 'http://tsn.ca'
        self.LIVE_LINK = 'tsn.ca/live'
        self.BANNER_PREFIX = 'matchup-banner">'
        self.RTMP_ID_PREFIX = 'clipid:'
        self.HTTP_ID_PREFIX = 'mpflashvars.id = '
        self.ELEMENT_ID_PREFIX = '<element id="'
        self.URL_PREFIX = 'url:'
        self.BASE_RTMP_LOOKUP = 'http://cls.ctvdigital.net/cliplookup.aspx?'
        self.BASE_ELMNT_LOOKUP = 'http://esi.ctv.ca/datafeed/content_much.aspx?'
        self.BASE_HTTP_LOOKUP = 'http://esi.ctv.ca/datafeed/flv/urlgenjs.aspx?'


    def getLiveStreamPage(self):
        """
        Get the page that would show the stream.
        """
        
        # get the main page
        req = urllib2.Request(self.MAIN_PAGE)

        # make the request
        try:
            resp = urllib2.urlopen(req)
        except:
            print "URL error trying to open %s" + self.main_page
            return None
        
        # read the response
        page_html = resp.read().lower()

        links = []
        start_idx = 0

        while 1:

            # get the end text
            start_idx = page_html.find(self.LIVE_LINK, start_idx)
            if start_idx == -1:
                break

            # now back up to the href
            start_idx = page_html.rfind('http://', 0, start_idx)
            if start_idx == -1:
                break
            start_idx = start_idx

            # if the string starts with "'" then it ends with it too
            delim = '"'
            if page_html[start_idx - 1] == "'":
                delim = "'"

            # find the end of the link
            end_idx = page_html[start_idx:len(page_html)].find(delim)
            if end_idx == -1:
                break
            end_idx = start_idx + end_idx

            # get the link (and default our title)
            link = page_html[start_idx:end_idx]
            title = None

            # see if we are in a div
            start_idx = page_html.rfind("<div", 0, start_idx)
            div_end_idx = page_html.find("div>", start_idx)
            if start_idx > 0 and end_idx > 0:
                title = self.getTitleInDiv(link, page_html[start_idx:div_end_idx])
                
            if title == None:
                title = link

            links.append([title, link])

            # move to the next live link
            start_idx = end_idx

        return links

    def getTitleInDiv(self, link, div_html):
        
        title = link

        # see if there is an H2 to use
        match = re.search("<h2>(.*?)</h2>", div_html)
        if match != None:
            if len(match.groups()) > 0:
                return match.group(1)
            
        match = re.search("<h3>(.*?)</h3>", div_html)
        if match != None:
            if len(match.groups()) > 0:
                return match.group(1)

        return None

    def getLiveStreamPage2(self):
        """
        Get the page that would show the stream.
        """
        
        # get the main page
        req = urllib2.Request(self.MAIN_PAGE)

        # make the request
        try:
            resp = urllib2.urlopen(req)
        except:
            print "URL error trying to open %s" + self.main_page
            return None
        
        # read the response
        page_html = resp.read().lower()
        
        # get the end text
        end_idx = page_html.find(self.LIVE_STRING)
        if end_idx == -1:
            return None
        
        # get the start <div tag
        start_idx = page_html.rfind("<div", 0, end_idx)
        if start_idx == -1:
            return None
        
        # cut down to the <div containing the link
        page_html =page_html[start_idx:end_idx] 
        
        # get the start of the link
        start_idx = page_html.find("<a href")
        if start_idx == -1:
            return None
        
        # get the end of the link
        end_idx = page_html[start_idx:len(page_html)].find("\">")
        if end_idx == -1:
            return None
        
        # return the page containing the stream
        return page_html[start_idx+9:start_idx + end_idx]
    
    def getRTMPStream(self, stream_page):
        """
        Get the RTMP stream of the live event
        
        @param stream_page The page that contains the stream player. This page
                           will be parsed and the RTMP stream will be extracted.
        """
        
        # get the clip ID and ensure it is valid
        clip_id = self.getID(stream_page, self.RTMP_ID_PREFIX, ',')
        if clip_id == None:
            return None

        return self.getVideoURL(self, self.BASE_RTMP_LOOKUP, "id", stream_page,
                                clip_id)

    
    def getID(self, stream_page, prefix, delimiter):
        """
        Get the clip id from the page that contains the stream player.
        
        @param stream_page The page that contains the stream player. This page
                           will be parsed and the RTMP stream will be extracted.

        @param prefix The value prefixing the 
        """
        # get the main page
        req = urllib2.Request(stream_page)

        # make the request
        try:
            resp = urllib2.urlopen(req)
        except:
            print "URL error trying to open %s" + stream_page
            return None

        # get the page as lower case text        
        page_html = resp.read().lower()

        # find the start of the clip id
        start_idx = page_html.find(prefix)
        if start_idx == -1:
            return None
        
        # find the end index of the 
        end_idx = page_html[start_idx:len(page_html)].find(delimiter)
        if end_idx == -1:
            return None
        end_idx = end_idx + start_idx        
        
        return page_html[start_idx + len(prefix):end_idx]
        
        
    def getVideoURL(self, base, id_var, stream_page, clip_id):
        """
        Get the video URL. The URL is returned by a request like:
        
        http://cls.ctvdigital.net/cliplookup.aspx?id=547533&timeZone=-5&random=8627676

        @param clip_id the id of the clip to watch
        """
        
        # generate a random number
        random.seed()
        rand_str = str(random.randrange(1000000,9999999))
        
        # get the timezone string
        tz_str = str(-1 * time.timezone / 3600)        

        # generate the request URL        
        req_url = base
        req_url = req_url + id_var + "="+ urllib.quote_plus(clip_id)
        req_url = req_url + "&timezone=" + urllib.quote_plus(tz_str)
        req_url = req_url + "&random=" + urllib.quote_plus(rand_str)
        
        # get the main page
        req = urllib2.Request(req_url)
        req.add_header('Referer', stream_page)
        
        # make the request
        try:
            resp = urllib2.urlopen(req)
        except:
            print "URL error trying to open page"
            return None

        page_html = resp.read()
        
        # find the start index (add one for the ') 
        start_idx = page_html.find(self.URL_PREFIX)
        if start_idx == -1:
            return None
        start_idx = start_idx + 1 + len(self.URL_PREFIX)
        
        # find the end index
        end_idx = page_html[start_idx:len(page_html)].find("'")
        if end_idx == -1:
            return None
        end_idx = end_idx + start_idx
        
        return page_html[start_idx:end_idx]
    
    
    def getHTTPSMIL(self, stream_page):
        """
        Get the HTTP Streams
        """
        
        # Get the HTTP ID
        http_id = self.getID(stream_page, self.HTTP_ID_PREFIX, ';')
        if http_id == None:
            return None
        
        # Get the Element ID
        element_id = self.getHTTPElement(http_id)
        if element_id == None:
            return None
        
        return self.getVideoURL(self.BASE_HTTP_LOOKUP, "vid", stream_page, element_id)

    def getHTTPElement(self, http_id):
        """
        Get the element value for later use in getting the SMIL file
        """

        # create the request
        req_url = self.BASE_ELMNT_LOOKUP + "cid="+ urllib.quote_plus(http_id)
        req = urllib2.Request(req_url)
        
        # make the request
        try:
            resp = urllib2.urlopen(req)
        except:
            print "URL error trying to open page"
            return None

        page_html = resp.read()
        
        # find the start index (add one for the ') 
        start_idx = page_html.find(self.ELEMENT_ID_PREFIX)
        if start_idx == -1:
            return None
        start_idx = start_idx + len(self.ELEMENT_ID_PREFIX)
        
        # find the end index
        end_idx = page_html[start_idx:len(page_html)].find('"')
        if end_idx == -1:
            return None
        end_idx = end_idx + start_idx
        
        return page_html[start_idx:end_idx]


    def getHTTPStreams(self, smil_uri):
        """
        Get the smil, parse it up and return a list of lists containing names
        and streams.
        """
        req = urllib2.Request(smil_uri)
        
        # make the request
        try:
            resp = urllib2.urlopen(req)
        except:
            print "URL error trying to open page"
            return None

        dom = xml.dom.minidom.parseString(resp.read())
        head_node = dom.getElementsByTagName('head')[0]
        base_uri = None

        # loop over the meta tags and find the base video URI
        for meta in head_node.getElementsByTagName('meta'):
            
            # make sure we are dealing with httpBase
            if meta.hasAttribute('name'):
                if meta.getAttributeNode('name').value != 'httpBase':
                    continue
                
                # get the base stream URL
                if meta.hasAttribute('content'):
                    base_uri = meta.getAttributeNode('content').value
                    break
        
        # at this point we should have the base
        if base_uri == None:
            print "ERROR: unable to parse base URI."
            return None

        print "base uri is '" + base_uri + "'"

        streams = []
        body_node = dom.getElementsByTagName('body')[0]
        for video in body_node.getElementsByTagName('video'):
            
            # make sure there is a source
            if not video.hasAttribute('src'):
                continue

            # set the source and default the title value            
            source = video.getAttributeNode('src').value
            title = source
            
            # I dont know why this is needed, but it is
            source = base_uri + source + "?v=1&fp=1&r=1&g=1"

            # get an actual title
            if video.hasAttribute('system-bitrate'):
                title = video.getAttributeNode('system-bitrate').value
                title = title + " bps"

            # add the stream
            streams.append([title, source])

        return streams