# This script is for automatically extracting the HB values along with their bidder.


import logging
import time

from selenium.webdriver import Firefox
from selenium.webdriver.common.by import By

from openwpm.commands.types import BaseCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.socket_interface import ClientSocket

script = """const resp = pbjs.getBidResponses();
const pairs = Object
  .values(resp)  // Parse the values out                          
  .flatMap(unit =>  // map for iterating through each value, creating a keypair for bidder + bid value (if they exist)
    unit.bids.map(bid => [
      bid.adapterCode || bid.bidderCode,   
      bid.adserverTargeting?.hb_pb          
    ])
  );
return pairs;"""

class GetPrebids(BaseCommand):
    """
    Runs the given JS snippet and stores its return value
    into the OpenWPM SQLite under extension_messages.
    """
    def __init__(self):
        super().__init__()          
        self.script = script
        self.logger = logging.getLogger("openwpm")

    def __repr__(self):
        return f"GetPrebids({self.script!r})"

    def execute(
        self,
        webdriver: Firefox,
        browser_params: BrowserParams,
        manager_params: ManagerParams,
        extension_socket: ClientSocket,
    ) -> None:
        current_url = webdriver.current_url

        time.sleep(15) # delay webdriver from pre-render
        result = webdriver.execute_script(self.script)  
        self.logger.info("The bids: %s links on %s", result, current_url)


