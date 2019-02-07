# bittorrenthash
Monitor for and lookup bittorrent hashes

Currently no commandline switch to tell it what interface to watch, if it is different than eth2, modify the following line:

p = pcapy.open_live('eth2', 65536, True, 0)

It also assumes the following directory is there to write the logs to:

filehandle = open('/var/log/bittorrent/hashlist-' + str(now) + '.txt', 'w')

I have a nightly crontab entry to run the following script:

#!/bin/bash
d="1 days ago"
STAMP1=`date --date="$d" +"%Y%m%d"`

`kill $(ps aux | grep '[p]ython /scripts/bittorrent/bt.py' | awk '{print $2}') 2>/dev/null`
`(python /scripts/bittorrent/bt.py &) > /dev/null 2>&1`
`cat /var/log/bittorrent/bittorrent-$STAMP1.log | awk -F',' ' $5 != "" { print $0 }' | mutt -s "Bittorrent from [some server]" -- "xnih13@gmail.com"`

---

Not the most elegant, but works for the time being.

The bt.py script keeps track of hashes its already looked up and won't query google again for it during that run.  This is to keep google from thinking you are a bot and shutting you down (may have happened my first weekend run with this).  To make sure it periodically looks up that hash again in the future, I setup the restart script.   So if everything is working correctly it will only lookup a hash once every 24 hours.

Example Results from the email:

2019-02-04T21:28:20|10.0.X.Y|X.Y.224.214|DDE2F37302C02767F72A20677B77DB9289731F7A|These Things Happen Bundle - torrent,
