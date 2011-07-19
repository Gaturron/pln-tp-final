# Scrapy settings for DCWrapper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'DCWrapper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['DCWrapper.spiders']
NEWSPIDER_MODULE = 'DCWrapper.spiders'
DEFAULT_ITEM_CLASS = 'DCWrapper.items.DcwrapperItem'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)

