import os
import pycurl
import sys
import time
import urllib2
import hashlib

from threading import Thread

class Download(Thread):
    _dst_path = ""
    _is_finished = False
    _is_successful = False
    _errors = []
    _HashFunc = None
    _HashValue = ""

    def __init__(self, url, path, cookies=False, useragent=False):
        super(Download, self).__init__()
        self.url = url
        self.path = path
        self.useragent = useragent
        self.cookies = cookies
        self.downloaded = 0
        
        self.progress = { 'downloaded': 0, 'total': 0, 'percent': 0,'stopped':False }
        self.stop = False
        self.filename = ""
    
    def isFinished(self):
        return self._is_finished

    def isSuccessful(self):
        return self._is_successful

    def get_dest(self):
        return self._dst_path

    def get_errors(self):
        return self._errors

    def run(self):
        
        c = pycurl.Curl()
        c.setopt(pycurl.URL, self.url)
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.NOBODY, 1)

        c.setopt(pycurl.CONNECTTIMEOUT, 10)
        
        if self.useragent:
            c.setopt(pycurl.USERAGENT, self.useragent)
        
        # add cookies, if available
        if self.cookies:
            c.setopt(pycurl.COOKIE, self.cookies)
        c.perform()
        realurl = c.getinfo(pycurl.EFFECTIVE_URL)
        
        self.filename = realurl.split("/")[-1].strip()
        
        c = pycurl.Curl()
        c.setopt(pycurl.CONNECTTIMEOUT, 10)
        c.setopt(pycurl.URL, realurl)
        c.setopt(pycurl.FOLLOWLOCATION, 0)
        c.setopt(pycurl.NOPROGRESS, False)
        c.setopt(pycurl.XFERINFOFUNCTION, self.getProgress)
        if self.useragent:
            c.setopt(pycurl.USERAGENT, self.useragent)
        
        # configure pycurl output file
        if self.path == False:
            self.path = os.getcwd()
        filepath = os.path.join(self.path, self.filename)
            
        if os.path.exists(filepath):## remove old file,restart download 
            os.system("rm -rf " + filepath)
            f = open(filepath, "wb")
        else:
            f = open(filepath, "wb")
        
        c.setopt(pycurl.WRITEDATA, f)
        
        self._dst_path = filepath

        # add cookies, if available
        if self.cookies:
            c.setopt(pycurl.COOKIE, self.cookies)
    
        # download file
        try:
            c.perform()
        except pycurl.error, error:
            errno,errstr = error
            print("curl error: %s" % errstr)
            self._errors.append(errstr)
            self.stop = True
            self.progress["stopped"] = True
        finally:

            code = c.getinfo( c.RESPONSE_CODE )
            c.close()            
            self._is_finished = True
        
            if self.progress["percent"] < 100:
                self._is_successful = False
            else:
                if self._HashFunc != None:
                    hashed = self.hashlib_hash(self._HashFunc, self._dst_path)
                    if hashed == self._HashValue:
                        self._is_successful= True
                    else:
                        self._is_successful = False
                        self._errors.append("hash failed")
                else:
                    if code != 200:
                        self._is_successful = False
                        os.system("rm -rf " + self._dst_path) ## clear garbage file
                        self._errors.append("response error %d " % code)
                    else:
                        self._is_successful = True ## 100% downloaded without hash check
 
    def getProgress(self,download_t, download_d, upload_t, upload_d):
        if download_t and download_d:
            self.progress['downloaded'] = download_d + self.downloaded
            self.progress['total'] = download_t + self.downloaded 
            self.progress['percent'] = ( float(self.progress['downloaded']) / float(self.progress['total'])) * 100.0
            self.progress["stopped"] = False            
        if self.stop:
            self.progress["stopped"] = True
            return 1
    
    def hashlib_hash(method,fname): #eg: method == hashlib.md5(),function pointer
        hash_ = method
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_.update(chunk)

        return hash_.hexdigest()

    def add_hash_verification(self,method_name,method_value):
        if method_name == "md5":
            self._HashFunc = hashlib.md5()
        else:
            self._HashFunc = None
 
        self._HashValue = method_value

    def get_progress(self):
        return self.progress["percent"]
    
    def stop(self):
        self.stop = True
 
    def cancel(self):
        # sets the boolean to stop the thread.
        self.stop = True
        
def main():
    from optparse import OptionParser
    
    parser = OptionParser(usage="%prog [options] <url>")
    parser.add_option(  "-p", "--path", default=False, dest="path", help="download file to PATH", metavar="PATH")
    parser.add_option(  "-c", "--cookies", default=False, dest="cookies", help="specify cookie(s)", metavar="COOKIES")
    opts, args = parser.parse_args()

    if len(args) == 0:
        parser.error("No url supplied")
    
    for url in args:
        print("Downloading: %s" % url)
        if opts.path:
            print("to: %s" % opts.path)
        else:
            print("to current directory")
        d = Download(url, opts.path, opts.cookies)
        d.start()

        last_downloaded = 0
        sleep_time = 0.05
        while 1:
            try:
                progress = d.progress['percent']
                
                download_dx = d.progress["downloaded"] - last_downloaded

                speed = float(download_dx) / ( sleep_time * 1000.0)
                
                last_downloaded = d.progress["downloaded"]
                
                if d.progress["stopped"] == True:
                    break

                print("%.2f percent | %d of %d | %.1f KB/s" % (progress, d.progress['downloaded'], d.progress['total'], speed))

                if progress == 100:
                    print("")
                    print("Download complete: %s" % d.filename)
                    break
                time.sleep(sleep_time)

            # tell thread to terminate on keyboard interrupt,
            # otherwise the process has to be killed manually
            except KeyboardInterrupt:
                d.cancel()
                break

            except:
                raise
            
if __name__ == "__main__":
    main()
