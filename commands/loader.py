from commands import balance, points, shop

def load_commands(tree):
    balance.register(tree)
    points.register(tree)
    shop.register(tree)
    print('Loaded commands:', [c.name for c in tree.get_commands()])
