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
        time.sleep(5)

        # grab all adslot keys from PBJS
        adslot_ids = webdriver.execute_script(
            "const resp = pbjs.getBidResponses(); return resp"
        )

        # convert dict of bid responses to a list of slot IDs
        adslot_ids = list(adslot_ids.keys())
        self.logger.info("Ad slot IDs: %s", adslot_ids)
        
        # let browser sleep while browser loads ads
        time.sleep(5)

        # exit early if no adslot ids found
        if not adslot_ids:
            self.logger.info("No ad slot IDs found, ending execution.")
            return
        self.logger.info("found: %s", adslot_ids)

        for slot_id in adslot_ids:
            try:
                # find the div by id and click it
                slot_div = webdriver.find_element(By.ID, slot_id)
                # ensure the ad slot div is in view
                webdriver.execute_script("arguments[0].scrollIntoView(true);", slot_div)
                # click at the center of the slot div to avoid obstructions
                webdriver.execute_script("""
                    var rect = arguments[0].getBoundingClientRect();
                    var x = rect.left + rect.width / 2;
                    var y = rect.top + rect.height / 2;
                    window.scrollTo(x, y);
                    var el = document.elementFromPoint(x - window.pageXOffset, y - window.pageYOffset);
                    if(el) el.click();
                """, slot_div)
                

                # take a screenshot of the clicked adslot
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
        
        
