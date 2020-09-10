# -*- coding: utf-8 -*-

"""

    This script will remove saved add-on settings that aren't available in
    the add-on's default settings.

    NOTE: This may be intended by some add-ons, only remove entries you're sure of.

    This will clean up log entries like the following examples;
        Kodi 18:
            DEBUG: CSettingsManager: requested setting (example_id) was not found.
            DEBUG: CAddonSettings[plugin.video.example]: failed to find definition for setting
                example_id. Creating a setting on-the-fly...

        Kodi 19:
            DEBUG <CSettingsManager>: requested setting (example_id) was not found.

    You will be asked whether you would like to delete each setting, and a
    backup <filename.timestamp> will be created before changes to any files
    are made.

    Example usage:
        # special://home -> https://kodi.wiki/view/Special_protocol#Default_OS_mappings

        # run from special://home
        ..\> python kssc.py

        # pass special://home (translated) as an argument
        ..\> python kssc.py D:\Programs\Kodi_19\portable_data


    This is free and unencumbered software released into the public domain.

    Anyone is free to copy, modify, publish, use, compile, sell, or
    distribute this software, either in source code form or as a compiled
    binary, for any purpose, commercial or non-commercial, and by any
    means.

    In jurisdictions that recognize copyright laws, the author or authors
    of this software dedicate any and all copyright interest in the
    software to the public domain. We make this dedication for the benefit
    of the public at large and to the detriment of our heirs and
    successors. We intend this dedication to be an overt act of
    relinquishment in perpetuity of all present and future rights to this
    software under copyright law.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
    OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
    ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
    OTHER DEALINGS IN THE SOFTWARE.

    For more information, please refer to <http://unlicense.org/>

"""

import os
import shutil
import sys
import time
from lxml import etree


class Paths:
    _required = []
    _working_directory = os.getcwd()

    def __init__(self):
        self.addons = os.path.join(self.working_directory, 'addons')
        self.addon_data = os.path.join(self.working_directory, 'userdata', 'addon_data')

    def settings_path(self, _addon_id):
        return os.path.join(self.addons, _addon_id, 'resources', 'settings.xml')

    @property
    def working_directory(self):
        if len(sys.argv) == 2:
            self._working_directory = sys.argv[1]

        return self._working_directory

    @property
    def required(self):
        if self._required:
            return self._required

        self._required = [(root.split(os.sep)[-1], self.join(root, name),
                           self.settings_path(root.split(os.sep)[-1]))
                          for root, dirs, files in os.walk(self.addon_data)
                          for name in files
                          if name == 'settings.xml' and
                          self.exists(self.settings_path(root.split(os.sep)[-1]))]

        return self._required

    @staticmethod
    def exists(path):
        return os.path.exists(path)

    @staticmethod
    def join(*args):
        return os.path.join(*args)


class SettingsXML:
    tree = None
    root = None
    filename = None
    ids = []

    def __init__(self, filename):
        self.filename = filename
        self.tree = etree.parse(self.filename)
        self.root = self.tree.getroot()

        self.ids = [setting.get('id') for setting in self.root.iter('setting')
                    if setting.get('id') is not None]

    def remove(self, setting_ids):
        settings = self.root.findall('setting')

        for setting in settings:
            if setting.get('id') in setting_ids:
                self.root.remove(setting)

    def write(self):
        backup_filename = '%s.%s' % (self.filename, time.strftime("%Y%m%d-%H%M%S"))
        try:
            shutil.copy(self.filename, backup_filename)
            print('Backup %s... completed.' % backup_filename)

        except:
            rusure_response = \
                yes_no('Failed to backup %s... continue to overwrite?' % self.filename, False)

            if not rusure_response:
                return

        payload = etree.tostring(self.root, method='html', pretty_print=True,
                                 xml_declaration=True, encoding='utf-8', standalone=True)

        with open(self.filename, 'wb') as open_file:
            open_file.write(payload)

        print('Changes made to %s... completed.' % self.filename)

    def __eq__(self, other):
        return not any([setting_id for setting_id in other.ids if setting_id not in self.ids])


def confirm_removals(addon_id, stored_ids, default_ids):
    potential_ids = [setting_id for setting_id in stored_ids if setting_id not in default_ids]

    for_removal = []
    for potential_id in potential_ids:
        remove_response = yes_no('Remove %s->%s?' % (addon_id, potential_id))
        if remove_response:
            for_removal.append(potential_id)

    return for_removal


def yes_no(prompt, default_result=True):
    default_result = bool(default_result)
    default_string = '[Y/n]' if default_result else '[y/N]'

    reply = str(input('%s %s: ' % (prompt, default_string))).lower().strip()
    response = reply[:1]

    if not response:
        return default_result

    if response == 'y':
        return True

    if response == 'n':
        return False

    return None


if __name__ == '__main__':
    if len(sys.argv) > 2:
        print('Too many arguments, only path supported')
        exit(1)

    paths = Paths()

    if not paths.exists(paths.addons):
        print('Path does not exist ' + paths.addons)
        exit(1)

    if not paths.exists(paths.addon_data):
        print('Path does not exist ' + paths.addon_data)
        exit(1)

    updated_addons = []

    for identifier, stored_xml, default_xml in paths.required:

        default = SettingsXML(default_xml)
        stored = SettingsXML(stored_xml)

        if default == stored:
            print(identifier + ' requires no clean up... skipped.')
            continue

        else:
            print(identifier + ' requires clean up...')

            settings_to_remove = confirm_removals(identifier, stored.ids, default.ids)

            if not settings_to_remove:
                print(identifier + ' no changes made...')
                continue

            stored.remove(settings_to_remove)
            updated_addons.append((identifier, stored))

    if not updated_addons:
        print('No add-on settings were changed... completed.')
        exit(0)

    for identifier, stored in updated_addons:
        stored.write()

    print('Changes to saved settings... completed.')
    exit(0)
