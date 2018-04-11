from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm
from login.models import *
from newspaper.article import Article, ArticleException
import feedparser
from _datetime import datetime
import logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Fetch stories of the Sources saved, all at once...!'

    def handle(self, *args, **options):
        source_obj = Sourcing.objects.all()
        story_exist = Stories.objects.values_list('url', flat=True)

        not_rss_url = 0
        fetched_story_count = 0
        existing_story_count = len(story_exist)
        download_exception = 0
        parsing_exception = 0
        broken_rss_list = 0

        print("""\n\n
        ------------------------Started fetching Url's:------------------------
        \n
        """)

        sources = tqdm(source_obj)
        for list_item in sources:
                # Sources Progress bar
                sources.set_description('Source Completed  ')

                # Parse data from Rss Url
                feed_data = feedparser.parse(list_item.rss_url)

                # Detects if the Url is not well formed RSS
                if feed_data.bozo == 1:
                    logger.debug("Not a RSS url :    %s" % list_item.rss_url)
                    not_rss_url += 1
                else:
                    # Stories progess bar
                    story_entries = tqdm(feed_data.get('entries'))

                    """
                        # This will iterate through each story url
                        # If story url is already in list fetched from DB
                        # It will exit for that
                        # Else: It will download the story and save to Stories DB
                    """

                    for data in story_entries:
                        story_entries.set_description('Stories Completed ')
                        story_url = data.get('link')

                        # If RSS is Empty return Story listing page
                        if story_url is None:
                            logger.debug("No feed data in RSS URL:   %s" % list_item.rss_url)
                            broken_rss_list += 1
                        else:
                            if story_url not in story_exist:
                                article = Article(story_url)

                                # Use newspaper library to download the article
                                try:
                                    article.download()
                                except ArticleException as e:
                                    logger.debug("Article Download exception in : %s" % story_url)
                                    download_exception += 1

                                # Parse Article
                                try:
                                    article.parse()
                                except ArticleException as e:
                                    logger.debug("Article parse exception in : %s" % story_url)
                                    parsing_exception += 1

                                article_instance = article

                                # if Datetime is none, assign current datetime
                                if article_instance.publish_date is None:
                                    article_instance.publish_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                elif not isinstance(article_instance.publish_date, datetime.date):
                                    article_instance.publish_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                                # Check if story exist

                                story = Stories(
                                    title=article_instance.title,
                                    source=list_item,
                                    pub_date=article_instance.publish_date,
                                    body_text=article_instance.text,
                                    url=article_instance.url
                                )
                                story.save()
                                fetched_story_count += 1

        final_count = len(Stories.objects.values_list('url', flat=True))
        print("""
        
        ------------------------Finished fetching Url's:------------------------
                    
                    
                    Final Result:
                    
                        No of Existing Stories          :   {0}
                        No of New Stories Fetched       :   {1}
                        No of wrong Rss Url's           :   {2}
                        No of Broken or Empty Rss Url's :   {3}
                        No of Stories not Downloaded    :   {4}
                        No of Stories not Parsed        :   {5}
                    -------------------------------------------------
                        Total Stories                   :   {6}
                        
        ------------------------------------------------------------------------
            
        """.format(existing_story_count, fetched_story_count,
                   not_rss_url, broken_rss_list, download_exception,
                   parsing_exception, final_count))
