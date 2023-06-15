from app.sites import SiteData
import boto3

class SiteTableDao(object):
    def __init__(self, siteTableName):
        dynamoDbClient = boto3.resource('dynamodb')
        self.tableClient = dynamoDbClient.Table(siteTableName)

    def getSite(self, siteId, date):
        response = self.tableClient.get_item(
                Key={
                    'siteId': siteId,
                    'date': date
                })

        if 'Item' not in response:
            return None

        site = response['Item']
        return SiteData(site['siteId'], site['siteName'], site['date'], site['spotsAvailable'])

    def putSite(self, siteId, siteName, date, spotsAvailable):
        self.tableClient.put_item(Item={
            'siteId': siteId,
            'siteName': siteName,
            'date': date,
            'spotsAvailable': spotsAvailable
        })

class SiteTopicDao(object):
    def __init__(self, topicName):
        snsClient = boto3.resource('sns')
        self.sns = snsClient.create_topic(Name=topicName)

    def publish(self, message):
        self.sns.publish(Message=message)