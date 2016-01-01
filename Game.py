import libtcodpy as libtcod

class Rect:
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
        
    def center(self):
        centerX = (self.x1 + self.x2) / 2
        centerY = (self.y1 + self.y2) / 2
        return (centerX, centerY)
    
    def intersect(self, other_rect):
        return (self.x1 <= other_rect.x2 and self.x2 >= other_rect.x1 and self.y1 <= other_rect.y2 and self.y2 >= other_rect.y1)
        
class Object:
    #generic class for handling anything in the game
    def __init__(self, x, y, char, name, color, blocks = False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        
    def move(self, dx, dy):
        if((0 <= (self.x + dx)  and (self.x + dx) < MAP_WIDTH) and (0 <= (self.y + dy) and (self.y + dy) < MAP_HEIGHT)):
            if not is_blocked(self.x + dx, self.y + dy):
                self.x += dx
                self.y += dy
        
    def draw(self):
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)
        
    def clear(self):
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

class Tile:
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
        
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
        
        self.explored = False

def offset(col, row, rowLen):
    return row * rowLen + col

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)

def handle_keys():
    global fov_recompute
    key = libtcod.console_check_for_keypress()
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        #Alt+Enter: toggle fullscreen
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
 
    elif key.vk == libtcod.KEY_ESCAPE:
        return "Exit"  #exit game
    
    if game_state == GameStates.PLAYING:
        #movement keys
        if libtcod.console_is_key_pressed(libtcod.KEY_UP):
            player_move_or_attack(0, -1)
            fov_recompute = True
     
        elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
            player_move_or_attack(0, 1)
            fov_recompute = True
     
        elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
            player_move_or_attack(-1, 0)
            fov_recompute = True
     
        elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
            player_move_or_attack(1, 0)
            fov_recompute = True
        else:
            return PlayerActions.NO_MOVE

def player_move_or_attack(dx, dy):
    global fov_rexompute
    
    x = player.x + dx
    y = player.y + dy
    
    target = None
    for gameObject in objects:
        if gameObject.x == x and gameObject.y == y:
            target = gameObject
            break
    
    if target is not None:
        print 'The ' + target.name + ' laughs at your puny efforts to attack him!'
    else:
        player.move(dx, dy)
        fov_recompute = True
        
def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
    if fov_recompute:

        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
        
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = gameMap[offset(x, y, MAP_WIDTH)].block_sight
                if not visible:
                    if gameMap[offset(x, y, MAP_WIDTH)].explored:
                        if(wall):
                            libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
                        else:
                            libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)
                else:
                    if(wall):
                        libtcod.console_set_char_background(con, x, y, color_light_wall, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, color_light_ground, libtcod.BKGND_SET)
                    gameMap[offset(x, y, MAP_WIDTH)].explored = True
    
    for gameObject in objects:
        gameObject.draw()
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def make_map():
    global gameMap
    
    gameMap = [Tile(True) for t in range(MAP_WIDTH * MAP_HEIGHT)]
    
    rooms = []
    num_rooms = 0
   
    for r in range(MAX_ROOMS):
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
       
        new_room = Rect(x, y, w, h)
        
        failed = False
        for room in rooms:
            if new_room.intersect(room):
                failed = True
                break
        if not failed:
            create_room(new_room)
            place_monsters(new_room)
            
            (cX, cY) = new_room.center()
            
            if num_rooms == 0:
                player.x = cX
                player.y = cY
            else:
                (oldX, oldY) = rooms[num_rooms-1].center()
                
                if libtcod.random_get_int(0, 0, 1) == 1:
                    create_h_tunnel(oldX, cX, oldY)
                    create_v_tunnel(oldY, cY, cX)
                else:
                    create_v_tunnel(oldY, cY, oldX)
                    create_h_tunnel(oldX, cX, cY)
            rooms.append(new_room)
            num_rooms += 1

def create_room(room_rect):
    global gameMap
    for x in range(room_rect.x1 + 1, room_rect.x2):
        for y in range(room_rect.y1 + 1, room_rect.y2):
            gameMap[offset(x, y, MAP_WIDTH)].blocked = False
            gameMap[offset(x, y, MAP_WIDTH)].block_sight = False
            
def create_h_tunnel(x1, x2, y):
    global gameMap
    for x in range(min(x1, x2), max(x1, x2) + 1):
        gameMap[offset(x, y, MAP_WIDTH)].blocked = False
        gameMap[offset(x, y, MAP_WIDTH)].block_sight = False
        
def create_v_tunnel(y1, y2, x):
    global gameMap
    for y in range(min(y1, y2), max(y1, y2) + 1):
        gameMap[offset(x, y, MAP_WIDTH)].blocked = False
        gameMap[offset(x, y, MAP_WIDTH)].block_sight = False
        
def place_monsters(room_rect):
    num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)
    
    for i in range(num_monsters):
        x = libtcod.random_get_int(0, room_rect.x1, room_rect.x2)
        y = libtcod.random_get_int(0, room_rect.y1, room_rect.y2)
        
        if not is_blocked(x, y):
            typeOfMonster = libtcod.random_get_int(0, 0, 100)
            if typeOfMonster < 80:
                #Orc
                monster = Object(x, y, 'o', "Orc", libtcod.desaturated_green, blocks = True)
            else:
                #Troll
                monster = Object(x, y, 'T', "Troll", libtcod.darker_green, blocks = True)
            
            objects.append(monster)

def is_blocked(x, y):
    if(gameMap[offset(x, y, MAP_WIDTH)].blocked):
        return True
    
    for gameObject in objects:
        if gameObject.blocks and gameObject.x == x and gameObject.y == y:
            return True
    return False

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
MAP_WIDTH = 80
MAP_HEIGHT = 45
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3
LIMIT_FPS = 20

FOV_ALGO = 0
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

GameStates = enum('PLAYING')
PlayerActions = enum('NONE', 'NO_MOVE')

color_dark_wall = libtcod.Color(0, 0, 100)
color_light_wall = libtcod.Color(130, 110, 50)
color_dark_ground = libtcod.Color(50, 50, 150)
color_light_ground = libtcod.Color(200, 100, 50)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Roguez", False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
libtcod.sys_set_fps(LIMIT_FPS)

player = Object(0, 0, '@', "Player", libtcod.white, blocks = True)
objects = [player]

make_map()
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not gameMap[offset(x, y, MAP_WIDTH)].block_sight, not gameMap[offset(x, y, MAP_WIDTH)].blocked)
fov_recompute = True

game_state = GameStates.PLAYING
player_action = PlayerActions.NONE

while not libtcod.console_is_window_closed():
    render_all()
    libtcod.console_flush()
    
    for gameObject in objects:
        gameObject.clear()
    player_action = handle_keys()
    
    if player_action == "Exit":
        break;
    
    