#!/usr/bin/env python
import re
import os
import time
import json
import random
import requests

class Chat:
    def __init__(self):
        ''' SETTINGS '''
        self.NOT_STAFF   = ['guest'] # You can use: member, mod, owner, main
        self.BLACK_LIST  = [10101, 1510151, 22332233, 23232323, 356566558] # Black list, you can ignore bots or someone else
        self.CACHE_TIME  = 86400 # 24 hours in seconds
        self.PHRASES     = [
            'Invalid password.',
            'You need MANAGE power enabled.',
            'Page not found, you can use 0-5.',
            'Language not found',
        ]
        self.XAT_IDS = {
            7:   'Darren',
            42:  'xat',
            100: 'Sam',
            101: 'Chris',
            200: 'Ajuda',
            201: 'Ayuda',
            804: 'Bot',
            911: 'Guy',
        }
        self.URL = {
            'xs': 'https://xat.me/web_gear/chat/profile.php?id=%d',
            'edit': 'https://xat.com/web_gear/chat.php?id=%d&pw=%d',
            'chat': 'https://xat.com/web_gear/chat/editgroup.php?GroupName=%s' % settings.CHAT_NAME,
            'eip': 'https://xat.com/web_gear/chat/eip.php?id=%d&pw=%d&md=4&back=%s&t=%s',
        }
        ''' #=#=#=#=# '''
        self.AUTH      = False
        self.LANGUAGES = []
        self.NAME      = settings.CHAT_NAME
        self.PASS      = settings.CHAT_PASS
        self.HEADERS   = {
            'Referer': self.URL['chat'],
            'User-Agent': 'Mozilla/5.0 (X11; Linux i586; rv:31.0) Gecko/20100101 Firefox/31.0',
        }
        self.HTML      = self.getInitData()
        self.INPUTS    = {}

    def getStaffList(self):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        self.INPUTS['BackupUsers'] = 1
        getParams = self.submit()
        staffList = {}
        if '**<span data-localize=edit.manage>' in getParams:
            return self.PHRASES[1]
        for line in getParams.splitlines():
            user = line.split(',')
            if user[5] not in self.NOT_STAFF and not int(user[0]) in self.BLACK_LIST:
                xatUser = self.getUsername(user[0])
                isTemp = True if user[5][:4] == 'temp' else False
                if xatUser:
                    staffList[user[0]] = {
                        'user': xatUser,
                        'rank': user[5].replace('temp', ''),
                        'temp': isTemp,
                    }
        return staffList

    def setOuter(self, bg):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        self.INPUTS['back'] = bg
        self.saveChanges()
        return True

    def setInner(self, bg):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        reqData = requests.get(self.URL['edit'] % (int(self.INPUTS['id']), int(self.INPUTS['pw']))).text
        getData = re.search(r'<input name="background" type="hidden" value="(.*?);=(.*?)">', reqData, re.DOTALL)
        newData = '%s;=%s' % (bg, getData[2])
        requests.post(self.URL['eip'] % (int(self.INPUTS['id']), int(self.INPUTS['pw']), newData, random.random()))
        return True

    def setTransparent(self, mode):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        if mode:
            self.INPUTS['Transparent'] = 'ON'
        else:
            del self.INPUTS['Transparent']
        self.saveChanges()
        return True

    def setComments(self, mode):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        if mode:
            self.INPUTS['Comments'] = 'ON'
        else:
            del self.INPUTS['Comments']
        self.saveChanges()
        return True

    def setDescription(self, desc):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        self.INPUTS['GroupDescription'] = desc
        self.saveChanges()
        return True

    def setTags(self, tags):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        self.INPUTS['Tags'] = tags
        self.saveChanges()
        return True

    def setAdsLink(self, url):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        self.INPUTS['www'] = url
        self.saveChanges()
        return True

    def setButtonText(self, number, text):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        elif int(number) < 0 or int(number) > 5:
            return self.PHRASES[2]
        number = "media%s" % number
        if number in self.INPUTS:
            self.INPUTS[number] = text
        self.saveChanges()
        return True

    def setLanguage(lang):
        if lang not in self.LANGUAGES:
            return self.PHRASES[3]
        self.INPUTS['Lang'] = lang
        self.saveChanges()
        return True

    def setButtonName(self, number, title):
        self.loadInputs()
        if not self.INPUTS:
            return self.PHRASES[0]
        elif int(number) < 0 or int(number) > 5:
            return self.PHRASES[2]
        number = "button%s" % number
        if number in self.INPUTS:
            self.INPUTS[number] = title
        self.saveChanges()
        return True

    def saveChanges(self):
        self.INPUTS['submit1'] = 1
        return self.submit()

    def submit(self):
        getSetup = requests.post(self.URL['chat'], data=self.INPUTS, headers=self.HEADERS).text
        return getSetup
        
    def getInitData(self):
        params = {'GroupName': self.NAME, 'password': self.PASS, 'SubmitPass': 'Submit'}
        getParams = requests.post(self.URL['chat'], data=params).text
        if '**<span data-localize=buy.wrongpassword>' in getParams:
            return False
        self.AUTH = True
        return getParams

    def getUsername(self, uid):
        if uid in self.XAT_IDS:
            return self.XAT_IDS[uid]
        uid = str(uid)
        fileDir = settings.INTERNAL_DIR + '/usercache.json'
        rUsers = open(fileDir, "r")
        users = json.loads(rUsers.read())
        rUsers.close()
        if uid in users:
            if int(users[uid]['time']) >= time.time() :
                return users[uid]['name']
        getProfile = requests.get(self.URL['xs'] % int(uid)).text
        if getProfile and len(getProfile) < 20:
            users[uid] = {
                'name': getProfile,
                'time': int(time.time() + self.CACHE_TIME)
            }
        wUsers = open(fileDir, "w")
        wUsers.write(json.dumps(users))
        wUsers.close()
        if uid in users:
            return users[uid]['name']  
        return False

    def loadInputs(self):
        if not self.AUTH:
            return False
        getInputs = re.findall(r'<input(.*?)>', self.HTML, flags=re.DOTALL)
        getTextarea = re.search(r'<textarea id="media0"(.*?)>(.*?)</textarea>', self.HTML, re.DOTALL)
        getLang = re.search(r'<select name="Lang">(.*?)</select>', self.HTML, re.DOTALL)
        getLangList = re.findall(r'<option value="([\w]+)"(.*?)>(.*?)</option>', getLang[0], flags=re.DOTALL)
        for code, extra, name in getLangList:
            self.LANGUAGES.append(code)
            if ' selected' in extra:
                self.INPUTS['Lang'] = code
        self.INPUTS['media0'] = getTextarea[2]
        for i in getInputs:
            getInput = re.findall(r'name\="(.*?)"', i)
            getInputLazy = re.findall(r'name\=(.*?) ', i)
            if getInput:
                getValue = re.findall(r'value\="(.*?)"', i)
                isChecked = re.findall(r' checked', i)
                if getValue:
                    if getValue[0] == 'ON' and isChecked or getValue[0] != 'ON':
                        self.INPUTS[getInput[0]] = getValue[0]
            elif getInputLazy:
                getValue = re.findall(r'value\="(.*?)"', i)
                if getValue:
                    self.INPUTS[getInputLazy[0]] = getValue[0]
        return self.INPUTS


''' YOUR CHAT DETAILS'''
CHAT_NAME = 'YOUR_CHATNAME'
CHAT_PASS = 'YOUR_PASSWORD'
''' #=#=#=#=#=#=#=#=# '''

chat = ChatHandler(CHAT_NAME, CHAT_PASS)

#chat.getStaffList()
#chat.setOuter('https://i.imgur.com/jnCTnx4.png')
#chat.setInner('https://i.imgur.com/vkiJhBu.png')
#chat.setTransparent(False)
#chat.setComments(True)
#chat.setDescription('My personal chat...')
#chat.setTags('mundo,smilies,chat')
#chat.setAdsLink('mundosmilies.com')
#chat.setLanguage('en')
#chat.setButtonText(0, 'This is my first page')
#chat.setButtonName(0, 'Home')
