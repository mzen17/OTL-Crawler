""" This file aims to demonstrate how to write custom commands in OpenWPM

Steps to have a custom command run as part of a CommandSequence

1. Create a class that derives from BaseCommand
2. Implement the execute method
3. Append it to the CommandSequence
4. Execute the CommandSequence

"""

import logging

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket
import time


class AdSearch(BaseCommand):
    """This command logs how many links it found on any given page"""

    def __init__(self) -> None:
        self.logger = logging.getLogger("openwpm")

    # While this is not strictly necessary, we use the repr of a command for logging
    # So not having a proper repr will make your logs a lot less useful
    def __repr__(self) -> str:
        return "AdSearchCommand"

    # Have a look at openwpm.commands.types.BaseCommand.execute to see
    # an explanation of each parameter
    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        current_url = webdriver.current_url
        # let PBJS populate its bid responses
        time.sleep(20)

        # grab all adslot keys from PBJS
        adslot_ids = webdriver.execute_script(
            "const resp = pbjs.getBidResponses(); return resp"
        )

        # convert dict of bid responses to a list of slot IDs
        adslot_ids = list(adslot_ids.keys())
        self.logger.info("Ad slot IDs: %s", adslot_ids)
        
        # exit early if no adslot ids found
        if not adslot_ids:
            self.logger.info("No ad slot IDs found, ending execution.")
            return
        self.logger.info("found: %s", adslot_ids)

        for slot_id in adslot_ids:
            try:
                # find the div by id and click it
                # find the ad slot container
                slot_div = webdriver.find_element(By.ID, slot_id)

                # locate the <iframe> inside the slot and scroll into view
                iframe = slot_div.find_element(By.TAG_NAME, "iframe")

                webdriver.execute_script("arguments[0].scrollIntoView(true);", iframe)
                
                # switch into the iframe context and click inside it
                webdriver.switch_to.frame(iframe)
                body = webdriver.find_element(By.TAG_NAME, "body")
                body.click()
                time.sleep(2)

                # switch back to the main document
                webdriver.switch_to.default_content()

                # take a screenshot of the full page (or crop externally if needed)
                screenshot_name = f"screenshot_{slot_id}.png"
                pages_dir = manager_params.data_directory / "ads"
                pages_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = pages_dir / screenshot_name
                webdriver.save_screenshot(str(screenshot_path))
                self.logger.info("Saved screenshot %s for slot %s", screenshot_name, slot_id)

            except Exception as e:
                self.logger.warning("Could not process slot %s: %s", slot_id, e)

            finally:
                # return to the original URL before the next iteration
                webdriver.get(current_url)
                time.sleep(2)
        
        
