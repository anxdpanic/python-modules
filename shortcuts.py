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

    Usage:
        - Make a copy of this file with whatever name you'd like
        - Edit the COMMANDS variable below


    Example:
    COMMANDS = {
        '<Command Name>': {                             # - name of the command
            'arguments': ['--arg1', '-a'],              # - list of arguments to execute command
            'help': 'Help text is helpful',             # - help text
            'commands': [                               # - list of commands(dict) to be executed
                {
                    'command': 'sudo mkdir /tmp/test/', # - the command to be executed
                    'shell': True,                      # - use shell’s own pipeline support
                    'require_success': False            # - require the command to successfully
                },                                      #   execute
                {
                    'command': 'sudo touch /tmp/test/test',
                    'shell': True,
                    'require_success': True
                },
                ...
            ]
        },
        ...
    }

"""

import argparse
import subprocess
import traceback

COMMANDS = {
    'start_kodi': {
        'arguments': ['--start', '-s'],
        'help': 'Start Kodi',
        'commands': [
            {
                'command': 'sudo tvservice -p',
                'shell': True,
                'require_success': False
            },
            {
                'command': 'sudo systemctl start mediacenter',
                'shell': True,
                'require_success': False
            },
        ]
    },
    'stop_kodi': {
        'arguments': ['--stop', '-x'],
        'help': 'Stop Kodi',
        'commands': [
            {
                'command': 'sudo systemctl stop mediacenter',
                'shell': True,
                'require_success': False
            },
        ]
    },
    'restart_kodi': {
        'arguments': ['--restart', '-r'],
        'help': 'Restart Kodi',
        'commands': [
            {
                'command': 'sudo tvservice -p',
                'shell': True,
                'require_success': False
            },
            {
                'command': 'sudo systemctl restart mediacenter',
                'shell': True,
                'require_success': False
            },
        ]
    },
    'tail_kodi': {
        'arguments': ['--tail', '-l'],
        'help': 'Tail the Kodi log',
        'commands': [
            {
                'command': 'sudo tail -f /home/osmc/.kodi/temp/kodi.log',
                'shell': True,
                'require_success': False
            },
        ]
    },
    'hdmi': {
        'arguments': ['--hdmi', '-t'],
        'help': 'Power on HDMI with preferred settings',
        'commands': [
            {
                'command': 'sudo tvservice -p',
                'shell': True,
                'require_success': False
            },
        ]
    },
    'reboot_device': {
        'arguments': ['--reboot', '-v'],
        'help': 'Reboot the device',
        'commands': [
            {
                'command': 'sudo reboot now',
                'shell': True,
                'require_success': False
            },
        ]
    },
}


class Executor:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    @staticmethod
    def validate_command(command_name, command_descriptor):
        command_arguments = command_descriptor.get('arguments')
        if not command_arguments or not isinstance(command_arguments, list):
            print('Command %s has invalid arguments' % command_name)
            return False

        command_help_text = command_descriptor.get('help')
        if not command_help_text or not isinstance(command_help_text, str):
            print('Command %s has invalid help text' % command_name)
            return False

        command_commands = command_descriptor.get('commands')
        if not all(isinstance(element, dict) and
                   isinstance(element.get('command'), str) and
                   isinstance(element.get('shell'), bool) and
                   isinstance(element.get('require_success'), bool)
                   for element in command_commands):
            print('Command %s has an invalid command' % command_name)
            return False

        return True

    def execute(self, action):
        command = COMMANDS.get(action, {})

        if not self.validate_command(action, command):
            exit(1)

        self._execute(command.get('commands'))

    @staticmethod
    def _execute(commands):
        for cmd in commands:
            command = cmd.get('command')
            shell = bool(cmd.get('shell'))
            require_success = bool(cmd.get('require_success'))

            try:
                _ = subprocess.check_call(command, shell=shell)
            except:
                traceback.print_exc()
                if require_success:
                    exit(1)


if __name__ == '__main__':
    executor = Executor()
    parser = argparse.ArgumentParser(description='Shortcuts')

    parser_group = parser.add_mutually_exclusive_group(required=True)

    for name, descriptor in COMMANDS.items():
        if not executor.validate_command(name, descriptor):
            continue

        parser_group.add_argument(*descriptor.get('arguments', []), action='store_const',
                                  default=None, const=name, help=descriptor.get('help', ''))

    arguments = parser.parse_args()

    argument_const = next(
        iter(const for argument, const in vars(arguments).items() if const is not None),
        None
    )

    if not argument_const:
        exit(1)

    executor.execute(argument_const)
    exit(0)
