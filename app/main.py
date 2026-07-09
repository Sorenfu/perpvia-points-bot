class CommunityOS:
    version='Beta 1.0.6 Full Business Integration'
    modules=[
        'points','daily','message','invite',
        'role_reward','shop','campaign',
        'admin','analytics'
    ]
    def start(self):
        print('Community OS Starting')
        print('Modules:',self.modules)

if __name__=='__main__':
    CommunityOS().start()
