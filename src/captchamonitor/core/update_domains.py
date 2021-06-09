import logging
from typing import List
from datetime import datetime

import pytz
from sqlalchemy.orm import sessionmaker

from captchamonitor.utils.config import Config
from captchamonitor.utils.models import Domain
from captchamonitor.utils.website_parser import WebsiteParser


class UpdateDomains:
    """
    Fetches Alexa topsites and Moz500 website and parses the list of urls in the website and inserts the urls listed there into the
    database
    """

    def __init__(
        self,
        config: Config,
        db_session: sessionmaker,
        auto_update: bool = True,
    ) -> None:
        """
        Initializes UpdateDomains

        :param config: The config class instance that contains global configuration values
        :type config: Config
        :param db_session: Database session used to connect to the database
        :type db_session: sessionmaker
        :param auto_update: Should I update the website list when __init__ is called, defaults to True
        :type auto_update: bool
        """
        # Private class attributes
        self.__db_session: sessionmaker = db_session
        self.__logger = logging.getLogger(__name__)
        self.__config: Config = config

        if auto_update:
            self.__logger.info(
                "Updating the website list using the latest version of the topsites"
            )
            self.update()

    def __insert_website_into_db(self, website_list: List[str]) -> None:
        """
        Inserts given list of websites into the database

        :param website_list: List of strings containing websites
        :type website_list: List[str]
        """
        # Iterate over the websites in consensus file
        for website in website_list:
            query = self.__db_session.query(Domain).filter(Domain.domain == website)
            if query.count() == 0:
                # Add new website
                db_website = Domain(
                    domain=website,
                    supports_http=True,
                    supports_https=False,
                    supports_ftp=False,
                    supports_ipv4=True,
                    supports_ipv6=False,
                    requires_multiple_requests=True,
                )
                self.__db_session.add(db_website)
            else:
                db_website = query.first()
                db_website.updated_at = datetime.now(pytz.utc)
                db_website.domain = website
                db_website.supports_http = True
                db_website.supports_https = False
                db_website.supports_ftp = False
                db_website.supports_ipv4 = True
                db_website.supports_ipv6 = False
                db_website.requires_multiple_requests = True

        # Commit changes to the database
        self.__db_session.commit()

        self.__logger.debug("Inserted a batch of website into the database")

    def update(self) -> None:
        """
        Fetches Alexa topsites and Moz500 website and parses the list of urls in the website.
        Later, adds the websites to the database.
        """
        website = WebsiteParser()
        website.get_alexa_top_50()
        website.get_moz_top_500()
        website_list = list(website.uniq_website_list)
        self.__insert_website_into_db(website_list)
        self.__logger.info(
            "Done with updating the unique website list of both Moz and Alexa sites"
        )