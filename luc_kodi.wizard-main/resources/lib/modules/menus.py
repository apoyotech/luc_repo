import sys
import json
import xbmc
import xbmcgui
import xbmcplugin
import urllib
from .utils import add_dir
from uservar import buildfile, videos_url, changelog_dir
from .parser import XmlParser, TextParser, get_page
from .addonvar import addon_name, setting, addon_icon, addon_fanart, addon_ver, local_string, authorize, kodi_ver, kodi_versions, chk_splash, chk_skin_override, thumbnailsize, packagesize, buildsize, cleanup, headers, home, os_info, cur_skin, total_space, used_space, used_perc, free_space, free_perc, uptime, total_uptime, build_ver, build_date, vid_list, prg_list, repo_list, inst_date, UPDATE_VERSION, CURRENT_BUILD, BUILD_VERSION, BUILD_NAME, NUM_BUILDS
from .colors import colors
from .db import lastchk

HANDLE = int(sys.argv[1])

COLOR1 = colors.color_text1
COLOR2 = colors.color_text2
COLOR3 = colors.color_text3
COLOR4 = colors.color_text4

def main_menu():
    xbmcplugin.setPluginCategory(HANDLE, COLOR1('Main Menu'))
    
    add_dir(COLOR1(f"<><> [B]Welcome to luc_kodi.wizard[/B] <><>"), '', '', addon_icon, addon_fanart, COLOR2(f'luc_kodi.wizard v{addon_ver}\n\nSystem Uptime:  {uptime}\nTotal System Uptime:  {total_uptime}'), isFolder=False)
    
    if UPDATE_VERSION > BUILD_VERSION:
        add_dir(COLOR3(f'[B]Build Update Available!!![/B]   [{BUILD_NAME} v{UPDATE_VERSION}]'), '', 41, addon_icon, addon_fanart, COLOR2(local_string(30110)), isFolder=False)  # Build Update Available
        
    elif CURRENT_BUILD not in ['No Build Installed', 'No Build']:
        add_dir(COLOR4(f'Installed Build:   {CURRENT_BUILD} v{BUILD_VERSION}'), '', '', addon_icon, addon_fanart, COLOR2(f'Install Date:  {inst_date}\nBuild Skin:  {cur_skin}\n\nVideo Add-ons  [{vid_list}]\nProgram Add-ons  [{prg_list}]\nRepositories  [{repo_list}]'), isFolder=False)  # Show the current installed build

    add_dir(COLOR4(f'Kodi Version:  v{kodi_ver}'), '', '', addon_icon, addon_fanart, COLOR2(f'Release Date: {build_date}\n\nFull Version:\n{build_ver}'), isFolder=False)  # Show the installed version of Kodi
    
    if buildfile not in ['', 'http://', 'http://CHANGEME/']:
        add_dir(COLOR2(f'Build Menu  ({NUM_BUILDS} Builds)'), '', 1, addon_icon, addon_fanart, COLOR2(local_string(30001)), isFolder=True)  # Build Menu with total builds
    else:
        add_dir(COLOR2(local_string(30010)), '', 1, addon_icon, addon_fanart, COLOR2(local_string(30001)), isFolder=True)  # Build Menu

    add_dir(COLOR2(local_string(30002)), '', 5, addon_icon, addon_fanart, COLOR2(local_string(30011)), isFolder=True)  # Maintenance Menu

    add_dir(COLOR2(local_string(30119)), '', 36, addon_icon, addon_fanart, COLOR2(local_string(30119)), isFolder=True)  # Build Tools Menu
    
    #add_dir(COLOR2(local_string(30026)),'',10,addon_icon,addon_fanart,COLOR2(local_string(30026)))  # Authorize Debrid Services
    
    add_dir(COLOR2(local_string(30013)), '', 34, addon_icon, addon_fanart, COLOR2(local_string(30014)), isFolder=False)  # View Notification
    
    if videos_url not in ('', 'http://', 'http://CHANGEME'):
        add_dir(COLOR2('Videos'), videos_url, 40, addon_icon, addon_fanart, COLOR2('Videos'), isFolder=True) # Videos

    if changelog_dir not in ['', 'http://', 'http://CHANGEME/'] and CURRENT_BUILD not in ['No Build Installed', 'No Build']:
        add_dir(COLOR2(f'View Changelog'), '', 35, addon_icon, addon_fanart, COLOR2(f'View the changelog for your installed build\n\nCurrent Build:  {CURRENT_BUILD} v{BUILD_VERSION}'), isFolder=False)  # View Build Changelog

    add_dir(COLOR2('View Log'),'', 26, addon_icon,addon_fanart,COLOR2('View the Kodi Log'), isFolder=False) # View Kodis log file
    
    add_dir(COLOR2(local_string(30015)), '', 9, addon_icon, addon_fanart, COLOR2(local_string(30016)), isFolder=False)  # Settings

def build_menu():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    xbmcplugin.setPluginCategory(HANDLE, local_string(30010))
    
    builds = []
    try:
       response = get_page(buildfile)
    except:
       xbmcgui.Dialog().notification(addon_name, 'No Build File Present!!', addon_icon, 3000) # Notify user if no build file is present
       quit()
        
    if '"name":' in response or "'name':" in response:
        builds = json.loads(response)['builds']
    
    elif '<name>' in response:
        xml = XmlParser(response)
        builds = xml.parse_builds()
    
    elif 'name=' in response:
        text = TextParser(response)
        builds = text.parse_builds()
            
    for build in builds:
        name = (build.get('name', local_string(30018)))  # Unknown Name
        version = (build.get('version'))
        kodiversion = (build.get('kodi'))
        url = (build.get('url', ''))
        if url.startswith('https://www.dropbox.com'):
            url = url.replace('dl=0', 'dl=1')
        if setting('autozipsize') == 'true': # Check if enabled
            if str(url) == 'http://':
                pass
            else:
                req = urllib.request.Request(f'{url}', method='HEAD', headers=headers)
                f = urllib.request.urlopen(req)
                size = f.headers['Content-Length']
                buildsize = f"{int(size) / float(1 << 20):.0f}MB" # Get build zip file size in MB via url header
        else:
            buildsize = (build.get('size'))
        icon = (build.get('icon', addon_icon))
        fanart = (build.get('fanart', addon_fanart))
        description = (build.get('description', local_string(30019)))  # No Description Available
        preview = (build.get('preview',None))
            
        if url.endswith('.xml') or url.endswith('.json') or url.endswith('.txt'):
            add_dir(COLOR2(name),url,1,icon,fanart,COLOR2(description),name2=name,version=version,kodi=kodiversion,size=buildsize,isFolder=True)

        elif '20' in kodi_ver and version == '' and kodiversion == 'K20':
            add_dir(COLOR2(f'{name}'), url, '', icon, fanart, description, name2=name, isFolder=False) # K20 Build Menu Separators
        elif '21' in kodi_ver and version == '' and kodiversion == 'K21':
            add_dir(COLOR2(f'{name}'), url, '', icon, fanart, description, name2=name, isFolder=False) # K21 Build Menu Separators
        elif '22' in kodi_ver and version == '' and kodiversion == 'K22':
            add_dir(COLOR2(f'{name}'), url, '', icon, fanart, description, name2=name, isFolder=False) # K22 Build Menu Separators
            
        elif '20' in kodi_ver and kodiversion == 'K20':
            add_dir(COLOR2(f'[B]{name}[/B] -- (v{version} / {buildsize})'), url, 3, icon, fanart, description, name2=name, version=version, kodi=kodiversion, size=buildsize, isFolder=False) # K20 Build Menu
            if preview not in (None, '', 'http://', 'https://'):
                add_dir(COLOR1(local_string(30021) + ' ' + name + ' ' + local_string(30020) + ' ' + version), preview, 2, icon, fanart, COLOR2(description), name2=name, version=version, isFolder=False)  # Video Previews
                
        elif '21' in kodi_ver and kodiversion == 'K21':
            add_dir(COLOR2(f'[B]{name}[/B] -- (v{version} / {buildsize})'), url, 3, icon, fanart, description, name2=name, version=version, kodi=kodiversion, size=buildsize, isFolder=False) # K21 Build Menu
            if preview not in (None, '', 'http://', 'https://'):
                add_dir(COLOR1(local_string(30021) + ' ' + name + ' ' + local_string(30020) + ' ' + version), preview, 2, icon, fanart, COLOR2(description), name2=name, version=version, isFolder=False)  # Video Previews
                
        elif '22' in kodi_ver and kodiversion == 'K22':
            add_dir(COLOR2(f'[B]{name}[/B] -- (v{version} / {buildsize})'), url, 3, icon, fanart, description, name2=name, version=version, kodi=kodiversion, size=buildsize, isFolder=False) # K22 Build Menu
            if preview not in (None, '', 'http://', 'https://'):
                add_dir(COLOR1(local_string(30021) + ' ' + name + ' ' + local_string(30020) + ' ' + version), preview, 2, icon, fanart, COLOR2(description), name2=name, version=version, isFolder=False)  # Video Previews

        elif not any(x in kodiversion for x in kodi_versions):
            add_dir(COLOR2(f'{name} (v{version})'), url, 3, icon, fanart, description, name2=name, version=version, isFolder=False)  # Standard Build Menu
            if preview not in (None, '', 'http://', 'https://'):
                add_dir(COLOR1(local_string(30021) + ' ' + name + ' ' + local_string(30020) + ' ' + version), preview, 2, icon, fanart, COLOR2(description), name2=name, version=version, isFolder=False) 

def submenu_maintenance():
    add_dir(COLOR1('<><> [B]Kodi Check-Up[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    if CURRENT_BUILD not in ['No Build Installed', 'No Build', 'NetKlix Lite', 'NetKlix Plus']:
        add_dir(COLOR4(f'Total Build Size:  {buildsize}MB'), '', '', addon_icon, addon_fanart, COLOR2('Total size on disk of your installed build'), isFolder=False)  # Current Build Size
    if cleanup > 400:
        add_dir(COLOR3(f'Clean Now:  {cleanup}MB'), '', '', addon_icon, addon_fanart, COLOR2('Total clean-up is above 250MB'), isFolder=False)  # Total clean-up > 250MB
    else:
        add_dir(COLOR4(f'Available to Clean:  {cleanup}MB'), '', '', addon_icon, addon_fanart, COLOR2('Total data available to clean'), isFolder=False)  # Total clean-up
    add_dir(COLOR1('<><> Clean Kodi <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    add_dir(COLOR2(f'Clear All  [{cleanup}MB]'),'',31,addon_icon,addon_fanart,COLOR2('Clear both packages and thumbnail folders to free up space.'),isFolder=False)  # Clear Packages & Thumbnails
    add_dir(COLOR2(f'Clear Packages  [{packagesize}MB]'),'',6,addon_icon,addon_fanart,COLOR2(local_string(30005)),isFolder=False)  # Clear Packages
    add_dir(COLOR2(f'Clear Thumbnails  [{thumbnailsize}MB]'),'',7,addon_icon,addon_fanart,COLOR2(local_string(30008)),isFolder=False)  # Clear Thumbnails
    add_dir(COLOR2('Kodi Fresh Start'), '', 4, addon_icon, addon_fanart, COLOR2(local_string(30003)), isFolder=False) # Fresh Start
    
    add_dir(COLOR1('<><> [B]System Check-Up[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    if total_space > 1024:
        add_dir(COLOR2(f'Capacity:  {round((total_space / 1024), 2)}GB  [100%]'), '', '', addon_icon, addon_fanart, COLOR2('Total size of your HDD/SSD'), isFolder=False)  # Total Size GB
    else:
        add_dir(COLOR2(f'Capacity:  {round((total_space))}MB'), '', '', addon_icon, addon_fanart, COLOR2('Total size of your HDD/SSD'), isFolder=False)  # Total Size MB
    if used_space > 1024:
        add_dir(COLOR2(f'Used Space:  {round((used_space / 1024), 2)}GB  [{used_perc}]'), '', '', addon_icon, addon_fanart, COLOR2('Total used HDD/SSD space'), isFolder=False)  # Total Used Space GB
    else:
        add_dir(COLOR2(f'Used Space:  {round((used_space))}MB  [{used_perc}]'), '', '', addon_icon, addon_fanart, COLOR2('Total used HDD/SSD space'), isFolder=False)  # Total Used Space MB
    if free_space > 1024:
        add_dir(COLOR2(f'Free Space:  {round((free_space / 1024), 2)}GB  [{free_perc}]'), '', '', addon_icon, addon_fanart, COLOR2('Total free HDD/SSD space'), isFolder=False)  # Total Free Space GB
    else:
        add_dir(COLOR2(f'Free Space:  {round((free_space))}MB  [{free_perc}]'), '', '', addon_icon, addon_fanart, COLOR2('Total free HDD/SSD space'), isFolder=False)  # Total Free Space MB

def submenu_tools():   
    add_dir(COLOR1('<><> [B]Backup & Restore[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    add_dir(COLOR2('Backup/Restore Build'),'',12,addon_icon,addon_fanart, COLOR2('Backup and Restore Build'))  # Backup Build
    add_dir(COLOR2('Backup/Restore GUI & Skin Settings'),'',19,addon_icon,addon_fanart,COLOR2('Backup/Restore GUI & Skin Settings'))
    
    add_dir(COLOR1('<><> [B]Whitelist Add-ons[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    add_dir(COLOR2('Add To Whitelist'),'',11,addon_icon,addon_fanart,COLOR2(local_string(30064)), isFolder=False)  # Add to Whitelist
    add_dir(COLOR2('Remove From Whitelist'),'', 33, addon_icon,addon_fanart,COLOR2('Remove items from whitelist'), isFolder=False) # Remove from Whitelist
    
    add_dir(COLOR1('<><> [B]Wizard Tools[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    if chk_splash == None or chk_splash == 'true':
        add_dir(COLOR2('Disable Kodi Splash Screen'),'',29,addon_icon,addon_fanart,COLOR2(local_string(30113)),isFolder=False)  # Disable Kodi Splash Screen
    else:
        add_dir(COLOR2('Enable Kodi Splash Screen'),'',29,addon_icon,addon_fanart,COLOR2(local_string(30113)),isFolder=False)  # Enable Kodi Splash Screen
    if chk_skin_override():
        add_dir(COLOR2('Enable Skin Override Protection'),'',30,addon_icon,addon_fanart,COLOR2(local_string(30115)),isFolder=False)  # Enable Skin Override
    else:
        add_dir(COLOR2('Disable Skin Override Protection'),'',30,addon_icon,addon_fanart,COLOR2(local_string(30115)),isFolder=False)  # Disable Skin Override
    #add_dir(COLOR2('Check for Broken Repos'),'', 37, addon_icon,addon_fanart,COLOR2(local_string(30122)), isFolder=False) # Broken Repository Check
    if '21' or '22' in kodi_ver:
        add_dir(COLOR2(local_string(30112)),'',8,addon_icon,addon_fanart,COLOR2(local_string(30009)),isFolder=False)  # Video Cache Settings K21 & K22
        add_dir(COLOR2('View Cache Settings'),'',75,addon_icon,addon_fanart,COLOR2('View video cache settings. Requires GUI settings level advanced or higher.'), isFolder=False) # View Video Cache Settings
    #add_dir(COLOR2(f'Force Update Addons'),'', 32, addon_icon,addon_fanart,COLOR2(f'Triggers a forced update of enabled add-on repositories.\n\nLast Checked:  {lastchk}'), isFolder=False) # Force update addons
    #add_dir(COLOR2('Force Close Kodi'),'', 18, addon_icon,addon_fanart,COLOR2('Force Close Kodi'), isFolder=False) # Force Close Kodi
    add_dir(COLOR2('Speedtest'),'',28,addon_icon,addon_fanart,COLOR2('Complete an Internet Speedtest'), isFolder=False) # Run Internet Speedtest

    #add_dir(COLOR1('<><> [B]Shortcuts[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1('Shortcuts'),isFolder=False) # Shortcuts
    #add_dir(COLOR2('Kodi Settings'),'',150,addon_icon,addon_fanart, COLOR2('Kodi Settings Shortcuts'))  # Kodi Settings Menu Shortcuts
    #add_dir(COLOR2('Kodi Builtins'),'',152,addon_icon,addon_fanart, COLOR2('Kodi Builtin Shortcuts'))  # Kodi Builtins Shortcuts
    #add_dir(COLOR2('Kodi Specific'),'',151,addon_icon,addon_fanart, COLOR2('Kodi Specific Setting Shortcuts'))  # Kodi Specific Shortcuts
    #add_dir(COLOR2('Add-on Specific'),'',153,addon_icon,addon_fanart, COLOR2('Add-on Specific Shortcuts'))  # Add-on Specific Shortcuts
    #add_dir(COLOR2('Addon Browser'),'',154,addon_icon,addon_fanart, COLOR2('Add-on Browser Shortcuts'))  # Add-on Browser
    #add_dir(COLOR2('Force Close Kodi'),'', 18, addon_icon,addon_fanart,COLOR2('Force Close Kodi'), isFolder=False) # Force Close Kodi

'''def submenu_stats():
    add_dir(COLOR1('<><> [B]Build Information[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    add_dir(COLOR4(f'Kodi Version:  v{kodi_ver}'), '', '', addon_icon, addon_fanart, COLOR2(local_string(30118)), isFolder=False)  # Show the current Kodi version installed
    if CURRENT_BUILD not in ['No Build Installed', 'No Build']:
        add_dir(COLOR4(f'Current Build:   {CURRENT_BUILD} v{BUILD_VERSION}'), '', '', addon_icon, addon_fanart, COLOR2(local_string(30111)), isFolder=False)  # Show the current installed build
        add_dir(COLOR4(f'Install Date::   {inst_date}'), '', '', addon_icon, addon_fanart, COLOR2('Build install date'), isFolder=False)  # Build install date
    else:
        add_dir(COLOR3(f'Current Build:   No Build Installed!'), '', '', addon_icon, addon_fanart, COLOR2(local_string(30111)), isFolder=False)  # No build installed
    add_dir(COLOR4(f'Build Skin:  {cur_skin}'), '', '', addon_icon, addon_fanart, COLOR2('Current skin'), isFolder=False)  # Current Skin
    add_dir(COLOR1('<><> [B]Installed Add-ons & Repos[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    add_dir(COLOR2(f'Video Add-ons  [{vid_list}]'), '', '', addon_icon, addon_fanart, COLOR2('Total video add-ons installed'), isFolder=False)  # Video Add-ons
    add_dir(COLOR2(f'Program Add-ons  [{prg_list}]'), '', '', addon_icon, addon_fanart, COLOR2('Total program add-ons installed'), isFolder=False)  # Program Add-ons
    add_dir(COLOR2(f'Repositories  [{repo_list}]'), '', '', addon_icon, addon_fanart, COLOR2('Total repositories installed'), isFolder=False)  # Repositories
    add_dir(COLOR2(f'Updates Available  [{add_up}]'), '', '', addon_icon, addon_fanart, COLOR2('Available add-on updates'), isFolder=False)  # Add-on Updates

    add_dir(COLOR1('<><> [B]System Memory[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    add_dir(COLOR2(f'Total RAM:  {total_mem}  [100%]'), '', '', addon_icon, addon_fanart, COLOR2('Total RAM'), isFolder=False)  # Total RAM
    add_dir(COLOR2(f'Used RAM:  {used_mem}  [{used_mem_perc}]'), '', '', addon_icon, addon_fanart, COLOR2('Used RAM'), isFolder=False)  # Used RAM
    add_dir(COLOR2(f'Free RAM:  {free_mem}  [{free_mem_perc}]'), '', '', addon_icon, addon_fanart, COLOR2('Free RAM'), isFolder=False)  # Free RAM
    
    add_dir(COLOR1('<><> [B]System Stats[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''),isFolder=False)
    add_dir(COLOR2(f'Operating System:  {os_info}'), '', '', addon_icon, addon_fanart, COLOR2('Installed Operating System'), isFolder=False)  # Operating System
    add_dir(COLOR2(f'IP Address:  {ip_addr}   {net_link}'), '', '', addon_icon, addon_fanart, COLOR2('System IP Address'), isFolder=False)  # IP Address
    add_dir(COLOR2(f'CPU Frequency:  {cpu_freq}'), '', '', addon_icon, addon_fanart, COLOR2('CPU Frequency'), isFolder=False)  # CPU Frequency
    add_dir(COLOR2(f'Uptime:  {uptime}'), '', '', addon_icon, addon_fanart, COLOR2('System Uptime'), isFolder=False)  # Uptime
    add_dir(COLOR2(f'Total Uptime:  {total_uptime}'), '', '', addon_icon, addon_fanart, COLOR2('Total System Uptime'), isFolder=False)  # Total Uptime'''


def backup_restore():
    xbmcplugin.setPluginCategory(HANDLE, COLOR1('Backup/Restore'))
    add_dir(COLOR1('<><> [B]Backup/Restore[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Backup Build'),'',13,addon_icon,addon_fanart, COLOR2('Backup Build'), isFolder=False)  # Backup Build
    add_dir(COLOR2('Restore Backup'),'',14, addon_icon,addon_fanart, COLOR2('Restore Backup'))  # Restore Backup
    add_dir(COLOR2('Change Backups Folder Location'),'',16,addon_icon,addon_fanart, COLOR2('Change the location where backups will be stored and accessed.'), isFolder=False)  # Backup Location
    add_dir(COLOR2('Reset Backups Folder Location'),'',17,addon_icon,addon_fanart, COLOR2('Set the backup location to its default.'), isFolder=False)  # Reset Backup Location

def restore_gui_skin():
    add_dir(COLOR1('<><> [B]Backup/Restore GUI & Skin Settings[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Backup GUI & Skin Settings'),'',22,addon_icon,addon_fanart,COLOR2('Backup GUI & Skin Settings'), isFolder=False) # Backup GUI & Skin Settings
    add_dir(COLOR2('Restore GUI Settings'),'',23, addon_icon,addon_fanart, COLOR2('Restore Your GUI Settings'), isFolder=False) # Backup GUI Settings
    add_dir(COLOR2('Restore Skin Settings'),'',24, addon_icon,addon_fanart, COLOR2('Restore Your Skin Settings'), isFolder=False) # Backup Skin Settings
    add_dir(COLOR2('Restore Build Default GUI Settings'),'',20,addon_icon,addon_fanart,COLOR2('Restore GUI Settings'), isFolder=False)  # Restore Default GUI Settings
    add_dir(COLOR2('Restore Build Default Skin Settings'),'',21, addon_icon,addon_fanart, COLOR2('Restore Skin Settings'), isFolder=False) # Restore Default Skin Settings

#Kodi Settings
def kodi_settings():
    add_dir(COLOR1('<><> [B]Kodi Settings[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('File Manager'),'',105,addon_icon,addon_fanart,COLOR2('File Manager'), isFolder=False)
    add_dir(COLOR2('Addon Browser'),'',106, addon_icon,addon_fanart, COLOR2('Addon Browser'), isFolder=False)
    add_dir(COLOR2('System Info'),'',107,addon_icon,addon_fanart,COLOR2('System Info'), isFolder=False)
    add_dir(COLOR2('Event Log'),'',108, addon_icon,addon_fanart, COLOR2('Event Log'), isFolder=False)
    add_dir(COLOR2('Player'),'',109,addon_icon,addon_fanart,COLOR2('Player Settings'), isFolder=False)
    add_dir(COLOR2('Media'),'',110,addon_icon,addon_fanart,COLOR2('Media Settings'), isFolder=False)
    add_dir(COLOR2('PVR & Live TV'),'',111,addon_icon,addon_fanart,COLOR2('PVR & Live TV Settings'), isFolder=False)
    add_dir(COLOR2('Services'),'',112, addon_icon,addon_fanart, COLOR2('Services'), isFolder=False)
    add_dir(COLOR2('Interface'),'',113,addon_icon,addon_fanart,COLOR2('Appearance Settings'), isFolder=False)
    add_dir(COLOR2('System'),'',114, addon_icon,addon_fanart, COLOR2('System Settings'), isFolder=False)

#Kodi Specific Settings  
def kodi_specific():
    add_dir(COLOR1('<><> [B]Force Update[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Force Update Addons'),'', 32, addon_icon,addon_fanart,COLOR2('Force update add-ons'), isFolder=False) # Force update addons
    
    add_dir(COLOR1('<><> [B]Player Settings[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Audio & Subtitle Language'),'',76, addon_icon,addon_fanart, COLOR2('Audio Language'), isFolder=False)
    #add_dir(COLOR2('Subtitle Language'),'',77, addon_icon,addon_fanart, COLOR2('Subtitle Language'), isFolder=False)
    add_dir(COLOR2('Subtitles'),'',78, addon_icon,addon_fanart, COLOR2('Subtitle Settings'), isFolder=False)
    
    add_dir(COLOR1('<><> [B]PVR Settings[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Clear Data'),'',80,addon_icon,addon_fanart,COLOR2('Clear Settings'), isFolder=False)
    #add_dir(COLOR2('Group Manager'),'',81, addon_icon,addon_fanart, COLOR2('Group Settings'), isFolder=False)

    add_dir(COLOR1('<><> [B]Service Settings[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Video Cache Settings'),'',75,addon_icon,addon_fanart,COLOR2('View Video Cache  Settings'), isFolder=False)
    
    add_dir(COLOR1('<><> [B]Look & Feel Settings[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Change Skin'),'',83,addon_icon,addon_fanart,COLOR2('Change Skin Settings'), isFolder=False)
    add_dir(COLOR2('Configure Skin'),'',84, addon_icon,addon_fanart, COLOR2('Configure Skin Settings'), isFolder=False)
    add_dir(COLOR2('Colors'),'',85,addon_icon,addon_fanart,COLOR2('Color Settings'), isFolder=False)
    add_dir(COLOR2('Fonts'),'',86, addon_icon,addon_fanart, COLOR2('Font Settings'), isFolder=False)
    add_dir(COLOR2('Regional'),'',87,addon_icon,addon_fanart,COLOR2('Regional Settings'), isFolder=False)
    
    add_dir(COLOR1('<><> [B]System Settings[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Manage Dependencies'),'',90,addon_icon,addon_fanart,COLOR2('Manage Dependencies Settings'), isFolder=False)
    #add_dir(COLOR2('Unknown Sources'),'',11, addon_icon,addon_fanart, COLOR2('Unknown Sources Settings'), isFolder=False)
    add_dir(COLOR2('Logging'),'',92,addon_icon,addon_fanart,COLOR2('Logging Settings'), isFolder=False)
    
    add_dir(COLOR1('<><> [B]System Information[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('System Summary'),'',95,addon_icon,addon_fanart,COLOR2('System Summary'), isFolder=False)
    add_dir(COLOR2('Storage'),'',96, addon_icon,addon_fanart, COLOR2('Storage'), isFolder=False)
    add_dir(COLOR2('Network'),'',97,addon_icon,addon_fanart,COLOR2('Network'), isFolder=False)
    add_dir(COLOR2('Graphics'),'',98, addon_icon,addon_fanart, COLOR2('Graphics'), isFolder=False)
    add_dir(COLOR2('Hardware'),'',99,addon_icon,addon_fanart,COLOR2('Hardware'), isFolder=False)

#Add-on Specific Settings
def addon_specific():
    #add_dir(COLOR1('<><> [B]Add-on & Skin MDblist Shortcuts[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1('Add-on Shortcuts'), isFolder=False)
    #add_dir(COLOR2('TMDbH MDblist API Key'),'',50,addon_icon,addon_fanart,COLOR2('TMDbH MDblist API Key'), isFolder=False)
    #add_dir(COLOR2('Fentastic MDblist API Key'),'',65,addon_icon,addon_fanart,COLOR2('Nimbus MDblist API Key'), isFolder=False)
    #add_dir(COLOR2('Nimbus MDblist API Key'),'',75,addon_icon,addon_fanart,COLOR2('Nimbus MDblist API Key'), isFolder=False)
    #add_dir(COLOR2('Altus MDblist API Key'),'',75,addon_icon,addon_fanart,COLOR2('Nimbus MDblist API Key'), isFolder=False)
    
    #Add-on Settings
    add_dir(COLOR1('<><> [B]Account Manager Shortcuts[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Accounts'),'',62, addon_icon,addon_fanart, COLOR2('Accounts'), isFolder=False)
    add_dir(COLOR2('Manage'),'',63,addon_icon,addon_fanart,COLOR2('Manage Accounts'), isFolder=False)
    add_dir(COLOR2('Backup & Restore'),'',64, addon_icon,addon_fanart, COLOR2('Backup & Restore Settings'), isFolder=False)

    add_dir(COLOR1('<><> [B]ResolveURL Shortcuts[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Real-Debrid'),'',51, addon_icon,addon_fanart, COLOR2('ResolveURL Real-Debrid'), isFolder=False)
    add_dir(COLOR2('Premiumize'),'',52,addon_icon,addon_fanart,COLOR2('ResolveURL Premiumize'), isFolder=False)
    add_dir(COLOR2('All-Debrid'),'',53, addon_icon,addon_fanart, COLOR2('ResolveURL All-Debrid'), isFolder=False)

#Kodi Builtins
def kodi_builtins():
    add_dir(COLOR1('<><> [B]Kodi System Builtins[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('Reload Skin'),'',120,addon_icon,addon_fanart,COLOR2('Reloads the current skin (saves power cycling)'), isFolder=False)
    add_dir(COLOR2('Activate Screensaver'),'',121, addon_icon,addon_fanart, COLOR2('Starts the screensaver'), isFolder=False)
    add_dir(COLOR2('Clean Video Library'),'',122, addon_icon,addon_fanart, COLOR2('This funtion will perform a number of cleanup tasks on your video database and can be run if you have moved, deleted or renamed files. Takes either "video" or "music" as a parameter to begin cleaning the corresponding database.'), isFolder=False)
    add_dir(COLOR2('Update Video Library'),'',123,addon_icon,addon_fanart,COLOR2('Update the video database'), isFolder=False)
    add_dir(COLOR2('Reboot'),'',124, addon_icon,addon_fanart, COLOR2('Cold reboots the system (power cycle)'), isFolder=False)
    add_dir(COLOR2('Quit'),'',125, addon_icon,addon_fanart, COLOR2('Quits Kodi'), isFolder=False)
    add_dir(COLOR2('Power Down'),'',126,addon_icon,addon_fanart,COLOR2('Powerdown system'), isFolder=False)
    add_dir(COLOR2('Reboot'),'',127, addon_icon,addon_fanart, COLOR2('Cold reboots the system (power cycle)'), isFolder=False)
    add_dir(COLOR2('Shutdown'),'',128,addon_icon,addon_fanart,COLOR2('Trigger default Shutdown action defined in System Settings'), isFolder=False)
    add_dir(COLOR2('Hibernate'),'',129,addon_icon,addon_fanart,COLOR2('Hibernate (S4) the System'), isFolder=False)
    add_dir(COLOR2('Suspend'),'',130,addon_icon,addon_fanart,COLOR2('Suspends (S3 / S1 depending on bios setting) the System'), isFolder=False)

def addonbrowser():
    add_dir(COLOR1('<><> [B]Addon Browser[/B] <><>'),'','',addon_icon,addon_fanart, COLOR1(''), isFolder=False)
    add_dir(COLOR2('All Add-ons'),'',135,addon_icon,addon_fanart,COLOR2('All Add-ons'), isFolder=False)
    add_dir(COLOR2('Repositories'),'',136, addon_icon,addon_fanart, COLOR2('Repositories'), isFolder=False)
    add_dir(COLOR2('Audio Encoders'),'',137,addon_icon,addon_fanart,COLOR2('Audio Encoders'), isFolder=False)
    add_dir(COLOR2('Game Add-ons'),'',138, addon_icon,addon_fanart, COLOR2('Game Add-ons'), isFolder=False)
    add_dir(COLOR2('Information Providers'),'',139,addon_icon,addon_fanart,COLOR2('Information Providers'), isFolder=False)
    add_dir(COLOR2('Look & feel'),'',140,addon_icon,addon_fanart,COLOR2('Look & feel'), isFolder=False)
    add_dir(COLOR2('Peripherals'),'',141, addon_icon,addon_fanart, COLOR2('Peripherals'), isFolder=False)
    add_dir(COLOR2('Services'),'',142,addon_icon,addon_fanart,COLOR2('Services'), isFolder=False)
    add_dir(COLOR2('Video Add-ons'),'',143, addon_icon,addon_fanart, COLOR2('Video Add-ons'), isFolder=False)
    add_dir(COLOR2('Web Interface Add-ons'),'',144,addon_icon,addon_fanart,COLOR2('Web Interface Add-ons'), isFolder=False)
     
'''def authorize_menu():  ### deprecated use authorize.py methods
    xbmcplugin.setPluginCategory(HANDLE, local_string(30027))  # Authorize Services
    response = get_page(authorize)
    builds = json.loads(response)['items']
    for build in builds:
        name = (build.get('name', 'Unknown'))
        url = (build.get('url', ''))
        icon = (build.get('icon', addon_icon))
        fanart = (build.get('fanart', addon_fanart))
        add_dir(name,url,2,icon,fanart,name,name2=name,version='' ,isFolder=False)'''
