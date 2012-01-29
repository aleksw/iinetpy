#!/usr/bin/env python

# Small script that prints iiNet volume usage stats.
# Requires python 2.6+ with the BeautifulSoup module.

import urllib
import urllib2
import re
import math
import string
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import calendar

VOLUME_URL = "https://toolbox.iinet.net.au/cgi-bin/new/volumeusage.cgi"

USERNAME = "username" ##### REPLACE with iiNet USERNAME ######
PASSWORD = "password" ##### REPLACE with iiNet PASSWORD ######

class UsageStats(object):
    def __init__(self, period_name, usage, total):
        self.period_name = string.capwords(period_name)
        self.usage = usage
        self.total = total
        self.percentage = 0

        if self.total:
            self.percentage = math.ceil(float(self.usage)/self.total * 100)

    def __str__(self):
        if self.percentage:
            return "%s: %d of %d MB (%d%%)" % (self.period_name, self.usage, self.total, self.percentage)
        else:
            return "%s: %d MB" % (self.period_name, self.usage)

if __name__ == "__main__":

    USER_AGENT = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    REFERER = "https://toolbox.iinet.net.au"

    headers = {"User-Agent":USER_AGENT, "Referer": REFERER}
    values = dict(username=USERNAME, password=PASSWORD, action="login")
    params = urllib.urlencode(values)

    try:
        request = urllib2.Request(VOLUME_URL, params, headers)
        response = urllib2.urlopen(request)
    except Exception:
        print "Error!"
        exit(1)

    soup = BeautifulSoup(response.read())

    usageTag= soup.findAll('td', id='usage_div')[0]
    resetdatere = re.compile('.*(?P<day>\d\d+).*(?P<month>(January|February|March|April|June|July|August|September|October|November|December)).*')
    resetTag = soup.findAll('div', id='quota_reset')[0]
    resetString = " ".join(str(x) for x in resetTag.contents)
    reset_day = int(resetdatere.search(resetString).group('day'))
    reset_month = resetdatere.search(resetString).group('month')
    reset_year = int(datetime.now().year)

    reset_date = datetime.strptime("%d %s %d" % (reset_day, reset_month, reset_year), "%d %B %Y")

    time_to_reset = (reset_date - datetime.now())
    if time_to_reset.days <= 0:
        days=365
        if calendar.isleap(datetime.now().year):
            days+=1
        reset_date += timedelta(days=days)
        time_to_reset = (reset_date - datetime.now())

    days_to_reset = time_to_reset.days
    hours_to_reset = time_to_reset.seconds / 3600


    btagsre = re.compile('peak|offpeak|freezone')
    statsre = re.compile('(?P<used>\d+(\,\d)?\d*)[A-Za-z\s]*(?P<total>\d+(\,\d)?\d*)?')
    bTags = [ b for b in usageTag.findAll('b') if btagsre.match(b.string) ]
    stats = []

    for bTag in bTags:
        period = bTag.string
        nextDiv = bTag.findNext('div')
        stats_used = int(statsre.match(nextDiv.string).group('used').replace(',', ''))
        stats_total = statsre.match(nextDiv.string).group('total')
        if stats_total:
            stats_total = stats_total.replace(',', '')
        else:
            stats_total = 0

        stats_total = int(stats_total)
        stats.append(UsageStats(period, stats_used, stats_total))

    for usagestat in stats:
        print "%s" % str(usagestat)

    print "Reset in: %d days %d hours" % (days_to_reset, hours_to_reset)
    print "Updated: %s" % datetime.now().strftime("%d %B %Y %I:%M %p")


