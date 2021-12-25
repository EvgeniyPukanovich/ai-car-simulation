import math
import pygame

class Car:    
    def __init__(self, sprite, size_x, size_y):
        self.sprite = sprite
        self.size_x = size_x
        self.size_y = size_y
        # гафика, через консируктор
        #self.sprite = pygame.image.load('car.png').convert() # Convert Speeds Up A Lot
        #self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite 

        # надо бы что то сделать, но пока хардкод
        self.position = [830, 920] # Starting Position
        self.angle = 0
        self.speed = 0

        self.speed_set = False # Flag For Default Speed Later on

        self.center = [self.position[0] + self.size_x / 2, self.position[1] + self.size_y / 2] # центр машины

        self.radars = [] # список радаров
        self.drawing_radars = [] # Radars To Be Drawn

        self.alive = True # столкнулась или нет

        self.distance = 0 # пройденная дистанция
        self.time = 0 # время жизни (в тиках)

    #ГРАФИКА
    # def draw(self, screen):
    #     screen.blit(self.rotated_sprite, self.position) # Draw Sprite
    #     self.draw_radar(screen) #OPTIONAL FOR SENSORS

    # def draw_radar(self, screen):
    #     # Optionally Draw All Sensors / Radars
    #     for radar in self.radars:
    #         position = radar[0]
    #         pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
    #         pygame.draw.circle(screen, (0, 255, 0), position, 5)

    def check_collision(self, game_map, border_color):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == border_color:
                self.alive = False
                break

    def check_radar(self, degree, game_map, border_color, radar_length = 300):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # столкнется ли конец луча радара с границей при длине луча length
        while not game_map.get_at((x, y)) == border_color and length < radar_length:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # высчитываем расстояние до границы
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])
    
    def update(self, game_map, map_width, map_height):
        # устанавливаем начальную скорость
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # поворачиваем спрайт и изменяем x координату
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        #чтобы не выйти за границу, если трасса нарисована прямо к краю
        self.position[0] = max(self.position[0], 1)
        self.position[0] = min(self.position[0], map_width - 1)
        
        # изменяем y координату
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 1)
        self.position[1] = min(self.position[1], map_height - 2)

        # увеличиваем пройденную дистанцию и время
        self.distance += self.speed
        self.time += 1

        # новый центр машины
        self.center = [int(self.position[0]) + self.size_x / 2, int(self.position[1]) + self.size_y / 2]

        # координаты углов машины
        length = 0.5 * self.size_x
        left_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length]
        right_top = [self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length]
        left_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length]
        right_bottom = [self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length, self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length]
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        self.check_collision(game_map)
        
        self.radars.clear()
        # -90 -45 0 45 90
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    def get_data(self):
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            # расстояние до границы, которое высчитал радар/30
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        return self.alive

    def get_reward(self):
        return self.distance / (self.size_x / 2)

    def rotate_center(self, image, angle):
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image