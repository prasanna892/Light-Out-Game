"""###### Brain game ###########################################"""
'''#######################*+Light OUT+*#########################'''
"""####################################### By -> Prasanna ######"""

# How to win?
#      Just pass the entered red laser light the screen 
# through by rotating the mirrors

# Control
#   Rotate mirror  ->  Right click
#   p              ->  Out path visible

# Note's
#       1) After the passage of red light outside the screen, 
# next level start's automatically
#       2) Starting and ending mirror are highlighted by red tile
#       3) This game with infinate level creation

# Contacts
# Instagram: https://www.instagram.com/prasanna_rdj_fan 
# Mail ID: k.prasannagh@gmail.com
# YouTube: https://www.youtube.com/channel/UC8W9MLLVK0wZjg9DwJiyivQ

# Enjoy the game

'''#############################################################'''

# Importing required module
import pygame
from pygame import mixer
from random import choice
from PIL import Image, ImageFilter

# Initializing pygame and mixer
pygame.init()
mixer.init()

# Defining required variable
screen_width = 1000
screen_height = 600
tile_size = 50
RES = screen_width, screen_height = 1000, 600
clockobject = pygame.time.Clock()
fps = 30
mouse_clicked = False
mirror_group = pygame.sprite.Group()
m = [['0']*(screen_width//tile_size) for _ in range(screen_height//tile_size)]
light_collision_list = []
maze = out_path = MAP = None

# Setting window screen and window title
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Light Out')


# Loding the image using pillow for better quality
def scale_smoothing(path, size):
    pilImage = Image.open(path)
    resize_img = pilImage.resize(size)
    sharp_img = resize_img.filter(ImageFilter.SMOOTH_MORE)
    final_img = pygame.image.fromstring(sharp_img.tobytes(), sharp_img.size, sharp_img.mode)
    return final_img

# Function to change pygame image to PIL image then rotate it and change back to pygame image for better quality
def pygameTO_pil_rotate_TOpygame(image, angle):
    pil_string_image = pygame.image.tostring(image, "RGBA",False)
    pil_image = Image.frombytes("RGBA", image.get_size(), pil_string_image)
    pil_rotated_img = pil_image.rotate(angle, Image.BICUBIC, expand=True)
    pil_img_size = pil_rotated_img.size
    pil_img_size_half = pil_img_size[0]//2
    left = top = pil_img_size_half-tile_size//2
    right = bottom = pil_img_size_half+tile_size//2
    pil_cropped_image = pil_rotated_img.crop((left, top, right, bottom))
    rotated_image = pygame.image.fromstring(pil_cropped_image.tobytes(), pil_cropped_image.size, pil_cropped_image.mode)
    return rotated_image

# Function for rotate the image at pivot point and place on given position
def blitRotate(image, origin, pivot, angle):
    image_rect = image.get_rect(topleft = (origin[0] - pivot[0], origin[1]-pivot[1]))
    offset_center_to_pivot = pygame.math.Vector2(origin) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (origin[0] - rotated_offset.x, origin[1] - rotated_offset.y)
    rotated_image = pygameTO_pil_rotate_TOpygame(image, angle)
    rotated_image_rect = rotated_image.get_rect(center = rotated_image_center)
    return (rotated_image, rotated_image_rect)

# Loding required images
wall_image = scale_smoothing('./assets/img/wall.png', (tile_size, tile_size))
floor1_image = scale_smoothing('./assets/img/floor1.png', (tile_size, tile_size))
floor2_image = scale_smoothing('./assets/img/floor2.png', (tile_size, tile_size))
floor3_image = scale_smoothing('./assets/img/floor3.png', (tile_size, tile_size))
mirror_img = scale_smoothing('./assets/img/glass.png', (tile_size, tile_size))

# Class to create basic cell
class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False
        self.thickness = 4
        self.cols, self.rows = screen_width // tile_size, screen_height // tile_size

    # Method to draw pathed cell
    def draw(self):
        x, y = self.x * tile_size, self.y * tile_size

        if self.visited:
            pygame.draw.rect(screen, pygame.Color('black'), (x, y, tile_size, tile_size))


        if self.walls['top']:
            pygame.draw.line(screen, pygame.Color('darkorange'), (x, y), (x + tile_size, y), self.thickness)
        if self.walls['right']:
            pygame.draw.line(screen, pygame.Color('darkorange'), (x + tile_size, y), (x + tile_size, y + tile_size), self.thickness)
        if self.walls['bottom']:
            pygame.draw.line(screen, pygame.Color('darkorange'), (x + tile_size, y + tile_size), (x , y + tile_size), self.thickness)
        if self.walls['left']:
            pygame.draw.line(screen, pygame.Color('darkorange'), (x, y + tile_size), (x, y), self.thickness)

    # Method to get rect of cell
    def get_rects(self):
        rects = []
        x, y = self.x * tile_size, self.y * tile_size
        if self.walls['top']:
            rects.append(pygame.Rect( (x, y), (tile_size, self.thickness) ))
        if self.walls['right']:
            rects.append(pygame.Rect( (x + tile_size, y), (self.thickness, tile_size) ))
        if self.walls['bottom']:
            rects.append(pygame.Rect( (x, y + tile_size), (tile_size , self.thickness) ))
        if self.walls['left']:
            rects.append(pygame.Rect( (x, y), (self.thickness, tile_size) ))
        return rects

    # Check if cell is visited
    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * self.cols
        if x < 0 or x > self.cols - 1 or y < 0 or y > self.rows - 1:
            return False
        return self.grid_cells[find_index(x, y)]

    # Check if current cell neighbors are visited
    def check_neighbors(self, grid_cells):
        self.grid_cells = grid_cells
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False

# Function to remove required wall for path
def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
        m[current.y][current.x] = 'l'
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
        m[current.y][current.x] = 'r'

    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
        m[current.y][current.x] = 't'
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False
        m[current.y][current.x] = 'b'

# Function to generate maze
def generate_maze():
    grid_cells = [Cell(col, row) for row in range(len(m)) for col in range(len(m[0]))]
    current_cell = grid_cells[0]
    stack = []
    break_count = 1
    out_path = [(0, 0)]

    while break_count != len(grid_cells):
        current_cell.visited = True
        
        next_cell = current_cell.check_neighbors(grid_cells)
        if next_cell:
            next_cell.visited = True
            break_count += 1
            stack.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()

        try:
            if len(out_path) == 1:
                stack_last = stack[-1]
                if stack_last.x == (screen_width//tile_size)-1 and stack_last.y == 0:
                    out_path = [(i.x, i.y) for i in stack]
        except: pass

    return grid_cells, out_path

# Draw out path of light
def draw_path(out_path):
    for x, y in out_path:
        pygame.draw.rect(screen, (0, 255, 0), (x*tile_size+5, y*tile_size+5,
                tile_size-10, tile_size-10), border_radius=12) 
        
# function for correcting map
def map_correction(out_path):
    for i in range(len(out_path)-1):
        ox, oy = out_path[i]
        nx, ny = out_path[i+1]
        dx = ox - nx
        if dx == 1:
            m[ox][oy] = 'l'
        elif dx == -1:
            m[ox][oy] = 'r'

        dy = oy - ny
        if dy == 1:
            m[ox][oy] = 't'
        elif dy == -1:
            m[ox][oy] = 'b'

# Function to place random wall's and extra mirror's on map
def random_props(out_path):
    row = len(m)
    col = len(m[0])
    for r in range(row):
        for c in range(col):
            if (r, c) not in out_path:
                m[r][c] = choice(['_', 'w', '_', 'm', '_']) + '_'

# Update map with props
def update_map(out_path):
    out_path = [i[::-1] for i in out_path]

    # map correction
    map_correction(out_path)

    row = len(m)
    col = len(m[0])
    for r in range(row):
        for c in range(col):
            if (r, c) not in out_path:
                m[r][c] = choice(['_', 'w', '_', 'm', '_', '_']) + '_'

    path = m[0][0]
    for i in out_path:
        x, y = i
        path+=m[x][y]

    count = 0
    while count<=len(out_path)-1:
        if path[count] != path[count+1]:
            x, y = out_path[count]
            m[x][y] = 'm' + path[count]
        count+=1
    if out_path[1][1] != 0:
        m[0][0] = 'm' + path[count]
    if out_path[-2][0] != 0:
        m[0][-1] = 'm' + path[count]

    # placing random props
    random_props(out_path)

    return m

# Remove unwanted walls
def remove_walls_advance():
    find_index = lambda x, y: x + y * len(MAP[0])

    for y in range(len(MAP)):
        for x in range(len(MAP[0])):
            current_cell = maze[find_index(x, y)]
            if MAP[y][x][1] != 'p':
                current_cell.walls['left'] = False
                current_cell.walls['right'] = False
                current_cell.walls['top'] = False
                current_cell.walls['bottom'] = False

            if  MAP[y][x][1] == 'p':
                if y != len(m)-1 and y != 0:
                    if MAP[y+1][x][1] == '_':
                        current_cell.walls['bottom'] = True
                
                    if MAP[y-1][x][1] == '_':
                        current_cell.walls['top'] = True
                
                if x != len(MAP[0])-1 and x != 0:
                    if MAP[y][x+1][1] == '_':
                        current_cell.walls['right'] = True
               
                    if MAP[y][x-1][1] == '_':
                        current_cell.walls['left'] = True
                
# Class for creating mirror to reflect light
class Mirror(pygame.sprite.Sprite):
    def __init__(self, x, y, first=False, last=False):
        pygame.sprite.Sprite.__init__(self)
        self.x = x*tile_size
        self.y = y*tile_size
        self.first = first
        self.last = last
        self.light_collision = True if self.first==True else False
        self.line_direction = None if self.first==False else 'top'
        self.line_position = [(0, 0), (0, 0)]
        self.angle = 0
        self.image = mirror_img
        self.rect = self.image.get_rect()

        self.image, new_rect = blitRotate(self.image, (self.rect.x, self.rect.y), self.rect.center, 45)
        self.org_image = self.image
        new_rect.center = self.rect.center
        self.rect = new_rect

        self.rect.x = x*tile_size
        self.rect.y = y*tile_size

        self.mouse_clicked = False

    # Check if mirror is clicked
    def check_mirror_click(self):

        if mouse_clicked and not self.mouse_clicked:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):

                self.angle = 0 if self.angle == 90 else self.angle+90

                self.image, new_rect = blitRotate(self.org_image, (self.rect.x, self.rect.y), self.rect.center, self.angle)#rot_center(self.image,  45)
                new_rect.center = self.rect.center
                self.rect = new_rect

            self.mouse_clicked = True
        elif not mouse_clicked:
            self.mouse_clicked = False

    # Method to check obstacle on x-axis
    def angle0_x(self, x, y):
        ln = len(m[y][:x])
        for idx, val in enumerate(m[y][:x][::-1]):
            if val[0] == 'm':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), ((ln-idx-1)*tile_size + tile_size//2, y*tile_size + tile_size//2)]
                return line_point_new
            if val[0] == 'w':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), ((ln-idx-1)*tile_size + tile_size//2, y*tile_size + tile_size//2)]
                return line_point_new
        return [(0, 0), (0, 0)]
    
    def angle90_x(self, x, y):
        ln = len(m[0])-len(m[y][x+1:])
        for idx, val in enumerate(m[y][x+1:]):
            if val[0] == 'm':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), ((idx+ln)*tile_size + tile_size//2, y*tile_size + tile_size//2)]
                return line_point_new
            if val[0] == 'w':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), ((idx+ln)*tile_size + tile_size//2, y*tile_size + tile_size//2)]
                return line_point_new
        return [(0, 0), (0, 0)]

    # Method to check obstacle on y-axis
    def angle0_y(self, x, y):
        new_m = [m[i][x] for i in range(y)]
        for idx, val in enumerate(new_m[::-1]):
            if val[0] == 'm':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), (x*tile_size + tile_size//2, (y-idx-1)*tile_size + tile_size//2)]
                return line_point_new
            elif val[0] == 'w':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), (x*tile_size + tile_size//2, (y-idx-1)*tile_size + tile_size//2)]
                return line_point_new
        return [(0, 0), (0, 0)]
    
    def angle90_y(self, x, y):
        new_m = [m[i][x] for i in range(len(m))][y+1:]
        for idx, val in enumerate(new_m):
            if val[0] == 'm':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), (x*tile_size + tile_size//2, (idx+y+1)*tile_size + tile_size//2)]
                return line_point_new
            if val[0] == 'w':
                line_point_new = [(self.x + tile_size//2, self.y + tile_size//2), (x*tile_size + tile_size//2, (idx+y+1)*tile_size + tile_size//2)]
                return line_point_new
        return [(0, 0), (0, 0)]

    # Main method for finding obstacle
    def find_obstacle(self):

        if self.first:
            self.line_direction = 'top'

        x = self.x//tile_size
        y = self.y//tile_size

        # x axis
        if self.angle == 0:
            if self.line_direction == 'top':
                val = self.angle0_x(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (0, self.y+tile_size//2))
                return val
            elif self.line_direction == 'bottom':
                val = self.angle90_x(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (screen_width, self.y+tile_size//2))
                return val
        
        elif self.angle == 90:
            if self.line_direction == 'top':
                val = self.angle90_x(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (screen_width, self.y+tile_size//2))
                return val
            elif self.line_direction == 'bottom':
                val = self.angle0_x(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (0, self.y+tile_size//2))
                return val
                
        # y axis
        if self.angle == 0:
            if self.line_direction == 'left':
                val = self.angle0_y(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (self.x+tile_size//2, 0))
                return val
            elif self.line_direction == 'right':
                val = self.angle90_y(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (self.x+tile_size//2, screen_height))
                return val
        
        elif self.angle == 90:
            if self.line_direction == 'left':
                val = self.angle90_y(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (self.x+tile_size//2, screen_height))
                return val
            elif self.line_direction == 'right':
                val = self.angle0_y(x, y)
                if val == [(0, 0), (0, 0)]:
                    draw_light((self.x+tile_size//2, self.y+tile_size//2), (self.x+tile_size//2, 0))
                return val

        return [(0, 0), (0, 0)]

    # Method to check Collusion with light
    def collide_with_light(self):
        global light_collision_list
        if not self.first:
            self.light_collision = False

        # checking collusion and incident light direction
        for i in light_collision_list:
            s_point, e_point = i
            if self.rect.collidepoint(e_point[0], e_point[1]):
                self.light_collision = True
                dx = s_point[0] - e_point[0]
                if dx < 0:
                    self.line_direction = 'left'
                elif dx > 0:
                    self.line_direction ='right'

                dy = s_point[1] - e_point[1]
                if dy < 0:
                    self.line_direction ='top'
                elif dy > 0:
                    self.line_direction ='bottom'
                    
        # if light is collide reflect the light
        if self.light_collision:
            previous_position = self.line_position.copy()
            self.line_position = self.find_obstacle()
            start, end = self.line_position
            
            if previous_position != self.line_position:
                try: 
                    previous_position_idx = light_collision_list.index(previous_position)
                    light_collision_list = light_collision_list[:previous_position_idx]
                except: pass
            else:
                if self.line_position not in light_collision_list and end != (0, 0):
                    light_collision_list.append(self.line_position)

            draw_light(start, end)

    # Method to relaunch the game with random level. After current game finished
    def game_end(self):
        if self.light_collision and self.angle == 0 and self.line_direction == 'bottom':
            global m

            # Resetting required variables
            mirror_group.empty()
            m = [['0']*(screen_width//tile_size) for _ in range(screen_height//tile_size)]
            light_collision_list.clear()
            required_update()

    # Updating mirror
    def update(self):
        self.collide_with_light()
        self.check_mirror_click()
        if self.last:
            self.game_end()

# Function to draw red laser light
def draw_light(start, end):
    pygame.draw.line(screen, (255, 0, 0), start, end, 4)

# get correct maze
def correct_maze():
    global maze, out_path, MAP
    try: 
        maze, out_path = generate_maze()    
        MAP = update_map(out_path)
        for i, j in out_path: 
            MAP[j][i] = MAP[j][i][0]+'p'
            
    except:
        correct_maze()

# Adding all mirror to mirror_group
def add_mirror_group():
    # Adding first mirror
    for i in range(len(m)):
        if m[i][0][0] == 'm':
            first_mirror_pos = (0, i)
            mirror = Mirror(0, i, True)
            mirror_group.add(mirror)
            break

    # getting last mirror pos
    ml = m[0][::-1]
    for i in range(len(m[0])):
        if ml[i][0] == 'm':
            val = len(m[0])-i-1
            last_mirror_pos = (val, 0)
            break
    
    # Adding mirrors between first and last mirror
    for i in range(len(m)):
        for j in range(len(m[0])):
            if m[i][j][0] == 'm' and (j, i) != first_mirror_pos and (j, i) != last_mirror_pos:
                mirror = Mirror(j, i)
                mirror_group.add(mirror)

    # Adding last mirror
    mirror = Mirror(last_mirror_pos[0], 0, last=True)
    mirror_group.add(mirror)

# Function for update requirements
def required_update():
    correct_maze()
    remove_walls_advance()
    add_mirror_group()
required_update()

# Function to get First mirror position
def first_mirror_pos():
    for i in range(len(m)):
        if m[i][0][0] == 'm':
            return (0 + tile_size//2, i*tile_size + tile_size//2)
            
# Loading and playing background music repeatedly
bg_music = mixer.Sound('./assets/sound/bg_music.mp3')
bg_music.set_volume(0.5)
bg_music.play(-1)

# Game creation
def game():
    global mouse_clicked
    run = True
    show_path = False

    while run:
        clockobject.tick(fps) # Setting FPS

        # Drawing tiles and walls
        for i in range(len(MAP)):
            for j in range(len(MAP[0])):
                if MAP[i][j][0] == 'w':
                    x, y = j* tile_size, i* tile_size
                    screen.blit(wall_image, (x, y, tile_size, tile_size))
                elif MAP[i][j][0] == '_' or MAP[i][j][1] == 'p':
                    x, y = j* tile_size, i* tile_size
                    screen.blit(floor1_image, (x, y, tile_size, tile_size))

        # Drawing other mirrors background tile
        for i in mirror_group:
            screen.blit(floor2_image, (i.x, i.y, tile_size, tile_size))

        # Drawing first and last mirror background tile
        first_mirror = mirror_group.sprites()[0]
        screen.blit(floor3_image, (first_mirror.x, first_mirror.y, tile_size, tile_size))
        last_mirror = mirror_group.sprites()[-1]
        screen.blit(floor3_image, (last_mirror.x, last_mirror.y, tile_size, tile_size))
        
        # Show maze and out path
        if show_path:
            [cell.draw() for cell in maze]
            draw_path(out_path)
            
        # Drawing and updating mirror group
        mirror_group.draw(screen)
        mirror_group.update()

        # Drawing boarder line
        pygame.draw.rect(screen, (0, 255, 255), (0, 0, screen_width, screen_height), 3)
        pygame.draw.line(screen, (0, 0, 0), (3, 0), (tile_size-1, 0), 7)
        pygame.draw.line(screen, (0, 0, 0), (screen_width-1, 3), (screen_width-1, tile_size), 5)
       
        # Drawing starting light
        draw_light((0+tile_size//2, 0), first_mirror_pos())
        
        # Checking window event's
        for event in pygame.event.get():
            
            # Mouse button event checking
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not mouse_clicked:
                    mouse_clicked = True
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_clicked = False

            # Keyboard button event checking
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    show_path = True
                # quit window
                if event.key == pygame.K_ESCAPE:
                    run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_p:
                    show_path = False

            #quit game
            if event.type == pygame.QUIT:
                run = False

        pygame.display.update() # Updating frame

    pygame.quit() # Close pygame

# Main
if __name__ == '__main__':
    game()