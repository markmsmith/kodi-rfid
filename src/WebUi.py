from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import json
from threading import Thread
import threading
import os
#import PrctlTool
import re
import urllib
import urlparse

class WebuiHTTPHandler(BaseHTTPRequestHandler):
    
    def log_message(self, format, *args):
      pass
    
    def _parse_url(self):
        # parse URL
        path = self.path.strip('/')
        sp = path.split('?')
        if len(sp) == 2:
            path, params = sp
        else:
            path, = sp
            params = None
        args = path.split('/')

        return path,params,args
    
    
    def _get_file(self, path):
      _path = os.path.join(self.server.www_directory,path)
      if os.path.exists(_path):
          try:
          # open asked file
              data = open(_path,'r').read()

              # send HTTP OK
              self.send_response(200)
              self.end_headers()

              # push data
              self.wfile.write(data)
          except IOError as e:
                self.send_500(str(e))
    
    def _get_types(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        types = self.server.app.get_availables_types()
        data = json.dumps(types)
        self.wfile.write(data)
        
    def _get_actions(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        actions = self.server.app.get_availables_actions()
        data = json.dumps(actions)
        self.wfile.write(data)
        
    def _get_addons(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        addons_raw = self.server.app.get_availables_addons()
        addons = []
        for a in addons_raw:
          addons.append({
            'id':a,
            'name': a.replace('.','_'),
            })
          data = json.dumps(addons)
        self.wfile.write(data)
    
    def _get_last(self, serial):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        data = {}
        if serial in self.server.app.last_tag:
          last = self.server.app.last_tag[serial]
          data = {'id':last}
        self.wfile.write(json.dumps(data))
    
    def _get_albums(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        albums = self.server.app.get_availables_albums()
        data = {}
        if albums is not None:
          for i,a in enumerate(albums):
              albums[i]['thumbnail'] = "%s/image/%s"%(self.server.app.args.kodiurl,urllib.quote_plus(albums[i]['thumbnail']))
          data = json.dumps(albums)
        self.wfile.write(data)
        
    def _get_artists(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        artists = self.server.app.get_availables_artists()
        data = {}
        if artists is not None:
          for i,a in enumerate(artists):
              artists[i]['thumbnail'] = "%s/image/%s"%(self.server.app.args.kodiurl,urllib.quote_plus(artists[i]['thumbnail']))
          data = json.dumps(artists)
        self.wfile.write(data)
    
    def _get_deezer(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        play = self.server.app.current_play()
        data = json.dumps(play)
        self.wfile.write(data)

    def _get_commands(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        commands =  []
        data = json.dumps(commands)
        self.wfile.write(data)

    def _get_urls(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        urls =  []
        data = json.dumps(urls)
        self.wfile.write(data)
    
    def _get_mode(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        data = json.dumps(self.server.app.name)
        self.wfile.write(data)
    
    def _get_tags(self, _serial, _type):
      self.send_response(200)
      self.send_header('Content-type','application/json')
      self.send_header('Access-Control-Allow-Origin','*')
      self.end_headers()
      tags = []
      if _type == 'album':
          tags = self.server.app.get_albums(_serial)
      elif _type == 'addon':
          tags = self.server.app.get_addons(_serial)
      elif _type == 'artist':
          tags = self.server.app.get_artists(_serial)
      elif _type == 'action':
          tags = self.server.app.get_actions(_serial)
      elif _type == 'url':
          tags = self.server.app.get_urls(_serial)
      elif _type == 'command':
          tags = self.server.app.get_commands(_serial)
      data = json.dumps(tags)
      self.wfile.write(data)
    
    def _delete(self, tag):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        self.server.app.delete_tag(tag)
        self.wfile.write(True)
    
    def _register(self, data):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        tagid = data['tagid'][0]
        serial = data['serial'][0]
        if 'albumid' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_album(serial, tagid, data['albumid'][0])
        elif 'artistid' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_artist(serial, tagid, data['artistid'][0])
        elif 'url' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_url(serial, tagid, data['url'][0])
        elif 'command' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_command(serial, tagid, data['command'][0])
        elif 'action' in data.keys():
            self.server.app.delete_tag(tagid)
            self.server.app.register_action(serial, tagid, data['action'][0])
        elif 'addon' in data.keys():
            if data['addon'][0] == 'plugin.video.youtube':
              self.server.app.delete_tag(tagid)
              playlist = ""
              video = ""
              try:
                video = data['video'][0]
              except:
                pass
              try:
                playlist = data['playlist'][0]
              except:
                pass
              self.server.app.register_youtube(tagid, playlist, video)
        self.wfile.write(json.dumps({'result':True}))
    
    def _get_tag(self, serial, tagid):
      print "received tag %s from %s"%(tagid, serial)
      self.send_response(200)
      self.send_header('Content-type','application/json')
      self.send_header('Access-Control-Allow-Origin','*')
      self.end_headers()
      self.server.app.on_tag_received(tagid, serial)
    
    def do_POST(self):
      path,params,args = self._parse_url()
      length = int(self.headers['Content-Length'])
      post = self.rfile.read(length)
      if len(args) == 1 and args[0] == 'delete.json':
        return self._delete(post)
      if len(args) == 1 and args[0] == 'register.json':
        return self._register(urlparse.parse_qs(urlparse.urlsplit(post).path))
    
    def do_GET(self):
        path,params,args = self._parse_url()
        if ('..' in args) or ('.' in args):
            self.send_400()
            return
        if len(args) == 1 and args[0] == '':
            path = 'index.html'
        elif len(args) == 1 and args[0] == 'mode.json':
            return self._get_mode()
        elif len(args) == 1 and args[0] == 'types.json':
            return self._get_types()
        elif len(args) == 1 and args[0] == 'tags.json':
          serial = ''
          if params is not None:
            m = re.match(
                r"serial=(.*)\&type=(.*)",params)
            if m is not None:
              serial = m.groups()[0]
              t = m.groups()[1]
          return self._get_tags(serial, t)
        elif len(args) == 1 and args[0] == 'last.json':
            serial = ''
            if params is not None:
              m = re.match(
                  r"serial=(.*)",params)
              if m is not None:
                serial = m.groups()[0]
            return self._get_last(serial)
        elif len(args) == 1 and args[0] == 'albums.json':
            return self._get_albums()
        elif len(args) == 1 and args[0] == 'urls.json':
            return self._get_urls()
        elif len(args) == 1 and args[0] == 'commands.json':
            return self._get_commands()
        elif len(args) == 1 and args[0] == 'artists.json':
            return self._get_artists()
        elif len(args) == 1 and args[0] == 'actions.json':
            return self._get_actions()
        elif len(args) == 1 and args[0] == 'addons.json':
            return self._get_addons()
        elif len(args) == 1 and args[0] == 'deezer.json':
            return self._get_deezer()
        elif len(args) == 1 and args[0] == 'tag.json':
            if params is not None:
              m = re.match(
                  r"serial=(.*)\&tagid=(.*)",params)
              if m is not None:
                serial,tagid = m.groups()
                return self._get_tag(serial, tagid)
        
        return self._get_file(path)
      
class WebuiHTTPServer(ThreadingMixIn, HTTPServer, Thread):
  allow_reuse_address = True
  
  def __init__(self, server_address, app, RequestHandlerClass, bind_and_activate=True):
    HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
    threading.Thread.__init__(self)
    self.app = app
    self.www_directory = "www/"
    self.stopped = False
    
  def stop(self):
    self.stopped = True
    
  def run(self):
      #PrctlTool.set_title('webserver')
      while not self.stopped:
          self.handle_request()