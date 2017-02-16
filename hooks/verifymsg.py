#!/usr/bin/python

'''
 -- commit permission check for CVS
 
This script should be invoked by the verifymsg file in CVSROOT.

.* /usr/local/bin/verifymsg.py --repository=nameofrepo --url=https://example.com/postsai/extensions/commitstop/api.py --msgfile=%l

@author:     nhnb
@license:    MIT
'''

import base64
import getopt
import httplib
import os
import re
import subprocess
import sys
import urlparse

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    DEVNULL = open(os.devnull, 'wb')


def urlencode(value):
    """ very simple url encoding that works with really old python versions"""

    return value.replace("%", "%25").replace("&", "%26").replace("=", "%3D").replace("\r\n", " ").replace("\n", " ")


class PermissionChecker:

    def __init__(self):
        self.urls = []
        self.repository = None
        self.msg_file = None

    def read_commandline_arguments(self):
        """parse command line arguments"""

        try:
            opts, args = getopt.getopt(sys.argv[1:], "", ["url=", "repository=", "msgfile="])
        except:
            print "Command line: --repository=name --url=https://example.com/postsai/extensions/commitstop/api.py --msgfile=%l"
            sys.exit(2)

        for o, a in opts:
            if o == "--url":
                self.urls.append(a)
            elif o == "--repository":
                self.repository = a
            elif o == "--msgfile":
                self.msg_file = a

        if self.repository == None or len(self.urls) == 0:
            print "Command line: --repository=name --url=https://example.com/postsai/extensions/commitstop/api.py --msgfile=%l"
            sys.exit(2)
             

    def read_user(self):
        """ reads author from $CVS_USER or $USER"""

        if "CVS_USER" in os.environ:
            self.user = os.environ["CVS_USER"]
        else:
            self.user = os.environ["USER"]


    def read_branch(self):
        """Read the branchname by invoking cvsstatus"""

        self.branch = "HEAD"

        cvs = subprocess.Popen(["/usr/bin/cvs", "-qn", "status"], stderr=DEVNULL, stdout=subprocess.PIPE)
        stdout = cvs.communicate()[0];
        for row in stdout.splitlines():
            if "Sticky Tag:" in row:
                m = re.search("[ \t]*Sticky Tag:[ \t]*([^( \t]*)", row)
                branch = m.group(1)
                if branch != "(none)":
                    self.branch = branch
                return


    def generate_query_string(self):
        return "repository=" + urlencode(self.repository) + "&branch=" + urlencode(self.branch) + "&user=" + urlencode(self.user)


    def query_webservice(self):
        urlsuffix = "?" + self.generate_query_string()

        for url in self.urls:
            u = urlparse.urlparse(url)

            # Connect to server
            if u.scheme == "https":
                con = httplib.HTTPSConnection(u.hostname, u.port)
            else:
                con = httplib.HTTPConnection(u.hostname, u.port)

            # Send request
            headers = {"Content-Type": "application/json"}
            if not u.username == None and not u.password == None:
                headers["Authorization"] = "Basic " + base64.b64encode(u.username + ":" + u.password)
            con.request("GET", url + urlsuffix, None, headers)

            # Verify response, forward messages, set exit code
            response = con.getresponse()
            print(response.read())
            if response.status != 200:
                sys.exit(1)

        sys.exit(0)


def main(argv=None):
    checker = PermissionChecker()
    checker.read_commandline_arguments()
    checker.read_user()
    checker.read_branch()
    checker.query_webservice()

if __name__ == "__main__":
    sys.exit(main())
