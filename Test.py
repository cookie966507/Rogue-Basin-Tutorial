import libtcodpy as libtcod

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
        playerY -= 1
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
        playerY += 1
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
        playerX -= 1
 
    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
        playerX += 1
        

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

#libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, "Roguez", False)
libtcod.sys_set_fps(LIMIT_FPS)

playerX = SCREEN_WIDTH/2
playerY = SCREEN_HEIGHT/2

while not libtcod.console_is_window_closed():
    libtcod.console_set_default_foreground(0, libtcod.white)
    libtcod.console_put_char(0, playerX, playerY, '@', libtcod.BKGND_NONE)
    libtcod.console_flush()
    
    libtcod.console_put_char(0, playerX, playerY, ' ', libtcod.BKGND_NONE)
    if(handle_keys()):
        break;