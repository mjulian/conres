#!/usr/bin/python
import os
import json
import sys
import MySQLdb

inputData = open(sys.argv[1])
jsonData = json.load(inputData)
con = MySQLdb.Connection('localhost', 'mjulian', 'mjulian', 'conres')
cursor = con.cursor()

cursor.execute("""select count(*) from conferences where name = '%s' and start = '%s' and end = '%s' and numAttendees = '%s'""" % (jsonData['conference']['name'], jsonData['conference']['start'], jsonData['conference']['end'], jsonData['conference']['numAttendees']))
rowCount = cursor.fetchone()

if rowCount[0] < 1:
    print "Conference: ", jsonData['conference']['name']
    cursor.execute("""insert into conferences (name, start, end, numAttendees) values ('%s', '%s', '%s', '%s')""" % (jsonData['conference']['name'], jsonData['conference']['start'], jsonData['conference']['end'], jsonData['conference']['numAttendees']))
    con.commit()
    cursor.execute("""select last_insert_id()""")
    confID = cursor.fetchone()
else:
    print "Conference: ", jsonData['conference']['name'], " EXISTS"
    print "Cancelling import -- Check your database or JSON data"
    sys.exit()

cursor.execute("""select count(*) from entities where name = '%s' and city = '%s' and state = '%s' and zip = '%s'""" % (jsonData['venue']['name'], jsonData['venue']['city'], jsonData['venue']['state'], jsonData['venue']['zip']))
rowCount = cursor.fetchone()

if rowCount[0] < 1:
    print "Venue: ", jsonData['venue']['name']
    cursor.execute("""insert into entities (name, city, state, zip) values ('%s', '%s', '%s', '%s')""" % (jsonData['venue']['name'], jsonData['venue']['city'], jsonData['venue']['state'], jsonData['venue']['zip']))
    con.commit()
    cursor.execute("""select last_insert_id()""")
    venueID = cursor.fetchone()
else:
    print "Venue: ", jsonData['venue']['name'], " exists, grabbing existing venue ID"
    cursor.execute("""select id from entities where name = '%s'""" % x['venue']['name'])
    venueID = cursor.fetchone()

cursor.execute("""insert into conferenceVenue (venueID, conferenceID) values ('%s', '%s')""" % (venueID[0], confID[0]))
con.commit()

for x in jsonData['sponsors']:
    cursor.execute("""select count(*) from entities where name = '%s'""" % x['sponsor'])
    rowCount = cursor.fetchone()
    if rowCount[0] < 1:
        print "Sponsor: ", x['sponsor']
        cursor.execute("""insert into entities (name) values ('%s')""" % x['sponsor'])
        con.commit()
        cursor.execute("""select last_insert_id()""")
        sponsorID = cursor.fetchone()
    else:
        print "Sponsor: ", x['sponsor'], " exists, grabbing existing entry ID"
        cursor.execute("""select id from entities where name = '%s'""" % x['sponsor'])
        sponsorID = cursor.fetchone()
    cursor.execute("""insert into conferenceSponsor (conferenceID, sponsorID) values ('%s', '%s')""" % (confID[0], sponsorID[0]))
    con.commit()

for x in jsonData['presentations']:
    cursor.execute("""select count(*) from entities where name = '%s'""" % x['speaker'])
    rowCount = cursor.fetchone()
    if rowCount[0] < 1:
        print "Speaker: ", x['speaker']
        cursor.execute("""insert into entities (name) values ('%s')""" % x['speaker'])
        con.commit()
        cursor.execute("""select last_insert_id()""")
        speakerID = cursor.fetchone()
    else:
        print "Speaker: ", x['speaker'], " exists, grabbing existing speaker ID"
        cursor.execute("""select id from entities where name = '%s'""" % x['speaker'])
        speakerID = cursor.fetchone()
    print "Presentation: ", x['topic'], x['type']
    cursor.execute("""insert into presentations (name, type) values ('%s', '%s')""" % (x['topic'], x['type']))
    con.commit()
    cursor.execute("""select last_insert_id()""")
    presentationID = cursor.fetchone()

    cursor.execute("""insert into conferencePresentations (conferenceID, speakerID, presentationID) values ('%s', '%s', '%s')""" % (confID[0], speakerID[0], presentationID[0]))
    con.commit()

inputData.close()
