import time

from selenium import webdriver

from captchamonitor.fetchers.base_fetcher import BaseFetcher


class OperaBrowser(BaseFetcher):
    """
    Inherits and extends the BaseFetcher class to fetch URLs with Opera Browser

    :param BaseFetcher: Inherits the BaseFetcher class
    :type BaseFetcher: BaseFetcher class
    """

    method_name_in_db = "opera_browser"

    def setup(self) -> None:
        """
        Prepares and starts the Opera Browser for fetching
        """
        self.container_host = self._config["docker_opera_browser_container_name"]
        self.container_port = self._config["docker_opera_browser_container_port"]

        self._desired_capabilities = webdriver.DesiredCapabilities.OPERA.copy()

        # Perform the rest of the common setup
        self._setup_common_chromium_based_fetcher()

    def connect(self) -> None:
        """
        Connects Selenium driver to Opera Browser Container
        """
        self._connect_to_selenium_remote_web_driver(
            container_name="Opera Browser",
            desired_capabilities=self._desired_capabilities,
            command_executor=self._selenium_executor_url,
            options=self._selenium_options,
        )

        # Allows some time for HAR export trigger extension to initialize.
        # Don't remove this sleep, otherwise HAR export trigger extension returns
        # nothing and causes trouble with Opera Browser
        time.sleep(1)

    def fetch(self) -> None:
        """
        Fetches the given URL using Opera Browser
        """
        self._fetch_with_selenium_remote_web_driver()
