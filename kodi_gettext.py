#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
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

try:
    import xbmcaddon
except ImportError:
    xbmcaddon = None


class Translator:

    def __init__(self, filename=None, addon_id=None, addon=None):
        """
        Class to translate Kodi gettext files, either through Kodi or this module.
        One or more of filename, addon_id, or addon is required.

        :param filename: filename and path to po file to parse
        :type filename: str
        :param addon_id: Kodi addon id
        :type addon_id: str
        :param addon: Kodi Addon() instance
        :type addon: xbmcaddon.Addon
        """

        if not filename and not addon_id and not addon:
            raise ValueError('At least one of `filename`, `addon_id`, or `addon` is required.')

        self._filename = filename

        self._addon_id = addon_id
        self._addon = addon

        self._kodi = xbmcaddon is not None and (self._addon_id or self._addon)

        self._dictionary = {}

    def i18n(self, string_id):
        """
        Get msgstr or msgid for msgctxt "#<string_id>" from self._dictionary
        :param string_id: msgctxt "#<string_id>"
        :type string_id: int
        :return: translated string
        :rtype: str, None
        """
        if self._kodi:
            return self.addon.getLocalizedString(string_id)

        if not self._dictionary:
            self.__load()

        if string_id not in self._dictionary:
            return ''

        entry = self._dictionary[string_id]
        if not entry.valid():
            return ''

        return entry.msgstr if entry.msgstr else entry.msgid

    @property
    def addon(self):
        if not self._kodi:
            return None

        if not self._addon:
            self._addon = xbmcaddon.Addon(self._addon_id)

        return self._addon

    def __load(self):
        """
        Populate self._dictionary with POEntry()'s
        """
        with open(self._filename, encoding='utf-8') as open_file:
            lines = open_file.readlines()

        entry = POEntry()
        for index, line in enumerate(lines):
            if entry.msgctxt is None and not line.startswith('msgctxt'):
                continue

            if line.startswith('msgctxt'):
                entry.msgctxt = int(line.lstrip().replace('msgctxt "#', '').rstrip().rstrip('"'))

                next_line = lines[index + 1]
                if next_line.startswith('msgid'):
                    entry.msgid = next_line.lstrip().replace('msgid "', '').rstrip().rstrip('"')

                    next_line = lines[index + 2]
                    if next_line.startswith('msgstr'):
                        entry.msgstr = \
                            next_line.lstrip().replace('msgstr "', '').rstrip().rstrip('"')

                        if entry.valid():
                            self._dictionary.update({
                                entry.msgctxt: entry
                            })

                entry = POEntry()
                continue


class POEntry:

    def __init__(self):
        """
            Class to contain values of a Kodi gettext file entry
        """
        self._msgctxt = None
        self._msgid = None
        self._msgstr = None

    @property
    def msgctxt(self):
        try:
            return int(self._msgctxt)
        except TypeError:
            return None

    @msgctxt.setter
    def msgctxt(self, value):
        try:
            self._msgctxt = int(value)
        except TypeError:
            self._msgctxt = None

    @property
    def msgid(self):
        return self._msgid

    @msgid.setter
    def msgid(self, value):
        self._msgid = value

    @property
    def msgstr(self):
        return self._msgstr

    @msgstr.setter
    def msgstr(self, value):
        self._msgstr = value

    def valid(self):
        return isinstance(self.msgctxt, int) and \
               isinstance(self.msgid, str) and \
               isinstance(self.msgstr, str)

    def __str__(self):
        if self.valid():
            return 'msgctxt "#%d"\nmsgid "%s"\nmsgstr "%s"\n\n' % \
                   (self.msgctxt, self.msgid, self.msgstr)

        return ''
