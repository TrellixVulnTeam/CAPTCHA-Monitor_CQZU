import time
import logging
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from captchamonitor.utils.exceptions import (
    FetcherConnectionInitError,
    FetcherURLFetchError,
)


class BaseFetcher:
    """
    Base fetcher class that will inherited by the actual fetchers, used to unify
    the fetcher interfaces
    """

    def __init__(
        self, config, url, tor_launcher, timeout=30, options=None, use_tor=True
    ):
        """
        Initializes the fetcher with given arguments and tries to fetch the given
        URL

        :param url: The URL to fetch
        :type url: str
        :param tor_launcher: TorLauncher class
        :type tor_launcher: TorLauncher class
        :param timeout: Maximum time allowed for a web page to load, defaults to 30
        :type timeout: int, optional
        :param options: Dictionary of options to pass to the fetcher, defaults to None
        :type options: dict, optional
        :param use_tor: Should I connect the fetcher to Tor? Has no effect when using Tor Browser, defaults to True
        :type use_tor: bool, optional
        """
        # Public attributes
        self.url = url
        self.use_tor = use_tor
        self.timeout = timeout
        self.options = options
        self.driver = None
        self.page_source = None
        self.page_cookies = None
        self.page_title = None

        # Other required attributes
        self.tor_launcher = tor_launcher
        self.config = config
        self.selenium_options = None
        self.selenium_executor_url = None
        self.desired_capabilities = None

        self.logger = logging.getLogger(__name__)

    @staticmethod
    def get_selenium_executor_url(container_host, container_port):
        """
        Returns the command executor URL that will be used by Selenium remote webdriver

        :param container_host: Host to the Selenium remote webdriver
        :type container_host: str
        :param container_port: Port to the Selenium remote webdriver
        :type container_port: str
        :return: Command executor URL
        :rtype: str
        """
        return f"http://{container_host}:{container_port}/wd/hub"

    def connect_to_selenium_remote_web_driver(
        self,
        container_name,
        desired_capabilities,
        command_executor,
        options=None,
    ):
        """
        Connects Selenium remote driver to a browser container

        :param container_name: Name of the target browser, just will be used for logging
        :type container_name: str
        :param desired_capabilities: webdriver.DesiredCapabilities object from Selenium
        :type desired_capabilities: webdriver.DesiredCapabilities object
        :param command_executor: Command executor URL for Selenium
        :type command_executor: str
        :param options: webdriver.Options from Selenium, defaults to None
        :type options: webdriver.Options object, optional
        :raises FetcherConnectionInitError: If it wasn't able to connect to the webdriver
        """
        # Connect to browser container
        connected = False
        for _ in range(3):
            try:
                self.driver = webdriver.Remote(
                    desired_capabilities=desired_capabilities,
                    command_executor=command_executor,
                    options=options,
                )
                connected = True
                break

            except ConnectionRefusedError as exception:
                self.logger.debug(
                    "Unable to connect to the %s container, retrying: %s",
                    container_name,
                    exception,
                )
                time.sleep(3)

        # Check if connection was successfull
        if not connected:
            self.logger.warning(
                "Could not connect to the %s container after many retries",
                container_name,
            )
            raise FetcherConnectionInitError

        # Set driver timeout
        self.driver.set_page_load_timeout(self.timeout)

        # Log the current status
        self.logger.info("Connected to the %s container", container_name)

    def fetch_with_selenium_remote_web_driver(self):
        """
        Fetches the given URL with the remote web driver
        """

        try:
            self.driver.get(self.url)

        except WebDriverException as exception:
            self.logger.debug(
                "Unable to fetch %s because of: %s",
                self.url,
                exception,
            )
            raise FetcherURLFetchError from exception

        self.page_source = self.driver.page_source
        self.page_cookies = self.driver.get_cookies()
        self.page_title = self.driver.title

    def get_selenium_logs(self):
        """
        Obtains and returns all kinds of available Selenium logs

        :return: Dictionary of logs with different log types
        :rtype: dict
        """
        logs = {}
        for log_type in self.driver.log_types:
            logs[log_type] = self.driver.get_log(log_type)
        return logs

    def get_screenshot_from_selenium_remote_web_driver(self, image_type="base64"):
        """
        [summary]

        :param image_type: Type of screenshot to return, defaults to "base64"
        :type image_type: str, optional
        :return: Screenshot as png file or base64 encoded depending on selected type]
        :rtype: png file or str depending on selected type
        """
        if image_type == "base64":
            return self.driver.get_screenshot_as_base64()
        # else
        return self.driver.get_screenshot_as_png()

    def __del__(self):
        if self.driver is not None:
            self.driver.quit()
