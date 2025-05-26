import base64
import xbmc
import xbmcvfs
import xbmcaddon
import xbmcgui
import json
import os
import re
from datetime import datetime
from xml.etree import ElementTree as ET
from uservar import buildfile, BUILDS
from urllib.request import Request, urlopen
from .parser import XmlParser, TextParser

addon_id = xbmcaddon.Addon().getAddonInfo('id')
addon           = xbmcaddon.Addon(addon_id)
addon_info      = addon.getAddonInfo
addon_version   = addon_info('version')
addon_name      = addon_info('name')
addon_icon      = addon_info("icon")
addon_fanart    = addon_info("fanart")
addon_ver       = xbmc.getInfoLabel(f'System.AddonVersion({addon_id})')
translatePath   = xbmcvfs.translatePath
addon_profile   = translatePath(addon_info('profile'))
addon_path      = translatePath(addon_info('path'))    
setting         = addon.getSetting
setting_true    = lambda x: bool(True if setting(str(x)) == "true" else False)
setting_set     = addon.setSetting
local_string    = addon.getLocalizedString
CURRENT_BUILD   = setting('buildname')
CURRENT_VERSION = setting('buildversion')
BUILD_VERSION   = setting('buildversion')
home = translatePath('special://home/')
dialog = xbmcgui.Dialog()
dp = xbmcgui.DialogProgress()
xbmcPath=os.path.abspath(home)
addons_path = os.path.join(home, 'addons/')
user_path = os.path.join(home, 'userdata/')
data_path = os.path.join(user_path, 'addon_data/')
db_path = translatePath('special://database/')
addons_db = os.path.join(db_path, 'Addons33.db')
packages = os.path.join(addons_path, 'packages/')
zippath = os.path.join(packages, 'tempzip.zip')
resources = os.path.join(addon_path, 'resources/')
thumbnails = os.path.join(user_path, 'Thumbnails')
user_agent = 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.101 Safari/537.36'
headers = {'User-Agent': user_agent}
kodi_ver_ = str(xbmc.getInfoLabel("System.BuildVersion")[:2])
kodi_ver = str(xbmc.getInfoLabel("System.BuildVersion")[:4])
kodi_versions = ['K20', 'K21', 'K22']
sleep = xbmc.sleep
notify_file = os.path.join(addon_profile,'notify.txt')
texts_path = os.path.join(resources, 'texts/')
authorize = texts_path + 'authorize.json'
installed_date = str(datetime.now())[:-7]
inst_date = setting('buildinstalled')

#Backup Path for User GUI/Skin Settings
gui_save_path = translatePath(setting('backupfolder'))

#GUI Settings
gui_file = os.path.join(user_path, 'guisettings.xml')
gui_temp_dir = os.path.join(packages, 'gui_temp/')
gui_temp_file = os.path.join(gui_temp_dir, 'guisettings.xml')
gui_save_default = os.path.join(user_path, 'gui_settings/')
gui_save_user = os.path.join(gui_save_path, 'gui_settings_user/')

#Advanced Settings
advancedsettings_blank = os.path.join(resources, 'advancedsettings/advancedsettings.xml')
advancedsettings_xml =  os.path.join(user_path, 'advancedsettings.xml')
advancedsettings_backup =  os.path.join(packages, 'advancedsettings.xml')

#Add-on lists
vid_list = str(len([i for i in os.listdir(addons_path) if i.startswith('plugin.video')]))
prg_list = str(len([i for i in os.listdir(addons_path) if i.startswith('plugin.program')]))
repo_list = str(len([i for i in os.listdir(addons_path) if i.startswith('repo')]))
#add_up = xbmc.getInfoLabel('System.AddonUpdateCount')

#HDD/SSD Stats
total_space = round(int(float(re.sub("[^0-9]", "", xbmc.getInfoLabel('System.TotalSpace')))), 3)
used_space = round(int(float(re.sub("[^0-9]", "", xbmc.getInfoLabel('System.UsedSpace')))), 3)
used_perc = xbmc.getInfoLabel('System.UsedSpacePercent')
free_space = round(int(float(re.sub("[^0-9]", "", xbmc.getInfoLabel('System.FreeSpace')))), 3)
free_perc = xbmc.getInfoLabel('System.FreeSpacePercent')

#Memory Stats   
#total_mem = xbmc.getInfoLabel('System.Memory(total)')
#used_mem = xbmc.getInfoLabel('System.Memory(used)')
#used_mem_perc = xbmc.getInfoLabel('System.Memory(used.percent)')
#free_mem = xbmc.getInfoLabel('System.Memory(free)')
#free_mem_perc = xbmc.getInfoLabel('System.Memory(free.percent)')

#Build Stats
build_ver = xbmc.getInfoLabel('System.BuildVersion')
build_date = xbmc.getInfoLabel('System.BuildDate')

def stats():
    systime = ['System.Uptime', 'System.TotalUptime', 'System.OSVersionInfo']
    data = []
    x = 0
    for item in systime:
        time = xbmc.getInfoLabel(item)
        y = 0
        while time == "Busy" and y < 10:
            time = xbmc.getInfoLabel(item)
            y += 1
            xbmc.sleep(200)
        data.append(time)
        x += 1
    uptime = data[0]
    total_uptime = data[1]
    os = data[2]
    os_info = "".join(re.split("\(|\)", os)[::2])
    return uptime, total_uptime, os_info
uptime, total_uptime, os_info = stats()

'''def clean_mem():
    #Clean Memory Percents
    used_mem_rpl = {" ": "", "U": "", "s": "", "e": "", "d": ""}
    for old, new in used_mem_rpl.items():
        used_p = used_mem_perc.replace(old, new)
        used_perc = used_p
    free_mem_rpl = {" ": "", "F": "", "r": "", "e": "", "e": ""}
    for old, new in free_mem_rpl.items():
        free_p = free_mem_perc.replace(old, new)
        free_perc = free_p
    return used_perc, free_perc
used_perc, free_perc = clean_mem()

def stats():
    systime = ['System.Uptime', 'System.TotalUptime', 'Network.IPAddress', 'Network.LinkState', 'System.OSVersionInfo', 'System.CpuFrequency']
    data = []
    x = 0
    for item in systime:
        time = xbmc.getInfoLabel(item)
        y = 0
        while time == "Busy" and y < 10:
            time = xbmc.getInfoLabel(item)
            y += 1
            xbmc.sleep(200)
        data.append(time)
        x += 1
    uptime = data[0]
    total_uptime = data[1]
    ip_addr = data[2]
    net_link = data[3]
    os = data[4]
    os_info = "".join(re.split("\(|\)", os)[::2])
    cpu_freq = data[5]
    return uptime, total_uptime, ip_addr, net_link, os_info, cpu_freq
uptime, total_uptime, ip_addr, net_link, os_info, cpu_freq = stats()'''

def isBase64(s):
    try:
        if base64.b64encode(base64.b64decode(s)).decode('utf8') == s:
            return True
        else:
            return False
    except:
        return False

def currSkin():
    return xbmc.getSkinDir()

def percentage(part, whole):
    return 100 * float(part)/float(whole)

def get_latest_db(db_type: str) -> str:
    highest_number = -1
    highest_file = None
    for file in os.listdir(db_path):
        if file.startswith(db_type) and file.endswith('.db'):
            try:
                number = int(file[len(db_type):file.index('.db')])
                if number > highest_number:
                    highest_number = number
                    highest_file = file
            except ValueError:
                pass
    if highest_file is not None:
        return os.path.join(db_path, highest_file)

textures_db = get_latest_db('Textures')
addons_db = get_latest_db('Addons')

def file_check(bfile):
    if isBase64(bfile):
        return base64.b64decode(bfile).decode('utf8')
    return bfile

def get_page(url):
       req = Request(file_check(url), headers = headers)
       return urlopen(req).read().decode('utf-8')
    
def splash_chk():
    if xbmcvfs.exists(advancedsettings_xml):
        tree = ET.parse(advancedsettings_xml) #Parse Advancedsettings.xml
        root = tree.getroot()
        for splash in root.iter('splash'): #Check if splash is enabled/disabled
                value = splash.text
                return value
chk_splash = splash_chk()

def chk_skin_override():
    if xbmcvfs.exists(advancedsettings_xml):
        tree = ET.parse(advancedsettings_xml) #Parse Advancedsettings.xml
        root = tree.getroot()
        if len(root.findall('lookandfeel')) == 0: #Check if skin settings exist
            return True
    else:
        return True
            
def get_skin_gui():
    #Get current skin name
    cur_skin = xbmc.executeJSONRPC('{"jsonrpc":"2.0", "method":"Settings.GetSettingValue", "params":{"setting":"lookandfeel.skin"}, "id":1}')
    cur_skin = json.loads(cur_skin)
    skin = ''
    if 'result' in cur_skin and 'value' in cur_skin['result']:
            skin = cur_skin['result']['value']
            return skin
skin_gui = get_skin_gui()
cur_skin = xbmcaddon.Addon(skin_gui).getAddonInfo('name')

def get_dir_size(dir_path):
    
    # Get the uncompressed size of a directory
    size = 0
    size_mb = 0
    for path, dirs, files in os.walk(dir_path):
        for name in dirs:
            if name in ['cache', 'temp']:
                pass
        for f in files:
            fp = os.path.join(path, f)
            try:
                size += os.path.getsize(fp)
            except OSError as e:
                xbmc.log(f'Error reading file while getting directory size - {e}', xbmc.LOGINFO)
    size_mb = f"{int(size) / float(1 << 20):.2f}"
    return size_mb

def build_size():
    if setting('buildname') not in ['NetKlix Lite', 'NetKlix Plus']:
        buildsize = get_dir_size(home)
    else:
        buildsize = 0
    return buildsize

#Kodi Maintenance Stats
packagesize = get_dir_size(packages)
thumbnailsize = get_dir_size(thumbnails)
thumbs = round(float(get_dir_size(thumbnails)), 2)
cleanup = round(float(packagesize) + float(thumbnailsize), 2)
buildsize = build_size()

def count_builds():
       response = ''
       try:
           response = get_page(buildfile)
       except:
           name = None
       name = ''
       current_list = []
       xml = XmlParser(response)
       builds = xml.parse_builds()
       for build in builds:
           if not build.get('version'):
               pass
           else:
               if kodi_ver_ in build.get('kodi'):
                    current_list.append(build.get('name'))
                    name = len(current_list)
       return name
NUM_BUILDS = count_builds()

def get_old_build():
       key = None
       for key in BUILDS:
           if key['Old Build'] == CURRENT_BUILD:
               builds = key
               break
           else:
               builds = {'Old Build': "Old Build_1"}
       for key, value in builds.items():
           if key == 'Old Build':
               old_build = value
               break
       return old_build
OLD_BUILD = get_old_build()

def get_new_build():
       if CURRENT_BUILD == OLD_BUILD:
           key = None
           for key in BUILDS:
               if key['Old Build'] == CURRENT_BUILD:
                   builds = key
                   break
           for key, value in builds.items():
               if key == 'New Build':
                   new_build = value
                   break
           return new_build
NEW_BUILD = get_new_build()

def get_update_details():
    response = ''
    try:
       response = get_page(buildfile)
    except:
       name = None
       version = None
       url = None
    name = ''
    version = ''
    url = ''
    builds = []

    if '"builds"' in response or "'builds'" in response:
       builds = json.loads(response)['builds']
       
    elif '<version>' in response:
       xml = XmlParser(response)
       builds = xml.parse_builds()
       
    elif 'name="' in response:
       text = TextParser(response)
       builds = text.parse_builds()

    for build in builds:
       if build.get('name') == NEW_BUILD:
           name = str(build.get('name'))
           version = str(build.get('version'))
           url = (build.get('url', ''))
           break
       elif build.get('name') == CURRENT_BUILD:
           name = str(build.get('name'))
           version = str(build.get('version'))
           url = (build.get('url', ''))
           break
    return name, version, url
BUILD_NAME, UPDATE_VERSION, BUILD_URL = get_update_details()
