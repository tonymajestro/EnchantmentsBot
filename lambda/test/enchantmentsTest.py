import unittest
import json
import app.dateUtils
from datetime import datetime
from unittest import mock
from app.enchantments import EnchantmentsHelper
import pdb

class TestEnchantments(unittest.TestCase):
    def getData(self, dataFileName):
        with open(f'test/testData/{dataFileName}') as dataFile:
            return json.load(dataFile)

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testSnowOneDate(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None
        siteTopicDao = mock.Mock()
        oneJson = self.getData('snowOneDate.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 5, 5)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        self.assertTrue('Snow Zone' in sitesMap)
        self.assertEqual(1, len(sitesMap['Snow Zone']))

        snowDate = sitesMap['Snow Zone'][0]
        self.assertEqual('2023-06-01T00:00:00Z', snowDate.date)
        self.assertEqual(1, snowDate.spotsAvailable)

        siteTopicDao.publish.assert_called_once()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testSnowTwoDates(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None
        siteTopicDao = mock.Mock()
        oneJson = self.getData('snowTwoDates.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 5, 5)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        self.assertTrue('Snow Zone' in sitesMap)
        self.assertEqual(2, len(sitesMap['Snow Zone']))

        snowDate1 = sitesMap['Snow Zone'][0]
        snowDate2 = sitesMap['Snow Zone'][1]

        self.assertEqual('2023-06-01T00:00:00Z', snowDate1.date)
        self.assertEqual(1, snowDate1.spotsAvailable)

        self.assertEqual('2023-06-03T00:00:00Z', snowDate2.date)
        self.assertEqual(2, snowDate2.spotsAvailable)

        siteTopicDao.publish.assert_called_once()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testNoDates(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None
        siteTopicDao = mock.Mock()
        oneJson = self.getData('noDates.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 5, 5)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)
        self.assertEqual(0, len(sitesMap))

        siteTopicDao.publish.assert_not_called()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testSnowAndColchuck(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None
        siteTopicDao = mock.Mock()
        oneJson = self.getData('snowAndColchuck.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 5, 5)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        self.assertTrue('Snow Zone' in sitesMap)
        self.assertEqual(1, len(sitesMap['Snow Zone']))

        snowData = sitesMap['Snow Zone'][0]
        colchuckData = sitesMap['Colchuck Zone'][0]

        self.assertEqual('2023-06-01T00:00:00Z', snowData.date)
        self.assertEqual(1, snowData.spotsAvailable)

        self.assertEqual('2023-06-02T00:00:00Z', colchuckData.date)
        self.assertEqual(2, colchuckData.spotsAvailable)

        siteTopicDao.publish.assert_called_once()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testDateInThePast(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None
        siteTopicDao = mock.Mock()
        oneJson = self.getData('snowOneDate.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 7, 1)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        self.assertEqual(0, len(sitesMap))

        siteTopicDao.publish.assert_not_called()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testOneDateInPastOneInFuture(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None
        siteTopicDao = mock.Mock()
        oneJson = self.getData('snowTwoDates.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 6, 2)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        snowData = sitesMap['Snow Zone'][0]

        self.assertEqual('2023-06-03T00:00:00Z', snowData.date)
        self.assertEqual(2, snowData.spotsAvailable)

        siteTopicDao.publish.assert_called_once()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testAlreadyAlerted(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = {
            'Item': {
                'siteId': '23',
                'siteName': 'Snow Zone',
                'date': '2023-06-01T00:00:00Z',
                'spotsAvailable': 1
            }
        }

        siteTopicDao = mock.Mock()
        oneJson = self.getData('snowOneDate.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 4, 1)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        self.assertEqual(0, len(sitesMap))

        siteTopicDao.publish.assert_not_called()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testTooManyDates(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None

        siteTopicDao = mock.Mock()
        oneJson = self.getData('tooManyDates.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 4, 1)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        self.assertEqual(0, len(sitesMap))

        siteTopicDao.publish.assert_not_called()

    @mock.patch.object(app.dateUtils, 'datetime', mock.Mock(wraps=datetime)) 
    def testTooManyDatesWithCurrentDateInMiddle(self):
        siteTableDao = mock.Mock()
        siteTableDao.getSite.return_value = None

        siteTopicDao = mock.Mock()
        oneJson = self.getData('tooManyDates.json')
        app.dateUtils.datetime.now.return_value=datetime(2023, 6, 12)

        enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
        sitesMap = enchantmentsHelper.getSites(data=oneJson)

        self.assertEqual(0, len(sitesMap))

        siteTopicDao.publish.assert_not_called()

if __name__ == '__main__':
    unittest.main()

