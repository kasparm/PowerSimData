from powersimdata.utility import const
from powersimdata.scenario.state import State

import os
import glob


class Delete(State):
    """Deletes scenario.

    """

    name = "delete"
    allowed = []

    def __init__(self, scenario):
        super().__init__(scenario)

    def print_scenario_info(self):
        """Prints scenario information.

        :raises AttributeError: if scenario has been deleted.
        """
        print("--------------------")
        print("SCENARIO INFORMATION")
        print("--------------------")
        try:
            for key, val in self._scenario_info.items():
                print("%s: %s" % (key, val))
        except AttributeError:
            print("Scenario has been deleted")

    def delete_scenario(self):
        """Deletes scenario on server.

        """

        # Delete entry in scenario list
        self._scenario_list_manager.delete_entry(self._scenario_info)

        # Delete entry in execute list
        print("--> Deleting entry in execute table on server")
        entry = "^%s,extracted" % self._scenario_info["id"]
        command = "sed -i.bak '/%s/d' %s" % (entry, const.EXECUTE_LIST)
        stdin, stdout, stderr = self._ssh.exec_command(command)
        if len(stderr.readlines()) != 0:
            raise IOError("Failed to delete entry in %s on server" % const.EXECUTE_LIST)

        # Delete links to base profiles on server
        print("--> Deleting scenario input data on server")
        command = "rm -f %s/%s_*" % (const.INPUT_DIR, self._scenario_info["id"])
        stdin, stdout, stderr = self._ssh.exec_command(command)
        if len(stderr.readlines()) != 0:
            raise IOError("Failed to delete scenario input data on server")

        # Delete output profiles
        print("--> Deleting scenario output data on server")
        command = "rm -f %s/%s_*" % (const.OUTPUT_DIR, self._scenario_info["id"])
        stdin, stdout, stderr = self._ssh.exec_command(command)
        if len(stderr.readlines()) != 0:
            raise IOError("Failed to delete scenario output data on server")

        # Delete temporary folder enclosing simulation inputs
        print("--> Deleting temporary folder on server")
        tmp_dir = "%s/scenario_%s" % (const.EXECUTE_DIR, self._scenario_info["id"])
        command = "rm -rf %s" % tmp_dir
        stdin, stdout, stderr = self._ssh.exec_command(command)
        if len(stderr.readlines()) != 0:
            raise IOError("Failed to delete temporary folder on server")

        # Delete local files
        print("--> Deleting input and output data on local machine")
        local_file = glob.glob(
            os.path.join(const.LOCAL_DIR, self._scenario_info["id"] + "_*")
        )
        if local_file:
            for f in local_file:
                os.remove(f)

        # Delete attributes
        self._clean()

    def _clean(self):
        """Clean after deletion.

        """
        self._ssh.close()
        self._scenario_info = None
