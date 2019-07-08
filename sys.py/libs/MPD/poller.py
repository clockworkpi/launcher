# -*- coding: utf-8 -*- 
#

from mpd import MPDClient, MPDError, CommandError
import sys
import os


class PollerError(Exception):
    """Fatal error in poller."""


class MPDPoller(object):
    _host="/tmp/mpd/socket"
    #_host = "localhost"
    _port="6600"
    _client= None

    def __init__(self, host, port="6600"):
        self._host = host
        self._port = port
        self._client = MPDClient(use_unicode=True)
        self._client.timeout = 60*60*1000

    def connect(self):
        try:
            self._client.connect(self._host, self._port)
        # Catch socket errors
        except IOError as err:
            errno, strerror = err
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, strerror))

        # Catch all other possible errors
        except MPDError as e:
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, e))


    def disconnect(self):
        # Try to tell MPD to close the connection first
        try:
            self._client.close()

        # If that fails, ignore it and disconnect
        except (MPDError, IOError):
            pass

        try:
            self._client.disconnect()

        # Disconnecting failed, setup a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            self._client = MPDClient(use_unicode=True)
            self._client.timeout = 60*60*1000
    
    def general(self,func,*args):
        ret = None
        try:
            ret = func( *args )
        except CommandError:
            return False
        except (MPDError, IOError):
            print("first error")
            self.disconnect()

            try:
                self.connect()

            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)

            try:
                ret = func(*args)
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve current song: %s" % e)
        
        return ret
    
    def ping(self):
        return self.general(self._client.ping)
         
    def poll(self):
        song = self.general( self._client.status )
        """ 
        while playing:
        {u'songid': u'4', u'playlistlength': u'4', u'playlist': u'7', u'repeat': u'0', u'consume': u'0', u'mixrampdb': u'0.000000', u'random': u'0', u'state': u'play', u'elapsed': u'148.758', u'volume': u'100', u'single': u'0', u'time': u'149:436', u'duration': u'435.670', u'song': u'3', u'audio': u'44100:24:2', u'bitrate': u'192'}
        
        """

#        print(song)
        return song
 
    def stop(self):
        self.general(self._client.stop)
   
    def addfile(self,url):
        self.general(self._client.add, url)
 
    def delete(self,posid):
        self.general(self._client.delete,posid)
 
    def play(self,posid):

        song = self.poll()

        if "song" in song:
            if int(song["song"]) != posid:
                self.general(self._client.play,posid)
            else:
                if  "state" in song:
                    if song["state"] == "play":
                        self.general(self._client.pause)
                    elif song["state"] == "pause":
                        self.general(self._client.pause)
                    elif song["state"] == "stop":
                        self.general(self._client.play,posid)
        else:
            self.general(self._client.play,posid)
        
        self.general(self._client.setvol,100)
   
        return posid
 
    def playlist(self):
        lst  = self.general(self._client.playlistinfo)
        return lst
        for i in lst:
            if "title" in i:
                print( i["title"] )
            elif "file"  in i:
                print( os.path.basename( i["file"] ) )
    
    def listfiles(self,path):
        files = self.general(self._client.lsinfo,path)
        return files
        for i in sorted(files):
            if "directory" in i:
                print( "D %s" % i["directory"] )
            elif "file" in i:
                print(i["file"])
        
    def rootfiles(self):
        files = self.general(self._client.lsinfo, "/")
        return files
        for i in sorted(files):
            if "directory" in i:
                print( "D %s" % i["directory"] )
            elif "file" in i:
                print(i["file"])
    
def main():
    from time import sleep

    poller = MPDPoller()
    poller.connect()

    while True:
        print("poll:")
        print( poller.poll() )

        """
        print("playlist:")
        print(poller.playlist())
        print("rootfiles:")
        poller.rootfiles()
        """
        sleep(120)


if __name__ == "__main__":
    import sys

    try:
        main()

    except PollerError as e:
        print("Fatal poller error: %s" % e)
        sys.exit(1)

    except Exception as e:
        print("Unexpected exception: %s" % e)
        sys.exit(1)

    except:
        sys.exit(0)


