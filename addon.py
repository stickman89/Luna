import os
import subprocess

import sys
import urllib.parse
import re

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from resources.lib.util.confighelper import ConfigHelper
from resources.lib.core.logger import Logger 

from xbmcvfs import translatePath

addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path')

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urllib.parse.parse_qs(sys.argv[2][1:])

logger = Logger()
config_helper = ConfigHelper(addon, logger)

def getAddonPath(path):
    return translatePath(addon_path + path)

def settings():
    addon.openSettings()
    config_helper.configure()

def main():
    li = xbmcgui.ListItem("Quick play")
    li.setArt({ 'icon': getAddonPath('/resources/icons/controller.png') })
    xbmcplugin.addDirectoryItem(addon_handle, base_url + '?action=quick_play&refresh=True', li)

    lastrun = addon.getSetting('last_run')
    if lastrun:
        li = xbmcgui.ListItem("Resume " + lastrun)
        li.setArt({ 'icon': getAddonPath('/resources/icons/resume.png') })
        xbmcplugin.addDirectoryItem(addon_handle, base_url + '?action=resume', li)

        li = xbmcgui.ListItem("Quit " + lastrun)
        li.setArt({ 'icon': getAddonPath('/resources/icons/quit.png') })
        xbmcplugin.addDirectoryItem(addon_handle, base_url + '?action=quit', li)

    li = xbmcgui.ListItem("ZeroTier connect")
    li.setArt({ 'icon': getAddonPath('/resources/icons/zerotier.png') })
    xbmcplugin.addDirectoryItem(addon_handle, base_url + '?action=zerotier', li)

    li = xbmcgui.ListItem("Settings")
    li.setArt({ 'icon': getAddonPath('/resources/icons/cog.png') })
    xbmcplugin.addDirectoryItem(addon_handle, base_url + '?action=settings', li)

    xbmcplugin.endOfDirectory(addon_handle)

    del li

def pair():
    from resources.lib.util.moonlighthelper import MoonlightHelper

    helper = MoonlightHelper(addon, config_helper, logger)
    helper.pair()

    del helper

def quickPlay():
    from resources.lib.util.moonlighthelper import MoonlightHelper

    helper = MoonlightHelper(addon, config_helper, logger)
    games = helper.list_games()
    if games == True:
        pair()
        return
    elif games == False:
        xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30018))
        return
    gameId = xbmcgui.Dialog().select("Select a game", games)    
    if gameId != -1:
        helper.launch_game(games[gameId])

    xbmc.executebuiltin('Container.Refresh')
    del helper

def resume():
    from resources.lib.util.moonlighthelper import MoonlightHelper
    lastrun = addon.getSetting('last_run')
    confirmed = xbmcgui.Dialog().yesno('', 'Continue playing ' + lastrun + '?', nolabel='No', yeslabel='Yes', autoclose=5000)
    if confirmed:
        helper = MoonlightHelper(addon, config_helper, logger)
        last_run = addon.getSetting('last_run')
        if last_run:
            helper.launch_game(last_run)

        del helper

def process_exists(process_name):
    try:
        progs = subprocess.check_output("ps -ef | grep " + process_name + " | grep -v grep | wc -l", shell=True)
        if '1' in str(progs):
            return True
        else:
            return False
    except:
        return False

def zerotier():
    if process_exists('zerotier-one'):
        confirmed = xbmcgui.Dialog().yesno('', 'Disable ZeroTier Connection?', nolabel='No', yeslabel='Yes', autoclose=5000)
        if confirmed:
            subprocess.Popen(["/usr/bin/killall", "zerotier-one"], shell=False, start_new_session=True)
    else:
        confirmed = xbmcgui.Dialog().yesno('', 'Enable ZeroTier Connection?', nolabel='No', yeslabel='Yes', autoclose=5000)
        if confirmed:
            if os.path.isfile("/opt/bin/zerotier-one"):
                subprocess.Popen(["/opt/bin/zerotier-one", "-d"], shell=False, start_new_session=True)
            else:
                xbmcgui.Dialog().ok('', 'Missing ZeroTier binaries... Installation is required via Entware!')

def quitgame():
    from resources.lib.util.moonlighthelper import MoonlightHelper
    lastrun = addon.getSetting('last_run')
    confirmed = xbmcgui.Dialog().yesno('', 'Confirm to quit ' + lastrun + '?', nolabel='No', yeslabel='Yes', autoclose=5000)
    if confirmed:
        helper = MoonlightHelper(addon, config_helper, logger)
        helper.quit_game()
        addon.setSettingString('last_run', '')
        xbmcgui.Dialog().ok(addon.getLocalizedString(30000), addon.getLocalizedString(30017))
        xbmc.executebuiltin('Container.Refresh')

def selectAudioDevice():
    device_list = []
    for line in subprocess.check_output('aplay -l | grep card', encoding='utf-8', shell=True).split('\n'):
        if line.strip():
            device_list.append(line)

    audio_device = xbmcgui.Dialog().select('Choose Audio Device', device_list)

    if audio_device != -1:
        device_name = device_list[audio_device]

        CARDS_REGEX = r'(?:card ?)([^:]*).*(?:device ?)([^:]*)'

        match = re.match(CARDS_REGEX, device_name)

        index1 = match.group(1)
        index2 = match.group(2)

        audio_parameter = 'hw:' + index1 + ',' + index2
        addon.setSettingString('audio_device_parameter', audio_parameter)

def selectLaunchscripts():
    launchscripts = os.listdir(getAddonPath('/resources/launchscripts/'))
    ret = xbmcgui.Dialog().select("Select launch scripts for your configuration", launchscripts)
    if ret != -1:
        addon.setSettingString('launchscript_conf', launchscripts[ret])
        os.system('chmod +x ' + getAddonPath('/resources/launchscripts/'+launchscripts[ret])+'/*.sh')

if config_helper.binary_path is None:
    xbmcgui.Dialog().ok("Missing binaries", "Couldn\'t detect moonlight binary.\nPlease check your setup.")
    exit()

if addon.getSetting('launchscript_conf') == "":
    selectLaunchscripts()

if 'action' in args:
    action = args['action'][0]
    if action == 'quick_play':
        quickPlay()
    elif action == 'zerotier':
        zerotier()
    elif action == 'resume':
        resume()
    elif action == 'quit':
        quitgame()
    elif action == 'pair_host':
        pair()
    elif action == 'select_audio_device':
        selectAudioDevice()
    elif action == 'select_launchscripts':
        selectLaunchscripts()
    elif action == 'settings':
        settings()

if addon_handle != -1:
    main()

del addon
del logger
del config_helper