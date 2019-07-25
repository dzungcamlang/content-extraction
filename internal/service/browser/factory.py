from internal.service.browser.service import IBrowser, Browser


class BrowserFactory:
    def get_browser_service(self, browser_endpoint):
        """

        Produce browser service.

        Args:
            browser_endpoint (unicode).

        """
        if issubclass(Browser, IBrowser):
            return Browser(browser_endpoint)