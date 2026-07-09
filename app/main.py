import os

class CommunityOS:
    version='Beta 1.0 Stable'
    modules=['points','daily','invite','message','roles','shop','campaign','admin','analytics','profile','ai']

    def start(self):
        print('Community OS Starting')
        print('Modules Loaded:', self.modules)

if __name__=='__main__':
    CommunityOS().start()
