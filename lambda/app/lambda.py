import yaml
from app.enchantments import EnchantmentsHelper
from app.aws import SiteTableDao, SiteTopicDao

def handler(event, context):
    with open('enchantments.yml') as configStream:
        config = yaml.safe_load(configStream)

    siteTableDao = SiteTableDao(config['sitesTableName'])
    siteTopicDao = SiteTopicDao(config['sitesSnsName'])

    enchantmentsHelper = EnchantmentsHelper(siteTableDao, siteTopicDao)
    enchantmentsHelper.getSites()