#! /usr/bin/env python
#
# a skeleton script to download a set of L1, L2, L3 and L4 file using OPeNDAP.
#
#
#   2015.12.11  Yibo Jiang, version 1
#   2019.09.19  Piyush Garg, version 2 for python 3.x

##################################
# user parameters to be editted: #
##################################

# Caution: This is a Python script, and Python takes indentation seriously.
# DO NOT CHANGE INDENTATION OF ANY LINE BELOW!

# Example:
# % ./download_dataset.py -s 20100101 -f 20100205 -x JPL-L4UHfnd-GLOB-MUR
# Download the data from 1 Jan 2010 to 5 Feb 2010 for shortName JPL-L4UHfnd-GLOB-MUR.  

import sys,os
import subprocess
import time
from datetime import date, timedelta
from optparse import OptionParser
from six.moves import input
import urllib.request
#import pydap.client
import numpy as np

from xml.dom import minidom

#####################
# Global Parameters #
#####################

itemsPerPage = 10
PODAAC_WEB = 'http://podaac.jpl.nasa.gov'

###############
# subroutines #
###############

def today():
    import datetime
    todays=datetime.date.today()
    return str(todays.year)+str(todays.month).zfill(2)+str(todays.day).zfill(2)

def yesterday():
    import datetime
    yesterdays=datetime.date.today() - timedelta(days=1)
    return str(yesterdays.year)+str(yesterdays.month).zfill(2)+str(yesterdays.day).zfill(2)

def getChildrenByTitle(node):
    for child in node.childNodes:
        if child.localName=='Title':
            yield child

def parseoptions():
    usage = "Usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-x", "--shortname", help="product short name", dest="shortname")
  
    parser.add_option("-s", "--start", help="start date: Format yyyymmdd (eg. -s 20140502 for May 2, 2014) [default: yesterday %default]", dest="date0", default=yesterday())
    parser.add_option("-f", "--finish", help="finish date: Format yyyymmdd (eg. -f 20140502 for May 2, 2014) [default: today %default]", dest="date1", default=today())
  
   # Parse command line arguments
    (options, args) = parser.parse_args()

  # print help if no arguments are given
    if(len(sys.argv) == 1):
        parser.print_help()
        exit(-1)

  #if len(args) != 1:
  #      parser.error("incorrect number of arguments")

    if options.shortname == None:
        print('\nShortname is required !\nProgram will exit now !\n')
        parser.print_help()
        exit(-1)

    return( options )

def standalone_main():
    
  # get command line options:

    options=parseoptions()

    shortname = options.shortname

    date0 = options.date0
    if options.date1==-1:
        date1 = date0
    else:
        date1 = options.date1

    if len(date0) != 8:
        sys.exit('\nStart date should be in format yyyymmdd !\nProgram will exit now !\n')
    
    if len(date1) != 8:
        sys.exit('\nEnd date should be in format yyyymmdd !\nProgram will exit now !\n')

    year0=date0[0:4]; month0=date0[4:6]; day0=date0[6:8];
    year1=date1[0:4]; month1=date1[4:6]; day1=date1[6:8];

    timeStr = '&startTime='+year0+'-'+month0+'-'+day0+'&endTime='+year1+'-'+month1+'-'+day1

    print ('\nPlease wait while program searching for the granules ...\n') 

    wsurl = PODAAC_WEB+'/ws/search/granule/?shortName='+shortname+timeStr+'&itemsPerPage=1&sortBy=timeAsc'
    response = urllib.request.urlopen(wsurl)

    data = response.read()

    if (len(data.splitlines()) == 1):
        sys.exit('No granules found for dataset: '+shortname+'\nProgram will exit now !\n')
    
  #****************************************************************************
 
    r=input('OK to download?  [yes or no]: ')
    if len(r)==0 or (r[0]!='y' and r[0]!='Y'):
        print ('... no download')
        sys.exit(0)

  # main loop:
    start = time.time()
    bmore = 1
    while (bmore > 0):
        if (bmore == 1):
            urllink = PODAAC_WEB+'/ws/search/granule/?shortName='+shortname+timeStr+'&itemsPerPage=%d&sortBy=timeAsc'%itemsPerPage
        else:
            urllink = PODAAC_WEB+'/ws/search/granule/?shortName='+shortname+timeStr+'&itemsPerPage=%d&sortBy=timeAsc&startIndex=%d'%(itemsPerPage, (bmore-1)*itemsPerPage)
        bmore = bmore + 1
        response = urllib.request.urlopen(urllink)
        data = response.read()
        doc = minidom.parseString(data)

        print (urllink)
 
        numGranules = 0
        for arrays in doc.getElementsByTagName('link'):
            names = arrays.getAttribute("title")
            if names == 'OPeNDAP URL':
                numGranules = numGranules + 1
                href = arrays.getAttribute("href")
                print (href)
                ncfile = href.rsplit( ".", 1 )[ 0 ]
                head, tail = os.path.split(ncfile)
                ncout = tail
                if ncout.endswith('.bz2') or ncout.endswith('.gz'):
                    ncout = ncout.rsplit( ".", 1 )[ 0 ]
                ncout = ncout.rsplit( ".", 1 )[ 0 ]+'_subset.'+ncout.rsplit( ".", 1 )[ 1 ]
                cmd=ncfile

                status_curl, result = subprocess.getstatusoutput("which curl")
                status_wget, result = subprocess.getstatusoutput("which wget")

                if status_curl == 0:
                    cmd='curl -g "'+cmd+'" -o '+ ncout
                elif status_wget == 0:
                    cmd='wget "'+cmd+'" -O '+ ncout
                else:
                    sys.exit('\nThe script will need curl or wget on the system, please install them first before running the script !\nProgram will exit now !\n')

          #cmd = cmd.replace("http://podaac-opendap.jpl.nasa.gov", "http://opendap-uat.jpl.nasa.gov")

                print (cmd)

                os.system( cmd )
                print (ncout + ' download finished !')

        if numGranules < itemsPerPage:
            bmore = 0 

    end = time.time()
    print ('Time spend = ' + str(end - start) + ' seconds')

if __name__ == "__main__":
    standalone_main()
  



