#!/usr/bin/env python
import pymongo
from flask import Flask, render_template, request
from bson.objectid import ObjectId
import json

app = Flask(__name__)

@app.route('/calendarRead', method='POST')
def calendarRead():
    custom_attribute = request.forms.get('custom_attribute')

    start = int(request.forms.get('start'))
    end = int(request.forms.get('end'))

    collection = db['calendar']

    events = []

    # Ensure there is an index on start date
    collection.ensure_index([('start', 1)]);

    # Fetch the event objects from MongoDB
    recs = collection.find({'start':{'$gte': start, '$lte': end}}) # Can add filter here for customer or calendar ID, etc

    for rec in recs:
        event = rec

        # Replace the ID with its string version, since the object is not serializable this way
        event['id'] = str(rec['_id'])
        del(event['_id'])

        events.append(event)

    outputStr = json.dumps(events)
    return render_template('{{!output}}', output=outputStr)

@app.route('/calendarUpdate', method='POST')
def calendarUpdate():
    custom_attribute = request.forms.get('custom_attribute')

    collection = db['calendar']

    event = {}
    event['title'] = request.forms.get('title')

    # allDay is received from the POST object as a string - change to boolean
    allDay_str = request.forms.get('allDay')
    if(allDay_str == "true"):
        event['allDay'] = True
    else:
        event['allDay'] = False

    # We're receiving dates in ms since epoch, so divide by 1000
    event['start'] = int(request.forms.get('start'))/1000

    # Set end-date if it exists
    end = request.forms.get('end')
    if (end is not None and end != ''):
        event['end'] = int(end)/1000

    # Set entry colour if it exists
    color = request.forms.get('color')
    if (color is not None and color != ''):
        event['color'] = request.forms.get('color')

    # Add or update collection record, determined by whether it has an ID or not
    record_id = request.forms.get('id')
    if(record_id is not None and record_id != ''):
        event_id = ObjectId(record_id)
        collection.update({'_id': event_id}, event) # Update record
    else: 
        record_id = collection.insert(event) # Insert record

    # Return the ID of the added (or updated) calendar entry
    output = {}
    output['id'] = str(record_id)

    # Output in JSON
    outputStr = json.dumps(output)
    return render_template('{{!output}}', output=outputStr)

@app.route('/calendarDelete', method='POST')
def calendarUpdate():
    custom_attribute = request.forms.get('custom_attribute')
    collection = db['calendar']

    # Delete the collection record using the ID
    record_id = request.forms.get('id')
    if(record_id is not None and record_id != ''):
        event_id = ObjectId(record_id)
        collection.remove({'_id': event_id}) # Delete record


if __name__ == '__main__':
   app.debug = True  # updates the page as the code is saved
   HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
   PORT = int(os.environ.get('PORT', 443))
   app.run(host='0.0.0.0', port=PORT)
