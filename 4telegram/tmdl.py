"""
*************************************************************************************************************************
*  TMDL - Telegram DL                                                                                                   *
*                                                                                                                       *
*  VERSION 0.0.4                                                                                                        *
*                                                                                                                       *
*  Idea/Written by Sebastian Vivian Gresser                                                                             *
*                                                                                                                       *
*  install modules: pip3 install telethon asyncio tqdm argparse                                                         *
*                                                                                                                       *
*  Usage example:   python3 tmdl.py --id 1234 --hash "1289u3jo1imn" --target "name" --output "directory"                *
*                   python3 tmdl.py --id 1234 --hash "1289u3jo1imn" --target id --output "directory"                    *
*                                                                                                                       *
*                   you will get prompted to type in your phone/bot token                                               *
*                   phone token: your phonenumber (e.g. +0155516213576) -> next type in the validation code you         *
*                   just received (you will have to do this once until you delete the registered session)               *
*                   bot token: can be generated by talking to the Botfather                                             *
*                                                                                                                       *
*  API ID/HASH URL: https://my.telegram.org/apps (open the link in a browser -> login and create your app to            *
*                   get a app ID/HASH)                                                                                  *
*                                                                                                                       *
*************************************************************************************************************************
Install / Dependencies Instructions:

Linux:
    Debian/Ubuntu:  apt-get install python3 python3-pip
    Gentoo:         emerge python dev-python/pip
    Fedora:         yum install python3 python3-pip
    Arch:           pacman -S python python-pip
    Suse:           zypper install python3 python3-pip

    --> sudo pip3(or pip) install telethon asyncio tqdm argparse
    (locally with: pip3(or pip) install telethon asyncio tqdm argparse --user)

    python tmdl.py --id 1234 --hash "1289u3jo1imn" --target "name" --output "/path/to/download/dir"
    --> or
    python tmdl.py --id 1234 --hash "1289u3jo1imn" --target id --output "~/Downloads"
    --> see
    python tmdl.py for all options

MAC:
    Download a python3 release: https://www.python.org/downloads/macos/
    --> Double-click python.mpkg
    --> Click "Continue" three times
    --> Select the Volume/HD installation target
    --> Click "Install"
    --> Click "Close"
    --> Open a terminal and type: python3 -m ensurepip --> Enter
    --> type: pip3(or pip) install telethon asyncio tqdm argparse

    python tmdl.py --id 1234 --hash "1289u3jo1imn" --target "name" --output "/path/to/download/dir"
    --> or
    python tmdl.py --id 1234 --hash "1289u3jo1imn" --target id --output "~/Downloads"
    --> see
    python tmdl.py for all options

Windows:
    Download a python3 release: https://www.python.org/downloads/windows/ (installer)
    --> Execute the installer file
    --> select the "Install launcher for all users" and "Add Python 3.x to PATH" checkboxes
    --> Click "Install Now"
    --> Check "Disable path length limit" (if you want to allow path-/filenames longer than 260 characters)
    --> Open the Start menu and type "cmd"
    --> Select the "Command Prompt" application
    --> type: py -m ensurepip --upgrade
    Environment Settings:
    --> Open the "Start menu" and start "Run app"
    --> Type sysdm.cpl and click "OK". (opens the System Properties window)
    --> Navigate to the "Advanced" tab and select "Environment Variables"
    --> Look for "System Variables" and select the "Path variable" -> Edit
    --> Select "Variable value" and add ;C:\Python3x at the end
    (x stands for the subversion you installed; e.g. ;C:\Python310 or ;C:\Python39)
    --> Click "OK" -> Now you can execute scripts like tmdl.py by using the Command Prompt -> python tmdl.py

    python tmdl.py --id 1234 --hash "1289u3jo1imn" --target "name" --output "C:\your\download\directory"
    --> or
    python tmdl.py --id 1234 --hash "1289u3jo1imn" --target id --output "C:\your\download\directory"
    --> see
    python tmdl.py for all options

"""

import argparse
from telethon import errors
from telethon.sync import TelegramClient
from telethon import types
import os
import asyncio
from tqdm import tqdm
import datetime
import re


""" Static Parameter Config Examples"""
param = {}

# APP_ID:                                   Integer
#param['id'] = 1234215
param['id'] = False
# APP_HASH:                                 String
# param['hash'] = "EXAMPLEHASH1i2j12i490"
param['hash'] = False
# Channel/chat ID/NAME:                     Integer/String
#param['target'] = 123441298
#param['target'] = "channelname"
param['target'] = False
# Output directory:                         String
param['output'] = "~/Downloads"
#param['output'] = "C:\Downloads"

# Filters:          Dictionary
#   mnum :          Integer - Maximum messages to process
#   fnum :          Integer - Maximum files to process
#   date_start :    String  - "Y-M-D H:M" e.g. "2021-04-01 00:00"
#   date_end :      String  - "Y-M-D H:M" e.g. "2021-04-01 00:00"
#   date_last :     Integer - Number of seconds to substract from now on e.g. last 3 days 60*60*24*3=259200
#   search_term:    String  - Search for specific String | including regular expressions
#                               e.g. "^.*[word1|word2|word3].*?\.fileextension$"
#   search_target:  Integer - "any" - any; "message" - Messages; "filename" - Filenames
#   mime :          String  - Common MIME type
#                               (https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types)
#                           - e.g. "application/zip,application/vnd.rar,application/x-tar"
#                                equals to search_term with "^.*?\.[zip|rar|tar]$"
#   reverse :       Boolean - True/False - True = older to newer messages
#   loop :          Integer - Keep running and repeat the iteration | -1 = infinite times
#                             in conjunction with date_last 60 for example you can check just the new messages commited
#                             within the last 60 seconds continously
param['filter'] = {
                    'reverse':False,
                    'mnum':False,
                    'fnum':False,
                    'date_start':False,
                    'date_end':False,
                    'date_last':False,
                    'search_term':False,
                    'search_target':False,
                    'mime': False,
                    'loop': False
                   }

args = argparse.ArgumentParser("tmdl")
# common
args.add_argument('--id', nargs=1, required=False, help='API ID', type=int, default=param['id'])
args.add_argument('--hash', nargs=1, required=False, help='API HASH', type=str, default=param['hash'])
args.add_argument('--target', nargs=1, required=False, help='Chat ID(int)/Username(str)', default=param['target'])
args.add_argument('--output', nargs=1, required=False, help='Output path', type=str, default=param['output'])
# filters
args.add_argument('--mnum', nargs=1, required=False, help='Messages max number', type=int, default=param['filter']['mnum'])
args.add_argument('--fnum', nargs=1, required=False, help='Files max number', type=int, default=param['filter']['fnum'])
args.add_argument('--date_start', nargs=1, required=False, help='Start Date e.g. "2021-04-01 00:00"', type=str, default=param['filter']['date_start'])
args.add_argument('--date_end', nargs=1, required=False, help='End Date e.g. "2021-04-01 03:00"', type=str, default=param['filter']['date_end'])
args.add_argument('--date_last', nargs=1, required=False, help='Number of seconds to substract from now on e.g. 259200', type=int, default=param['filter']['date_last'])
args.add_argument('--search_term', nargs=1, required=False, help='Search for specific String e.g. "Name" or Regular Expression e.g. "^.*[word1|word2|word3].*?\.fileextension$"', type=str, default=param['filter']['search_term'])
args.add_argument('--search_target', nargs=1, required=False, help='"any" - any; "message" - Messages; "filename" - Filenames', type=str, default=param['filter']['search_target'])
args.add_argument('--mime', nargs=1, required=False, help='Common MIME Type Filter: e.g. "application/zip,application/vnd.rar,application/x-tar" but you could also use search_term with the following regular expression "^.*?\.[zip|rar|tar]$"', type=str, default=param['filter']['mime'])
args.add_argument('--reverse', nargs=1, required=False, help='Reverse message list', type=bool, default=param['filter']['reverse'])
args.add_argument('--loop', nargs=1, required=False, help='Keep running and repeat the iteration n times (-1 = infinite)', type=int, default=param['filter']['loop'])

argv = args.parse_args()

#sanitize/normalize filters
argv.filter = {}
for k in param['filter']:
    if argv.__getattribute__(k):
        param['filter'][k] = argv.__getattribute__(k).pop()
    v = param['filter'][k]
    if v:
        if k == "mime":
            v = v.split(",")
        elif k == "date_start" or k == "date_end":
            v = datetime.datetime.strptime(v, "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        elif k == "date_last":
            dt=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(seconds=v)
            argv.filter['date_start'] = datetime.datetime.strptime(dt.strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S").replace(tzinfo=datetime.timezone.utc)
        elif k == "search_term":
            v = re.compile(v)
        elif k == "search_target":
            if v not in ["any", "filename", "message"]:
                v = "any"

    argv.filter[k] = v

class tm_dl:
    def __init__(self, id, hash, target, filter, output):
        self.data = {}
        self.id = id
        self.hash = hash
        self.target = target
        self.filter = filter
        if os.name == "posix":
            lst = "/"
        else:
            lst = "\\"
        if output[-1:] != lst:
            output += lst
        self.output = output
        self.mt_dls_max = 10
        self.num_mt_dls = 0
        self.mnum = 0
        self.fnum = 0
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.run())

    async def run(self):
        self.client = TelegramClient('TMDL', self.id, self.hash)
        await self.client.start()
        self.dialogs = await self.client.get_dialogs()
        self.e=await self.client.get_entity(self.target)
        print('[INFO] - Started downloading messages/files to {}'.format(self.output))
        try:
            async with self.client as tt:
                tm=await tt.get_messages(self.e)
                self.total_messages = tm.total
                #self.overall_pbar = tqdm(total=self.total_messages, desc="Overall Progress", position=1)
                last_date = False
                loop = 1
                while loop:
                    async for message in tt.iter_messages(self.e, wait_time=0, reverse=self.filter['reverse']):
                        print("[INFO] Message %s / %s" %(self.mnum, self.total_messages))

                        if self.filter['date_start'] and message.date < self.filter['date_start']:
                            # check for direction to break iteration
                            if not self.filter['reverse']:
                                break
                            continue
                        elif self.filter['date_end'] and message.date > self.filter['date_end']:
                            # check for direction to break iteration
                            if self.filter['reverse']:
                                break
                            continue

                        if self.filter['search_term'] and self.filter['search_target'] in ["any", "message"] and self.filter['search_term'].findall(message.message) == []:
                            continue

                        #self.overall_pbar.update(1)
                        if message.media is not None:
                            if isinstance(message.media, types.MessageMediaDocument):
                                fn=message.media.document.attributes[0].file_name
                                if self.filter['search_term'] and self.filter['search_target'] in ["any", "filename"] and self.filter['search_term'].findall(fn) == []:
                                    continue
                                fp=self.output+fn
                                if self.filter['mime']:
                                    skip=True
                                    if isinstance(filter['mime'], list):
                                        for ft in self.filter['mime']:
                                            if ft == message.media.document.mime_type:
                                                skip=False
                                                break
                                    if skip:
                                        continue
                                if os.path.exists(fp):
                                    if os.path.getsize(fp) ==  message.media.document.size:
                                        print("[FILE] - %s already downloaded" % fn)
                                        continue
                                    elif os.path.getsize(fp)<message.media.document.size:
                                        print("[FILE] - %s resuming download" % fn)
                                        offset = os.path.getsize(fp)
                                    else:
                                        offset = 0
                                print('[INFO] - Starting download of {}'.format(fn))
                                self.pbar=tqdm(unit='B',unit_scale=True,total=message.media.document.size, unit_divisor=1024,desc="[FILE] - "+fn,position=0)
                                self.cp=0
                                if offset:
                                    with open(fp, 'ab') as fd:
                                        async for chunk in self.client.iter_download(message.media,offset=offset):
                                            offset += len(chunk)
                                            fd.write(chunk)
                                            self.dl_callback(offset, message.media.document.size)
                                else:
                                    await self.client.download_media(message=message, file=fp, progress_callback=self.dl_callback)
                                self.pbar.close()
                                self.fnum += 1
                                if self.filter['fnum'] and self.filter['fnum'] >= self.fnum:
                                    break
                        self.mnum += 1
                        if self.filter['mnum'] and self.filter['mnum'] >= self.mnum:
                            break
                    #self.overall_pbar.close()
                    if not self.filter['loop'] or (self.filter['loop'] != -1 and loop >= self.filter['loop']):
                        loop = False
                    else:
                        loop += 1
        except Exception as e:
            print(e)

        print('[INFO] - Finished downloading messages/files')

    def dl_callback(self, current, total):
        progress = current - self.cp
        self.cp = current
        self.pbar.update(progress)
        #self.overall_pbar.update(0)

if __name__ == "__main__":
    tm=tm_dl(id=argv.id,hash=argv.hash,target=argv.target,filter=argv.filter,output=argv.output)
