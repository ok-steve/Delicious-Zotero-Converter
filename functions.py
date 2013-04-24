from datetime import datetime
import re

# Sanitizes HTML values in elements
def convert_html_entities(elem, attr):
    xml_dict = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": "&apos;"}

    attrib_val = elem.attrib[attr]

    for key, val in xml_dict.items():
        if key == "&" and attrib_val.find(key) > -1:
            temp = attrib_val[attrib_val.find(key):attrib_val.find(';', attrib_val.find(key)+1)+1]
            if temp not in xml_dict.values():
                attrib_val = attrib_val.replace(key, val)
            elif var.find(key) > -1:
                attrib_val = attrib_val.replace(key, val)

    return attrib_val

# Converts 1 Delicious post to 1 MODS record
def convert_record(elem):
    record = {}

    # In Delicious data, but not used
    # record['hash'] = elem.attrib['hash']
    # record['private'] = elem.attrib['private']
    # record['shared'] = elem.attrib['shared']

    record['href'] = convert_html_entities(elem, 'href')

    record['description'] = convert_html_entities(elem, 'description')

    tags = elem.attrib['tag']
    if tags != "":
        record['tags'] = tags.split()

    time = elem.attrib['time']
    for letter in ['T', 'Z']:
        time = time.replace(letter, ' ')
    record['time'] = time

    extended = elem.attrib['extended']
    if extended != "":
        record['extended'] = convert_html_entities(elem, 'extended')

    return record

# Loops through all Delicious bookmarks and runs convert_record function
def convert_to_mods(l):
    posts = []

    for element in l:
        post = convert_record(element)

        posts.append(post)

    return posts

# Constructs the URL to fetch bookmarks from Delicious

def build_url(fr, to, tg):
    base_url = 'https://api.del.icio.us/v1/posts/all'

    # Put all variables into a list
    filt_lst = []

    if not fr == None:
        fr = 'fromdt=%s' % fr
        filt_lst.append(fr)

    if not to == None:
        to = 'todt=%s' % to
        filt_lst.append(to)

    if not tg == None:
        for tag in tg:
            tag = 'tag=%s' % tag
            filt_lst.append(tag)

    # Create string from the list of filters
    tmp_str = ''
    for i in range(len(filt_lst)):
        if tmp_str == '':
            tmp_str = '?' + filt_lst[0]
        else:
            tmp_str += '&' + filt_lst[i]

    url = base_url + tmp_str

    return url

# Takes form input and creates
def clean_date(m, d, y, direction='to'):

    now = datetime.now()

    # Create initial datetime object with time filled in to the maximum range
    if direction == 'to':
        dt = datetime.now()
    else:
        dt = datetime(1900, 01, 01, 0, 0, 0)

    # Convert the form input
    m = int(m)
    d = int(d)

    # If no date filled in, then skip and return None
    if m == 1 and d == 1 and y == '':
        return None

    # If the year's filled in check to see if it's a number, else consider it as a blank
    try:
        y = int(y)
    except:
        y = ''

    # Guess a year if it's not filled in
    if y == '':
        if direction == 'to':
            y = int(now.year)
        else:
            y = 1900

    dt = dt.replace(year=y, month=m, day=d)
    dt = dt.strftime('%Y-%m-%dT%H:%M:%SZ')

    return dt

def clean_tags(t):
    if t == '':
        return None

    lst = re.split('\,| ', t)

    for tag in lst:
        if tag == '':
            lst.pop(lst.index(tag))

    return lst
