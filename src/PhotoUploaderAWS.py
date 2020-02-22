#-------------------------------------------
#
#    ESP32 WiFi Camera (OV7670 FIFO Version)
#    ESP32WiFiCAM-OV7670
#
#    file:PhotoUploaderAWS.py
#   
#-------------------------------------------
#
# Usage
#    from PhotoUploaderAWS import uploadFileAWS
#
#    url  = "https://xxx.amazonaws.com/prod/upload"  (example)
#    key  = "setYourKey"
#    file = "/SD/XXXX/SSSS"
#    (status, info) = uploadFileAWS(file, url, key)
#

import usocket
from ussl import wrap_socket
from urequests import Response 
import mylib
BUFSIZE=256


def uploadFileAWS(fileName, url, apiKey=None):

    headers = {}
    headers['Content-Type']= 'application/octet-stream'
    if apiKey:
       headers['API-Key']= apiKey
    resp = postBodyFromFile(url, headers, fileName)
    status_code = resp.status_code
    postInfo = resp.text
    resp.close()
    return (status_code, postInfo)  

#
#
# modified; get data from fileSystem and post
# Original Source:
#
#
def postBodyFromFile(url, headers, fileName):

    try:
        proto, dummy, host, path = url.split("/", 3)
    except ValueError:
        proto, dummy, host = url.split("/", 2)
        path = ""
    if proto == "https:":
        port = 443
    else:
        raise ValueError("Unsupported protocol: " + proto)

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
    ai = ai[0]

    s = usocket.socket(ai[0], ai[1], ai[2])
    try:
        s.connect(ai[-1])
        s = wrap_socket(s, server_hostname=host)
        s.write(b"%s /%s HTTP/1.0\r\n" % ('POST', path))
        if not "Host" in headers:
            s.write(b"Host: %s\r\n" % host)
        # Iterate over keys to avoid tuple alloc
        for k in headers:
            s.write(k)
            s.write(b": ")
            s.write(headers[k])
            s.write(b"\r\n")

        size = mylib.getFileSize(fileName)
        if size is None:
            raise ValueError("FileSize is None")
        s.write(b"Content-Length: %d\r\n" % size)
        s.write(b"\r\n")

        with open(fileName, 'rb') as fp:            
            while True:
                size = s.write(fp.read(BUFSIZE))
                if size == 0:
                     break

        l = s.readline()
        l = l.split(None, 2)
        status = int(l[1])
        reason = ""
        if len(l) > 2:
            reason = l[2].rstrip()
        while True:
            l = s.readline()
            if not l or l == b"\r\n":
                break
            if l.startswith(b"Transfer-Encoding:"):
                if b"chunked" in l:
                    raise ValueError("Unsupported " + l)
            elif l.startswith(b"Location:") and not 200 <= status <= 299:
                raise NotImplementedError("Redirects not yet supported")
    except OSError:
        s.close()
        raise

    resp = Response(s)
    resp.status_code = status
    resp.reason = reason
    return resp



