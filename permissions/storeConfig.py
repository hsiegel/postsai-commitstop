# The MIT License (MIT)
# Copyright (c) 2016-2017 HIS e. G.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import sys
import os

# ugly but necessary: also find packages at the root of the package tree
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import config

from configDb import writeConfigToDB
from checkPrivilege import checkLinesSyntax
from response import ret403


def storeConfig(arguments):
    """ store a new configuration in the database """
    
    if not arguments.__contains__("changeComment"):
        ret403("no changeComment")
    elif not arguments.__contains__("configText"):
        ret403("no configText.\n")
    elif not config.repository_status_permission():
        ret403("no permission to alter configuration.")
    else:
        (syntaxOkay, syntaxMsg) = checkLinesSyntax(arguments["configText"]);
        if not syntaxOkay:
            ret403("Syntax error in search configuration: " + syntaxMsg)
        else:
            username = os.environ.get("REMOTE_USER", "-")
            if "repository_status_username" in vars(config):
                username = config.repository_status_username()
            data = (arguments["configText"], username, arguments["changeComment"])
            writeConfigToDB(data)
