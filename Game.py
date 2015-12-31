import libtcodpy as libtcod

class Object:
    #generic class for handling anything in the game
    def __init__(self, x, y, char, color):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        
    def move(self, dx, dy):
        if((0 <= (self.x + dx)  and (self.x + dx) < MAP_WIDTH) and (0 <= (self.y + dy) and (self.y + dy) < MAP_HEIGHT)):
            if not gameMap[offset(self.x + dx, self.y + dy, MAP_WIDTH)].blocked:
                self.x += dx
                self.y += dy
        
    def draw(self):
        libtcod.console_set_default_foreground(con, self.color)
        libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
        
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

def offset(col, row, rowLen):
    return row * rowLen + col

def handle_keys():
    global playerX, playerY
    
    key = libtcod.console_check_for_keypress()
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return True  #exit game
    
    #movement keys
    if libtcod.console_is_key_pressed(libtcod.KEY_UP):
        player.move(0, -1)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        player.move(0, 1)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        player.move(-1, 0)
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        player.move(1, 0)
        
def render_all():
    for gameObject in objects:
        gameObject.draw()
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            wall = gameMap[offset(x, y, MAP_WIDTH)].block_sight
            if(wall):
                libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def make_map():
    global gameMap
    gameMap = [Tile(False) for t in range(MAP_WIDTH * MAP_HEIGHT)]
    gameMap[offset(30, 22, MAP_WIDTH)].blocked = True
    gameMap[offset(30, 22, MAP_WIDTH)].block_sight = True
    gameMap[offset(50, 22, MAP_WIDTH)].blocked = True
    gameMap[offset(50, 22, MAP_WIDTH)].block_sight = True

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45
LIMIT_FPS = 20

color_dark_wall = libtcod.Color(0, 0, 100)
color_dark_ground = libtcod.Color(50, 50, 150)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Roguez", False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)
npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)
objects = [npc, player]

make_map()

while not libtcod.console_is_window_closed():
    render_all()
    libtcod.console_flush()
    
    for gameObject in objects:
        gameObject.clear()
    if(handle_keys()):
        break;