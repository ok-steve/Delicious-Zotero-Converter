#!/usr/bin/env python
import os
import webapp2
from google.appengine.ext.webapp import template

import base64, urllib2
import xml.etree.ElementTree as ET

#from django.http import HttpResponse
#from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

from forms import ApiForm
from functions import convert_html_entities, convert_to_mods, clean_date, clean_tags, build_url

# A helper to do the rendering and to add the necessary
# variables for the _base.htm template
def doRender(handler, tname = 'index.html', values = { }):
    if tname == '/' or tname == '' or tname == None:
        tname = 'index.html'
    temp = os.path.join(
        os.path.dirname(__file__), 
        'templates/' + tname)
    if not os.path.isfile(temp):
      return False

    # Make a copy of the dictionary and add basic values
    newval = dict(values)
    if not 'path' in newval:
        path = handler.request.path
        newval['path'] = handler.request.path

    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True

class MainHandler(webapp2.RequestHandler):
    def get(self):
        params = {}
        params['form'] = ApiForm()
        
        doRender(
            self, 
            'index.html', 
            params)

    def post(self):
        params = {}

        un = self.request.get('username')
        pw = self.request.get('password')

        #Get variables from form
        from_month = self.request.get('from_month')
        from_day = self.request.get('from_day')
        from_year = self.request.get('from_year')
        to_month = self.request.get('to_month')
        to_day = self.request.get('to_day')
        to_year = self.request.get('to_year')
        tags = self.request.get('tags')

        # Cleans optional data
        from_date = clean_date(from_month, from_day, from_year, 'from')
        to_date = clean_date(to_month, to_day, to_year)
        tag_list = clean_tags(tags)

        # Create URL with filters
        url = build_url(from_date, to_date, tag_list)

        # Makes request
        req = urllib2.Request(url)

        base64string = base64.encodestring('%s:%s' % (un, pw))[:-1]

        req.add_header('Authorization', 'Basic %s' % base64string)

        try:
            result = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            if e.code == 401:
                params['error'] = 'Please enter your correct Delicious username and password.'
            elif e.code == 500:
                params['error'] = 'There was an error with the request. Please limit your results and try again. Delicious can only export 1,000 records at a time.'
            else:
                params['error'] = e.code
            return doRender(self, 'index.html', params)

        bookmarks = result.read()

        #Process form input
        tree = ET.fromstring(bookmarks)
        lst = tree.findall('post')
        if len(lst) == 0:
            params['error'] = 'Delicious returned no results, please check your entries and try again.'
            return doRender(self, 'index.html', params)

        params['posts'] = convert_to_mods(lst)

        #Render templates
        #t = get_template('delicious.xml')
        #html = t.render(Context(params))
        #response = HttpResponse(html, mimetype='application/x-download')
        
        
        self.response.headers["Content-Type"] = "application/x-download"
        self.response.headers['Content-Disposition'] = 'attachment; filename=zotero.xml'
        path = os.path.join(os.path.dirname(__file__), 'templates/delicious.xml')
        self.response.out.write(template.render(path, params))
                #return doRender(self, 'delicious.xml', params)
        #return self.response.out.write(params)

app = webapp2.WSGIApplication([
    ('/', MainHandler)
], debug=True)