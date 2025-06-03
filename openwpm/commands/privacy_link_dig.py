import os
import time
import logging
import urllib.parse

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket


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
        for link in all_links:
            text = (link.text or "").strip().lower()
            if not text:
                continue
            
            for phrase in target_phrases:
                if phrase in text:
                    print(text)
                    href = link.get_attribute("href")
                    if href and href not in hrefs_to_click:
                        hrefs_to_click.append(href)
                    break
        
        if not hrefs_to_click:
            self.logger.info("No matching <a> text found on %s", original_url)
            return


        # 5. Ensure final URL is the original
        if webdriver.current_url != original_url:
            webdriver.get(original_url)
            time.sleep(2)
            self.logger.info("Returned to %s", original_url)
