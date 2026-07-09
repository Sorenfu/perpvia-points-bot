import os

def validate_env():
    required=['DISCORD_TOKEN']
    missing=[x for x in required if not os.getenv(x)]
    if missing:
        raise RuntimeError('Missing config: '+','.join(missing))
    print('Environment OK')
