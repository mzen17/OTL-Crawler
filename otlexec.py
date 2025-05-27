# This script is for automatically extracting the HB values along with their bidder.

from openwpm.commands.types import BaseCommand

class StoreJSResultCommand(BaseCommand):
    """
    Runs the given JS snippet and stores its return value
    into the OpenWPM SQLite under extension_messages.
    """
    def __init__(self, script: str):
        super().__init__()          
        self.script = script

    def __repr__(self):
        return f"StoreJSResultCommand({self.script!r})"

    def execute(
        self,
        webdriver,            
        browser_params,
        manager_params,
        extension_socket,     
    ) -> None:
        print("FOOBUZZ")
        print(type(extension_socket))
        result = webdriver.execute_script(self.script)  
        extension_socket.send({
            "type": "js_result",   # a tag you choose
            "value": result        # the actual JS return value
        })

