from Commands.Command import Command
from consts import *
import subprocess
import Logger

TOPIC = 'terminal_command'

COMMAND_CONTENT_KEY = 'command'
WHITELIST_CONTENT_KEY = 'whitelist'
WHITELIST_DENY = 'deny'
WHITELIST_ALLOW = 'allow'
# Config content: 'whitelist'
# 'whitelist' accepts: deny, allow, list of allowed commands filenames


class TerminalCommand(Command):

    def Initialize(self):
        self.SubscribeToTopic(self.GetTopic(TOPIC))

    def Callback(self, message):
        messageDict = ''
        try:
            messageDict = eval(message.payload.decode('utf-8'))
        except:
            pass  # No message in the payload

        # Look for the command
        # At first check if defined in options
        if self.GetOption([CONTENTS_OPTION_KEY, COMMAND_CONTENT_KEY]):
            command = self.GetOption(
                [CONTENTS_OPTION_KEY, COMMAND_CONTENT_KEY])
            self.ExecuteCommand(command)
        # Else check if I received the command: if yes, it must be in the commands whitelist (SECURITY)
        elif 'command' in messageDict:
            # Check if I have the whitelist
            whitelist = self.GetOption(
                [CONTENTS_OPTION_KEY, WHITELIST_CONTENT_KEY])
            if (whitelist):
                # Check if the command is in the whitelist: I have to check only for the filename, not for the arguments
                # Disallow
                if str(whitelist) == WHITELIST_DENY:
                    self.Log(
                        Logger.LOG_WARNING, 'Command not executed: whitelist deny')
                # Check if allow or if in list
                elif str(whitelist) == WHITELIST_ALLOW or (type(whitelist) == list and messageDict['command'].split()[0] in whitelist):
                    content = messageDict['command']
                    self.ExecuteCommand(content)
                else:
                    self.Log(Logger.LOG_WARNING, "Command not in whitelist: " +
                             messageDict['command'].split()[0])
            else:
                self.Log(
                    Logger.LOG_WARNING, 'You must specify a whitelist to send the command through message')
        else:
            self.Log(Logger.LOG_WARNING,
                     'No valid terminal command received/set')

    def ExecuteCommand(self, command):
        try:
            subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        except:
            self.Log(Logger.LOG_WARNING,
                     "Error during command execution: " + command)
