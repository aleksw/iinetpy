#!/usr/bin/env python

# Small script that prints iiNet volume usage stats
# Tested with python 2.6

import urllib
import urllib2
import math
import string
from datetime import datetime
from datetime import timedelta
import calendar
from xml.etree import ElementTree

VOLUME_URL = "https://toolbox.iinet.net.au/cgi-bin/new/volume_usage_xml.cgi"

USERNAME = "username" ##### replace with iinet username ######
PASSWORD= "password" ##### replace with iinet password ######

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

    doc = ElementTree.fromstring(response.read())

    tags = doc.findall("volume_usage/expected_traffic_types/type")

    stats = []

    for usage_info in tags:
        period = usage_info.attrib["classification"]
        used = int(usage_info.attrib["used"]) / 1000000 # to MB
        total = 0
        allocation_tag = usage_info.find("quota_allocation")
        if(allocation_tag is not None):
            total = int(allocation_tag.text)
        stats.append(UsageStats(period, used, total))

    reset_day = 0
    reset_day_tag = doc.find("volume_usage/quota_reset/anniversary")
    if(reset_day_tag is not None):
        reset_day = int(reset_day_tag.text)

    now = datetime.now()
    reset_month = now.date().month
    reset_year = now.date().year

    if(reset_day < now.date().day):
        if(reset_month + 1 > 12):
            reset_year += 1
            reset_month = 1
        else:
            reset_month += 1

    reset_date = datetime(reset_year, reset_month, reset_day)

    time_to_reset = (reset_date - datetime.now())
    if time_to_reset.days <= 0:
        days=365
        if calendar.isleap(datetime.now().year):
            days+=1
        reset_date += timedelta(days=days)
        time_to_reset = (reset_date - datetime.now())

    days_to_reset = time_to_reset.days
    hours_to_reset = time_to_reset.seconds / 3600

    for usagestat in stats:
        print "%s" % str(usagestat)

    print "\nReset in: %d days %d hours" % (days_to_reset, hours_to_reset)
    print "Updated: %s" % datetime.now().strftime("%d %B %Y %I:%M %p")


