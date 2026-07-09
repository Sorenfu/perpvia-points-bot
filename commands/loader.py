from commands import balance,points,daily,shop

def load_commands(tree):
    balance.register(tree)
    points.register(tree)
    daily.register(tree)
    shop.register(tree)
