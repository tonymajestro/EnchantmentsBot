import requests
import collections
import app.dateUtils as dateUtils
from app.sites import SiteData

HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0'}

START_DATES = [
    '2023-06-01T00:00:00.000Z',
    '2023-07-01T00:00:00.000Z',
    '2023-08-01T00:00:00.000Z',
    '2023-09-01T00:00:00.000Z'
]

SITE_NAME_MAP = {
    '23': 'Snow Zone',
    '29': 'Colchuck Zone',
    '30': 'Core Zone'
}

URL = 'https://www.recreation.gov/api/permits/233273/availability/month?start_date={startDate}&commercial_acct=false&is_lottery=false'
RESERVATION_URL = 'https://www.recreation.gov/permits/233273/registration/detailed-availability?date=2023-06-01'

class EnchantmentsHelper(object):
    def __init__(self, siteTableDao, siteTopicDao):
        self.siteTableDao = siteTableDao
        self.siteTopicDao = siteTopicDao
        self.availableSites = []

    def getSites(self, data=None):
        if data == None:
            for startDate in START_DATES:
                url = URL.format(startDate=startDate)
                response = requests.get(url, headers=HEADERS)
                enchantmentsData = response.json()['payload']['availability']
                self.parse(enchantmentsData)
        else:
            self.parse(data)

        if len(self.availableSites) == 0:
            print('No sites available right now.')
            return dict()

        sitesMap = self.filterSites(self.availableSites)
        if len(sitesMap) > 0:
            self.sendNotifications(sitesMap)

        return sitesMap

    def parse(self, enchantmentsData):
        for siteId, siteData in enchantmentsData.items():
            if siteId not in SITE_NAME_MAP:
                continue

            siteName = SITE_NAME_MAP[siteId]
            self.checkAvailability(siteId, siteName, siteData)

    def checkAvailability(self, siteId, siteName, siteData):
        for dateStr, dateData in siteData['date_availability'].items():
            spotsRemaining = dateData['remaining']
            if spotsRemaining > 0:
                self.availableSites.append(SiteData(siteId, siteName, dateStr, spotsRemaining))

    def filterSites(self, availableSites):
        sitesMap = collections.defaultdict(list)
        for site in availableSites:
            sitesMap[site.siteName].append(site)

        filteredSitesMap = collections.defaultdict(list)
        for siteName, sitesByName in sitesMap.items():
            if len(sitesByName) > 20:
                print(f'Ignoring {siteName} because it contains {len(sitesByName)} available spots which is probably a bug.')
                continue

            for site in sitesByName:
                if dateUtils.dateIsInThePast(site.date):
                    print(f'Ignoring {site.siteName} in {site.date} because it is in the past.')
                    continue
                if self.siteTableDao.getSite(site.siteId, site.date) is not None:
                    print(f'Ignoring {site.siteName} in {site.date} because it is already been alerted.')
                    continue

                self.siteTableDao.putSite(site.siteId, site.siteName, site.date, site.spotsAvailable)
                filteredSitesMap[siteName].append(site)

        return filteredSitesMap

    def sendNotifications(self, sitesMap):
        msg = 'Enchantment sites available:\n'
        for siteName, sites in sitesMap.items():
            siteMsg = f'Available dates for {siteName}'
            for site in sites:
                siteMsg += '\n\t{date}'.format(date=site.date)

            msg += siteMsg

        msg += '\n\n' + RESERVATION_URL
        print(msg)

        self.siteTopicDao.publish(msg)