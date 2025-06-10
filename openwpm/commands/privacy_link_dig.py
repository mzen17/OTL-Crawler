import os
import time
import logging
import urllib.parse

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket
from bs4 import BeautifulSoup
import html2text


class DNSMPISearch(BaseCommand):
    """Find <a> tags by VISIBLE TEXT (DNSMPI / Privacy Policy / Do-Not-Sell phrases),
       then for each href: re-find it, click, save HTML, and return."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    def __repr__(self) -> str:
        return "DNSMPISearch"

    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        original_url = webdriver.current_url
        self.logger.info("Scanning %s for qualifying <a> text", original_url)

        # 1. All target phrases, lowercase
        target_phrases = [
            "dnsmpi",
            "privacy policy",
            "do not sell my information",
            "do not sell my info",
            "do not sell my personal info",
            "do not sell or share my personal information",
            "do not sell or share my information",
            "do not sell or share my info",
            "do not sell or share my personal info",
        ]

        # 2. First, collect hrefs of any <a> whose VISIBLE text contains a target phrase
        hrefs_to_click = []
        all_links = webdriver.find_elements(By.TAG_NAME, "a")
        hrefs_to_click = [
            link.get_attribute("href")
            for link in all_links
            if link.get_attribute("href") and any(
                phrase in ((link.text or "").strip().lower())
                for phrase in target_phrases
            )
        ]
        
        self.logger.info("hrefs: %s", hrefs_to_click)

        for url in hrefs_to_click:
            try:
                webdriver.get(url)
                time.sleep(2)

                print("HELLO?")
                page_html = webdriver.page_source

                # parse the page HTML

                soup = BeautifulSoup(page_html, "html.parser")
                body = soup.body or soup

                # convert to Markdown
                converter = html2text.HTML2Text()
                converter.ignore_images = False
                converter.ignore_links = False
                markdown = converter.handle(str(body))

                # construct a filename based on the URL
                parsed = urllib.parse.urlparse(url)
                safe_netloc = parsed.netloc.replace(".", "_")
                filename_only = f"{safe_netloc}.md"

                # Use manager_params.data_directory to construct the output path
                pages_dir = manager_params.data_directory / "pages"
                os.makedirs(pages_dir, exist_ok=True)
                path = pages_dir / filename_only

                # write Markdown to disk
                with open(path, "w", encoding="utf-8") as f:
                    f.write(markdown)
                self.logger.info("Converted page %s to Markdown at %s", url, path)
            except Exception as e:
                self.logger.error("Error processing %s: %s", url, e)

