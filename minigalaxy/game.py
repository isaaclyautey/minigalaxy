import os
import re
import json


class Game:
    def __init__(self, name: str, url: str = "", game_id: int = 0, install_dir: str = "", image_url="",
                 platform="linux", dlcs=None):
        self.name = name
        self.url = url
        self.id = game_id
        self.install_dir = install_dir
        self.image_url = image_url
        self.platform = platform
        self.dlcs = [] if dlcs is None else dlcs
        self.status_file_name = "minigalaxy-info.json"
        self.status_file_path = os.path.join(self.install_dir, self.status_file_name)

    def get_stripped_name(self):
        return self.__strip_string(self.name)

    def get_install_directory_name(self):
        return re.sub('[^A-Za-z0-9 ]+', '', self.name)

    def load_minigalaxy_info_json(self):
        json_dict = {}
        if os.path.isfile(self.status_file_path):
            staus_file = open(self.status_file_path, 'r')
            json_dict = json.load(staus_file)
            staus_file.close()
        return json_dict

    def save_minigalaxy_info_json(self, json_dict):
        status_file = open(self.status_file_path, 'w')
        json.dump(json_dict, status_file)
        status_file.close()

    @staticmethod
    def __strip_string(string):
        return re.sub('[^A-Za-z0-9]+', '', string)

    def is_installed(self, dlc_title="") -> bool:
        installed = False
        json_dict = self.load_minigalaxy_info_json()
        if dlc_title:
            if "dlcs" in json_dict:
                if dlc_title in json_dict["dlcs"]:
                    if "version" in json_dict["dlcs"][dlc_title]:
                        installed = True
        else:
            if self.install_dir and os.path.exists(self.install_dir):
                installed = True
        # Start: Code for compatibility with minigalaxy 1.0
        if dlc_title and not installed:
            status = self.legacy_get_dlc_status(dlc_title)
            installed = True if status in ["installed", "updatable"] else False
        # End: Code for compatibility with minigalaxy 1.0
        return installed

    def is_update_available(self, version_from_api, dlc_title="") -> bool:
        update_available = False
        installed_version = "0"
        json_dict = self.load_minigalaxy_info_json()
        if dlc_title:
            if "dlcs" in json_dict:
                if dlc_title in json_dict["dlcs"]:
                    if "version" in json_dict["dlcs"][dlc_title]:
                        installed_version = json_dict["dlcs"][dlc_title]["version"]
        else:
            if "version" in json_dict:
                installed_version = json_dict["version"]
            else:
                installed_version = self.fallback_read_installed_version()
        if version_from_api != installed_version:
            update_available = True
        # Start: Code for compatibility with minigalaxy 1.0
        if dlc_title and installed_version == "0":
            status = self.legacy_get_dlc_status(dlc_title, version_from_api)
            update_available = True if status in ["updatable"] else False
        # End: Code for compatibility with minigalaxy 1.0
        return update_available

    # This function is for compatibility with minigalaxy 1.0. It can be removed, when decision to break compatibility
    # is taken.
    # This is not a big deal. After removal of this function all DLCs from minigalaxy 1.0 will be marked as uninstalled.
    def legacy_get_dlc_status(self, dlc_title, available_version="0"):
        dlc_status_list = ["not-installed", "installed", "updatable"]
        dlc_status_file_name = "minigalaxy-dlc.json"
        dlc_status_file_path = os.path.join(self.install_dir, dlc_status_file_name)
        json_list = ["", ""]
        status = dlc_status_list[0]
        if os.path.isfile(dlc_status_file_path):
            dlc_staus_file = open(dlc_status_file_path, 'r')
            json_list = json.load(dlc_staus_file)
            dlc_status_dict = json_list[0]
            dlc_staus_file.close()
            if dlc_title in dlc_status_dict:
                status = dlc_status_dict[dlc_title]
        if status == dlc_status_list[1]:
            installed_version_dict = json_list[1]
            if dlc_title in installed_version_dict:
                installed_version = installed_version_dict[dlc_title]
                if available_version != installed_version:
                    status = dlc_status_list[2]
        return status

    def fallback_read_installed_version(self):
        gameinfo = os.path.join(self.install_dir, "gameinfo")
        gameinfo_list = []
        if os.path.isfile(gameinfo):
            with open(gameinfo, 'r') as file:
                gameinfo_list = file.readlines()
        if len(gameinfo_list) > 1:
            version = gameinfo_list[1].strip()
        else:
            version = "0"
        return version

    def set_status(self, key, value, dlc_title=""):
        json_dict = self.load_minigalaxy_info_json()
        if dlc_title:
            if "dlcs" not in json_dict:
                json_dict["dlcs"] = {}
            if dlc_title not in json_dict["dlcs"]:
                json_dict["dlcs"][dlc_title] = {}
            json_dict["dlcs"][dlc_title][key] = value
        else:
            json_dict[key] = value
        self.save_minigalaxy_info_json(json_dict)

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if self.id > 0 and other.id > 0:
            if self.id == other.id:
                return True
            else:
                return False
        if self.name == other.name:
            return True
        # Compare names with special characters and capital letters removed
        if self.get_stripped_name().lower() == other.get_stripped_name().lower():
            return True
        if self.install_dir and other.get_stripped_name() in self.__strip_string(self.install_dir):
            return True
        if other.install_dir and self.get_stripped_name() in self.__strip_string(other.install_dir):
            return True
        return False

    def __lt__(self, other):
        names = [str(self), str(other)]
        names.sort()
        if names[0] == str(self):
            return True
        return False
