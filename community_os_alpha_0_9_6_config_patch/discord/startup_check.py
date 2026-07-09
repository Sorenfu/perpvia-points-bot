def startup_check(config):
    required=['guild_id','application_id']
    for item in required:
        if item not in config:
            raise Exception(f'Missing config: {item}')
    return True
