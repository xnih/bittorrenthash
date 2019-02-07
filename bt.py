#!/usr/bin/env python

import pcapy
import sys
import base64
import dpkt
import socket
import urllib2
import time
from datetime import datetime

def parse_udp(hdr, buf):
  global fileoutput
  global hashList
  x = buf.find(':info_hash')
  if x > -1:
    ts = hdr.getts()[0]
    timeStamp = datetime.utcfromtimestamp(ts).isoformat()
    data = buf[x+13:x+13+20]
    hash = base64.b16encode(data)
    if hash not in hashList.keys():
      google = urllookup(hash)
      hashList[hash] = google
    else:
      google = ''

    eth = dpkt.ethernet.Ethernet(buf)
    ip = eth.data
    val = timeStamp + ',' + socket.inet_ntoa(ip.src) + ',' + socket.inet_ntoa(ip.dst) + ',' + hash + ',' + google
    #print('%s|%s|%s|%s%s' % (timeStamp, socket.inet_ntoa(ip.src), socket.inet_ntoa(ip.dst), hash, google))
    #print(val)
    fileoutput.write(val + '\n')
    fileoutput.flush()

def main(argv):
    global hashList
    global fileoutput

    print "[+] Start sniffing..."

    # Open interface for catpuring.
    p = pcapy.open_live('eth2', 65536, True, 0)
    if p.datalink() != pcapy.DLT_EN10MB:
      death("Interface not Ethernet ")

    # Set the BPF filter. See tcpdump(3).
    p.setfilter('udp')

    try:
      p.loop(-1, parse_udp)

    except KeyboardInterrupt:
        print "[!] Exiting"
        now = time.strftime("%Y%m%d")
        filehandle = open('/var/log/bittorrent/hashlist-' + str(now) + '.txt', 'w')
        for key, value in hashList.items():
          filehandle.write(str(key) + ', ' + str(value) + '\n')
        filehandle.close()

        fileoutput.close()

        sys.exit(0)

def urllookup(hash):
  google = ''
  hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
  site = 'https://www.google.com/search?hl=en&q=' + hash + '&num=3'
  req = urllib2.Request(site, headers=hdr)

  try:
    page = urllib2.urlopen(req)
  except urllib2.HTTPError, e:
    print e.fp.read()

  content = page.read()
  x = content.find('No results found for <b>' + hash + '</b>')
  if x == -1:
    content = content.replace('<h3', '\n<h3')
    content = content.replace('</h3>', '\n</h3')
    lines = content.splitlines()
    for line in lines:
      if '<h3' in line:
         x = line.find('">')
         if x > -1:
           items = line.split('"LC20lb">')
           if len(items) >= 2:
             google = google + '|' +  items[1]

  return google



if __name__ == '__main__':
  hashList = dict()
  now = time.strftime("%Y%m%d")
  fileoutput = open('/var/log/bittorrent/bittorrent-' + str(now) + '.log', 'w')

  main(sys.argv[1:])


