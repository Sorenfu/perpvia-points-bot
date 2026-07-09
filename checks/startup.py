import os

def validate_env():
    for key in ['DISCORD_TOKEN','GUILD_ID']:
        if not os.getenv(key):
            raise RuntimeError('Missing '+key)
    print('Environment OK')
