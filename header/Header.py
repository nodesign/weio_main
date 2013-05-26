### 
#
# WEIO Web Of Things Platform
# Copyright (C) 2013 Nodesign.net, Uros PETREVSKI, Drasko DRASKOVIC
# All rights reserved
#
#               ##      ## ######## ####  #######  
#               ##  ##  ## ##        ##  ##     ## 
#               ##  ##  ## ##        ##  ##     ## 
#               ##  ##  ## ######    ##  ##     ## 
#               ##  ##  ## ##        ##  ##     ## 
#               ##  ##  ## ##        ##  ##     ## 
#                ###  ###  ######## ####  #######
#
#                    Web Of Things Platform 
#
# This file is part of WEIO
# WEIO is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# WEIO is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Authors : 
# Uros PETREVSKI <uros@nodesign.net>
# Drasko DRASKOVIC <drasko.draskovic@gmail.com>
#
###

import subprocess
import os, signal, sys
import functools
import errno
import os
from tornado import web, ioloop, iostream
sys.path.append(r'./');

# pure websocket implementation
#from tornado import websocket

import tornado_subprocess

from sockjs.tornado import SockJSRouter, SockJSConnection
from weioLib import WeioFiles

import json
import ast


# pure websocket implementation    
#class WeioEditorHandler(websocket.WebSocketHandler):
class WeioHeaderHandler(SockJSConnection):
    global weio_main
    
    """Opens editor route."""
    def on_open(self, data):
        """On open asks weio for"""
        print "WebSocket opened!"
        pass
        
    def on_message(self, data):
        self.serve(data)

# pure websocket implementation         
#    def send(self, message):
#        self.write_message(message)
        
    def serve(self, request) :
        global weio_main
        
        # parsing strings from browser
        rq = ast.literal_eval(request)
        
        # answer dictionary object
        data = {}          
        
        if 'getFileList' in rq['request'] :
            # echo given request
            data['requested'] = rq['request']
            
            # read all files paths from user directories
            data['data'] = WeioFiles.scanFolders()

            # notify what is happening at this moment
            data['status'] = "I'm ready, gimme some awesome code!"
            fileList = data 
            
            #sending
            self.send(json.dumps(data))
            
        elif 'getFile' in rq['request'] :
            # echo given request
            data['requested'] = rq['request']

            # echo given data
            data['requestedData'] = rq['data']
            
            fileInfo = rq['data']
            pathname = fileInfo['path']
            
            rawFile = WeioFiles.getRawContentFromFile(pathname)
            
            fileInfo['data'] = rawFile
            data['data'] = fileInfo

            self.send(json.dumps(data))
            
        elif 'saveFile' in rq['request']:
            # echo given request
            data['requested'] = rq['request']

            # don't echo given data to spare unnecessary communication, just return name 
            fileInfo = rq['data']
            data['requestedData'] = fileInfo['name']

            pathname = fileInfo['path']
            rawData = fileInfo['data']
            
            #print(pathname + " " + rawData)
            ret = WeioFiles.saveRawContentToFile(pathname, rawData)
            
            data['status'] = fileInfo['name'] + " is saved!"
            self.send(json.dumps(data))

            
        elif 'play' in rq['request']:
            """ This is where all the magic happens.

                "Play" button will spawn a new subprocess
                which will execute users program written in the editor.
                This subprocess will communicate with Tornado wia non-blocking pipes,
                so that Tornado can simply transfer subprocess's `stdout` and `stderr`
                to the client via WebSockets. """
                    
            
            processName = './userProjects/myFirstProject/weio_main.py'

            #launch process
            
            #weio_main = tornado_subprocess.Subprocess(self.on_subprocess_result, args=['python', processName])
            #weio_main.start()


            print("weio_main indipendent process launching...")
            #subprocess.call("python " + processName, shell=True)
            self.pipe = p = subprocess.Popen(['python', '-u', processName], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
            
            ioloopObj = ioloop.IOLoop.instance()
            
            #callback = functools.partial(self.socket_connection_ready, sock)
            callback = functools.partial(self.weio_main_handler, data)
            #ioloopObj.add_handler(sock.fileno(), callback, ioloopObj.READ)
            ioloopObj.add_handler(p.stdout.fileno(), callback, ioloopObj.READ)

            
            # Inform client the we run subprocess
            data['requestedData'] = rq['request']
            data['status'] = "weio_main.py is running!"
            self.send(json.dumps(data))
            
        elif 'stop' in rq['request']:
            # not yet implemented                
            ##weio_main.cancel()
            data = {}
            data['serverPush'] = 'stopped'
            data['status'] = "weio_main.py stopped!"
            self.send(json.dumps(data))
            
        elif 'storeProjectPreferences' in rq['request']:
            projectStore = rq['data']
            
            print(rq['data'])
            
            # echo given request
            data['requested'] = rq['request']
            data['status'] = "Your project is saved"
            self.send(json.dumps(data))
            
        elif 'runPreview' in rq['request']:
            # echo given request
            data['requested'] = rq['request']
            data['status'] = "Entering preview mode"
            self.send(json.dumps(data))
            
        elif 'addNewFile' in rq['request']:
            # this function is similar to saveFile
            
            # echo given request
            data['requested'] = rq['request']

            # don't echo given data to spare unnecessary communication, just return name 
            fileInfo = rq['data']
            data['requestedData'] = fileInfo['name']

            pathname = fileInfo['path']
            # in new file there are no data, it will be an empty string
            rawData = ""
            
            #rawData = fileInfo['data']
            
            #print(pathname + " " + rawData)
            ret = WeioFiles.saveRawContentToFile(pathname, rawData)
            
            data['status'] = fileInfo['name'] + " has been created"
            self.send(json.dumps(data))


    def weio_main_handler(self, data, fd, events):
        line = self.pipe.stdout.readline()
        if line :
            # parse incoming data
            #stdout = line.rstrip()
            stdout = line
            print(stdout)
    
            #pack and go
            data = {}
    
            data['serverPush'] = 'stdout'
            data['data'] = stdout
    
            # TODO, send this only once, at the beginning
            data['status'] = "Check output console"
    
            # this is raw output, some basic parsing is needed in javascript \n etc...
            self.send(json.dumps(data))


        if self.pipe.poll() is not None :
            """ Child is terminated """
            print "Child has terminated - removing handler"
            ioloop.IOLoop.instance().remove_handler(self.pipe.stdout.fileno())
            return