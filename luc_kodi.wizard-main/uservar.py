'''#####-----Build File-----#####'''
buildfile = 'https://mia.nl.tab.digital/s/Sd5ZgsCyFSJ8R99/download/builds.xml'

'''#####-----Notifications File-----#####'''
notify_url  = 'http://CHANGEME'

'''#####-----Changelog Directory-----#####'''
changelog_dir  = 'http://CHANGEME'

'''#####-----Videos File-----#####'''
videos_url = 'http://CHANGEME'

'''#####-----Excludes-----#####'''
excludes  = ['plugin.video.whatever']

#Change Build Name(s) Guide
'''
1. Add your Old/New build names to the BUILDS variable below.
2. Update your builds file to remove the Old Build and add the New Build.
   IMPORTANT: Apply the Old Build version to the New Build entry.
3. Bump the version of your New Build.
4. At first run the user will be prompted to install the update (Your New Build).'''

#Change Build Name(s)
BUILDS = [{'Old Build': "Old Build_1", 'New Build': "New Build_1"},
          {'Old Build': "Old Build_2", 'New Build': "New Build_2"}]
