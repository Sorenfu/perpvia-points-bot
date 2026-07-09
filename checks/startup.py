import os

def validate_env():
    for key in ['DISCORD_TOKEN','GUILD_ID']:
        if not os.getenv(key):
            raise RuntimeError(f'Missing {key}')
    print('Environment OK')
