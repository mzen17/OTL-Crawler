import argparse
from pathlib import Path
from typing import Literal


from custom_command import LinkCountingCommand
from openwpm.command_sequence import CommandSequence
from openwpm.commands.browser_commands import GetCommand
from openwpm.config import BrowserParams, ManagerParams
from openwpm.storage.sql_provider import SQLiteStorageProvider
from openwpm.task_manager import TaskManager

sites = [
    "https://www.cnn.com/",
    "https://www.espn.com/",
]

NUM_BROWSERS = 1
manager_params = ManagerParams(num_browsers=NUM_BROWSERS)
browser_params = [BrowserParams(display_mode="xvfb") for _ in range(NUM_BROWSERS)]

# Update browser configuration (use this for per-browser settings)
for browser_param in browser_params:
    # Record HTTP Requests and Responses, cookie changes, navigations, js calls, webreqs, DNS
    browser_param.http_instrument = True
    browser_param.cookie_instrument = True
    browser_param.navigation_instrument = True
    browser_param.js_instrument = True
    browser_param.dns_instrument = True
    browser_param.maximum_profile_size = 1000 * (10**20)  # 50 MB = 50 * 2^20 Bytes

manager_params.data_directory = Path("./datadir/")
manager_params.log_path = Path("./datadir/openwpm.log")

with TaskManager(
    manager_params,
    browser_params,
    SQLiteStorageProvider(Path("./datadir/crawl-data.sqlite")),
    None,
) as manager:
    # Visits the sites
    for index, site in enumerate(sites):

        def callback(success: bool, val: str = site) -> None:
            print(
                f"CommandSequence for {val} ran {'successfully' if success else 'unsuccessfully'}"
            )
 
        # Parallelize sites over all number of browsers set above.
        command_sequence = CommandSequence(
            site,
            site_rank=index,
            callback=callback,
        )

        # Start by visiting the page
        command_sequence.append_command(GetCommand(url=site, sleep=3), timeout=60)
        command_sequence.append_command(LinkCountingCommand())
        manager.execute_command_sequence(command_sequence)
