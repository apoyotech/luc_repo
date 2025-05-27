#Inspired by drinfernos Openwizard Repo Check

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import os
import re
from .addonvar import addon_name, addons_path
from .notify import notification

translatePath = xbmcvfs.translatePath
log_file_path = translatePath('special://logpath/kodi.log')
logfile = os.path.join(log_file_path)

def percentage(part, whole):
    return 100 * float(part)/float(whole)

def read_from_file(file, mode='r'):
    f = open(file, mode, encoding='utf-8')
    a = f.read()
    f.close()
    return a

def check_repos():
    progress_dialog = xbmcgui.DialogProgress()
    progress_dialog.create('Checking Repositories...')
    
    goodrepos = []
    xbmc.executebuiltin('UpdateAddonRepos')
    repolist = [i for i in os.listdir(addons_path) if i.startswith('repo')]

    if len(repolist) == 0:
        progress_dialog.close()
        return
    
    sleeptime = len(repolist)
    start = 0
    while start < sleeptime:
        start += 1
        if progress_dialog.iscanceled():
            break
        perc = int(percentage(start, sleeptime))
        progress_dialog.update(perc,
                      '\n' + f'Checking: {repolist[start-1][0:]}')
        xbmc.sleep(1000)
    if progress_dialog.iscanceled():
        progress_dialog.close()
        sys.exit()
    progress_dialog.close()
    
    log = read_from_file(logfile)
    repos = re.compile('CRepositoryUpdateJob(.+?) checksum not changed.').findall(log)

    for item in repos:
        repo = item.replace('[', '').replace(']', '')
        if repo not in goodrepos:
            goodrepos.append(repo)
    badrepos = list(set(repolist) - set(goodrepos))


    if len(badrepos) > 0:
        msg = f'[B]<><><><><> Broken Repositories <><><><><>[/B]\n\n[COLOR red][B]'
        msg += '[CR]'.join(badrepos)
        msg += '[/B][/COLOR]'
        notification(msg)
    else:
        sys.exit()

