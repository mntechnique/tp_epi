# -*- coding: utf-8 -*-
from boto.mws import connection
import time
from jinja2 import Environment, PackageLoader

# Amazon US MWS ID
MarketPlaceID = '13CHARMID'
MerchantID = '13DIGITID'
AccessKeyID = '20CHARACTERKEY'
SecretKey = '40CHARACTERKEY'

# env = Environment(loader=PackageLoader('boto_test', 'templates'),
#                   trim_blocks=True,
#                   lstrip_blocks=True)
#template = env.get_template('product_feed_template.xml')

# class Message(object):
#     def __init__(self, sku, title):
#         self.SKU = sku
#         self.Title = title

# feed_messages = [
#     Message('SDK1', 'Title1'),
#     Message('SDK2', 'Title2'),
# ]
# namespace = dict(MerchantId=MerchantID, FeedMessages=feed_messages)

# def make():
# feed_content = "None" #template.render(namespace).encode('utf-8')

# conn = connection.MWSConnection(
#     aws_access_key_id=AccessKeyID,
#     aws_secret_access_key=SecretKey,
#     Merchant=MerchantID)

# feed = conn.submit_feed(
#     FeedType='_POST_PRODUCT_DATA_',
#     PurgeAndReplace=False,
#     MarketplaceIdList=[MarketPlaceID],
#     content_type='text/xml',
#     FeedContent=feed_content
# )

# feed_info = feed.SubmitFeedResult.FeedSubmissionInfo
# print 'Submitted product feed: ' + str(feed_info)

# while True:
#     submission_list = conn.get_feed_submission_list(
#         FeedSubmissionIdList=[feed_info.FeedSubmissionId]
#     )
#     info =  submission_list.GetFeedSubmissionListResult.FeedSubmissionInfo[0]
#     id = info.FeedSubmissionId
#     status = info.FeedProcessingStatus
#     print 'Submission Id: {}. Current status: {}'.format(id, status)

#     if (status in ('_SUBMITTED_', '_IN_PROGRESS_', '_UNCONFIRMED_')):
#         print 'Sleeping and check again....'
#         time.sleep(60)
#     elif (status == '_DONE_'):
#         feedResult = conn.get_feed_submission_result(FeedSubmissionId=id)
#         print feedResult
#         break
#     else:
#         print "Submission processing error. Quit."
#         break