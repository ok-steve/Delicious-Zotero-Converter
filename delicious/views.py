import base64, urllib2
import xml.etree.ElementTree as ET

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context
from django.template.loader import get_template

from delicious.forms import ApiForm
from delicious.functions import convert_html_entities, convert_to_mods, clean_date, clean_tags, build_url


# Create your views here.
def delicious_handler(request):

    params = {}

    params['form'] = ApiForm()

    if request.method == 'POST':
        form = ApiForm(request.POST)
        if form.is_valid:
            #Get variables from form
            un = request.POST['username']
            pw = request.POST['password']

            from_month = request.POST['from_month']
            from_day = request.POST['from_day']
            from_year = request.POST['from_year']
            to_month = request.POST['to_month']
            to_day = request.POST['to_day']
            to_year = request.POST['to_year']
            tags = request.POST['tags']

            # Cleans optional data
            from_date = clean_date(from_month, from_day, from_year, 'from')
            to_date = clean_date(to_month, to_day, to_year)
            tag_list = clean_tags(tags)

            # Create URL with filters
            url = build_url(from_date, to_date, tag_list)
            #return render_to_response('delicious/delicious.html', {'error': url})

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
                return render_to_response('delicious/delicious.html', params)

            bookmarks = result.read()

            #Process form input
            tree = ET.fromstring(bookmarks)
            lst = tree.findall('post')
            if len(lst) == 0:
                params['error'] = 'Delicious returned no results, please check your entries and try again.'
                return render_to_response('delicious/delicious.html', params)

            params['posts'] = convert_to_mods(lst)

            #Render templates
            t = get_template('delicious/delicious.xml')
            html = t.render(Context(params))
            response = HttpResponse(html, mimetype='application/x-download')
            response['Content-Disposition'] = 'attachment; filename=zotero.xml'
            return response

    #Show the initial Delicious converter start page
    else:
        return render_to_response('delicious/delicious.html', params)
