import pygame_menu
import threading
import pygame
import socket
import select
import random
import time
import sys

# global variable
bind_ip = ""
bind_port = 9999
dead_time = 0.5

FPS = 60
WIDTH = 1000
HEIGHT = 600
BLACK = (0,0,0)
WHITE = (255,255,255)

# game object variables
player_speed = 5
# Can be added in future updates
ball_speedx = 5
ball_speedy = 5

# Game initialization and window creation
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ping-Pong Game")
clock = pygame.time.Clock()

class Player(pygame.sprite.Sprite):
    def __init__(self,num):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10,50))
        self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.num = num
        self.score = 0
        self.single_mode = False
        if self.num  == 1:
            self.rect.x = 50
            self.rect.y = HEIGHT / 2
            self.speed = player_speed
        elif self.num  == 2:
            self.rect.x = WIDTH - 50
            self.rect.y = HEIGHT / 2
            self.speed = player_speed
        
    def update(self):
        global s,client,is_server
        key_pressed = pygame.key.get_pressed()
        if self.num == 1 and is_server:
            if key_pressed[pygame.K_DOWN]:
                self.rect.y += self.speed
            if key_pressed[pygame.K_UP]:
                self.rect.y -= self.speed
            client.send("pos,%d,".encode() % (self.rect.y))
        elif self.num == 2 and not is_server:
            if key_pressed[pygame.K_DOWN]:
                self.rect.y += self.speed
            if key_pressed[pygame.K_UP]:
                self.rect.y -= self.speed
            s.send("pos,%d,".encode() % (self.rect.y))
        elif self.single_mode:
            if key_pressed[pygame.K_DOWN]:
                self.rect.y += self.speed
            if key_pressed[pygame.K_UP]:
                self.rect.y -= self.speed
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

class AI(pygame.sprite.Sprite):
    def __init__(self,num):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10,50))
        self.image.fill((0,255,0))
        self.rect = self.image.get_rect()
        self.score = 0
        self.num = num
        if self.num == 1:
            self.rect.x =  50
        else:
            self.rect.x = WIDTH - 50
        self.rect.y = HEIGHT/2
        self.speed = player_speed
        
    def update(self):
        global ball
        if self.num == 1:
            x = ball.rect.x
            y = ball.rect.y
            # Calculate the target position of the ball
            while x >  50 and ball.speedx < 0:
                x += ball.speedx
                y += ball.speedy
            if ball.speedx < 0:
                if y > self.rect.y and y - self.rect.y >= self.speed:
                    self.rect.y += self.speed
                elif y < self.rect.y and self.rect.y - y >= self.speed:
                    self.rect.y -= self.speed
        if self.num == 2:
            x = ball.rect.x
            y = ball.rect.y
            # Calculate the target position of the ball
            while x < WIDTH - 50 and ball.speedx > 0:
                x += ball.speedx
                y += ball.speedy
            if ball.speedx > 0:
                if y > self.rect.y and y - self.rect.y >= self.speed:
                    self.rect.y += self.speed
                elif y < self.rect.y and self.rect.y - y >= self.speed:
                    self.rect.y -= self.speed
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
        if self.rect.top < 0:
            self.rect.top = 0

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH / 2
        self.rect.y = random.randrange(HEIGHT/2 - 100, HEIGHT/2 + 100)
        self.speedx = random.choice([-4, 4])
        while(True):
            self.speedy = random.randrange(-7, 7)
            if self.speedy != 0:
                break

    def update(self):
        global is_server, client, player1
        if player1.single_mode or is_server:
            self.rect.x += self.speedx
            self.rect.y += self.speedy
        if is_server:
            client.send('ball-%d-%d-'.encode() %(self.rect.x, self.rect.y))
        if self.rect.bottom > HEIGHT or self.rect.top < 0:
            self.speedy *= -1

def draw_text(surf, text, size, x, y):
    font_name = pygame.font.match_font('arial')
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.centerx = x
    text_rect.top = y
    surf.blit(text_surface, text_rect)

def init_wait(screen, all_sprites):
    # wait 3 seconds
    for i in range(3,0,-1):
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(screen, str(i), 100, WIDTH/2, HEIGHT/5)
        pygame.display.update()
        time.sleep(1)
    screen.fill(BLACK)
    all_sprites.draw(screen)
    draw_text(screen, "GO!", 100, WIDTH/2, HEIGHT/5)
    pygame.display.update()
    time.sleep(0.3)

def ai_mode():
    global is_server, ball, player1
    is_server = False

    # Create objects
    all_sprites = pygame.sprite.Group()
    players = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    
    player1 = AI(1)
    player1.single_mode = True
    player2 = AI(2)
    all_sprites.add(player1)
    all_sprites.add(player2)
    players.add(player1)
    players.add(player2)
    
    ball = Ball()
    all_sprites.add(ball)
    balls.add(ball)

    running = True
    first_init = True
    # game loop
    while running:
        clock.tick(FPS)

        # get input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        # update the game
        all_sprites.update()
        hits = pygame.sprite.groupcollide(players, balls, False, False)
        if hits:
            ball.speedx *= -1

        # Score Check
        if ball.rect.x < 0:
            ball.kill()
            ball = Ball()
            time.sleep(dead_time)
            all_sprites.add(ball)
            balls.add(ball)
            player2.score += 1
        if ball.rect.x > WIDTH:
            ball.kill()
            ball = Ball()
            time.sleep(dead_time)
            all_sprites.add(ball)
            balls.add(ball)
            player1.score += 1

        # screen display
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(screen, str(player1.score), 18, WIDTH/2 - 10, 10)
        draw_text(screen, str(player2.score), 18, WIDTH/2 + 10, 10)
        pygame.display.update()

        # wait for start
        if first_init:
            init_wait(screen, all_sprites)
            first_init = False

def single_mode():
    global is_server,ball,player1
    is_server = False

    # Create objects
    all_sprites = pygame.sprite.Group()
    players = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    
    player1 = Player(1)
    player1.single_mode = True
    player2 = AI(2)
    all_sprites.add(player1)
    all_sprites.add(player2)
    players.add(player1)
    players.add(player2)

    ball = Ball()
    all_sprites.add(ball)
    balls.add(ball)
    
    running = True
    first_init = True
    # game loop
    while running:
        clock.tick(FPS)

        # get input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

        # update the game
        all_sprites.update()
        hits = pygame.sprite.groupcollide(players, balls, False, False)
        if hits:
            ball.speedx *= -1

        # Score Check
        if ball.rect.x < 0:
            ball.kill()
            ball = Ball()
            time.sleep(dead_time)
            all_sprites.add(ball)
            balls.add(ball)
            player2.score += 1
        if ball.rect.x > WIDTH:
            ball.kill()
            ball = Ball()
            time.sleep(dead_time)
            all_sprites.add(ball)
            balls.add(ball)
            player1.score += 1

        # screen display
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(screen, str(player1.score), 18, WIDTH/2 - 10, 10)
        draw_text(screen, str(player2.score), 18, WIDTH/2 + 10, 10)
        pygame.display.update()

        # wait for start
        if first_init:
            init_wait(screen, all_sprites)
            first_init = False

def double_mode():
    global is_double_mode, player1, player2, ball# global client, s
    is_double_mode = True
    
    # Create objects
    all_sprites = pygame.sprite.Group()
    players = pygame.sprite.Group()
    balls = pygame.sprite.Group()
    
    player1 = Player(1)
    player2 = Player(2)
    all_sprites.add(player1)
    all_sprites.add(player2)
    players.add(player1)
    players.add(player2)
    
    ball = Ball()
    all_sprites.add(ball)
    balls.add(ball)

    # create thread
    t = threading.Thread(target=job)
    t.start()
    running = True
    first_init = True
    # game loop
    while running:
        clock.tick(FPS)

        # multithreading - receiving data
        if not t.is_alive():
            t = threading.Thread(target=job)
            t.start()

        # get input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if is_server:
                        client.close()
                        return
                    else:
                        s.close()
                        return

        # update the game
        all_sprites.update()
        hits = pygame.sprite.groupcollide(players, balls, False, False)
        if hits:
            ball.speedx *= -1

        # Score check
        if is_server:
            if ball.rect.x < 0:
                ball.kill()
                ball = Ball()
                time.sleep(dead_time)
                all_sprites.add(ball)
                balls.add(ball)
                player2.score += 1
                client.send(" player2_score".encode())
            if ball.rect.x > WIDTH:
                ball.kill()
                ball = Ball()
                time.sleep(dead_time)
                all_sprites.add(ball)
                balls.add(ball)
                player1.score += 1
                client.send(" player1_score".encode())

        # screen display
        screen.fill(BLACK)
        all_sprites.draw(screen)
        draw_text(screen, str(player1.score), 18, WIDTH/2 - 10, 10)
        draw_text(screen, str(player2.score), 18, WIDTH/2 + 10, 10)
        pygame.display.update()

        # wait for start
        if first_init:
            init_wait(screen, all_sprites)
            first_init = False

def wait_server():
    global client, is_server
    is_server = True
    screen.fill(BLACK)
    draw_text(screen, 'Waiting for connection...',20, WIDTH // 2, HEIGHT // 2 - 100)
    pygame.display.update()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((bind_ip, bind_port))
    except socket.error as exc:
        print('[client] ' + str(exc))
        draw_text(screen, 'IP address is not correct.',20, WIDTH // 2, HEIGHT // 2 + 100)
        pygame.display.update()
        time.sleep(2)
        s.close()
        return
    s.listen()
    s.setblocking(False)
    inputs = [s]
    is_connected = False
    while not is_connected:
        readable, _, _ = select.select(inputs, [], [], 0.1)

        for sck in readable:
            if sck is s:
                client, addr = sck.accept()
                client.setblocking(True)
                is_connected = True

        for event in pygame.event.get():
            # when player closed the screen
            if event.type == pygame.QUIT:
                s.close()
                sys.exit()
            # when player press Esc key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                print('[server] connection canceled.')
                s.close()
                return
        pygame.display.update()
    try:
        double_mode()
    except socket.error as exc:
        # Opponent closes the game
        print('[client] ' + str(exc))
        draw_text(screen, "connection failed.", 20, WIDTH/2, HEIGHT/2 + 100)
        pygame.display.update()
        time.sleep(2)
        client.close()
        return

def wait_client():
    global s, is_server
    is_server = False
    screen.fill(BLACK)
    draw_text(screen, 'Waiting for connection...',20, WIDTH // 2, HEIGHT // 2 - 100)
    pygame.display.update()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5)
    try:
        s.connect((bind_ip, bind_port))
        double_mode()
    except socket.error as exc:
        print('[server] ' + str(exc))
        draw_text(screen, 'connection failed.', 20,WIDTH // 2, HEIGHT // 2 + 100)
        pygame.display.update()
        time.sleep(2)
        s.close()
        return

def job():
    global s, client, is_server, player1, player2, ball
    if is_server:
        data = client.recv(1024)
        if data.decode().find('pos') != (-1):
            player2.rect.y = int(data.decode().split(',')[1])
        print("Client recv data : %s " % (data.decode()))
    else:
        data = s.recv(1024)
        if data.decode().find('pos') != (-1):
            player1.rect.y = int(data.decode().split(',')[1])
        if data.decode().find('player1_score') != (-1):
            player1.score += 1
        if data.decode().find('player2_score') != (-1):
            player2.score += 1
        if data.decode().find('ball') != (-1):
            try:
                ball.rect.x = int(data.decode().split('-')[1])
                ball.rect.y = int(data.decode().split('-')[2])
            except:
                pass
        print("Server recv data : %s " % (data.decode()))

def change_IP(value):
    global bind_ip
    bind_ip = value

def menu():
    # Create menu
    main_menu = pygame_menu.Menu('Main Menu', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_BLUE)
    help_menu = pygame_menu.Menu('Help', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_BLUE)
    double_menu = pygame_menu.Menu('Double Player Mode', WIDTH, HEIGHT, theme=pygame_menu.themes.THEME_BLUE)
    
    # Create main_menu object
    main_menu.add.button('AI Mode', ai_mode)
    main_menu.add.button('Single Player Mode', single_mode)
    main_menu.add.button(double_menu.get_title(), double_menu)
    main_menu.add.button(help_menu.get_title(), help_menu)
    main_menu.add.button('Quit', pygame_menu.events.EXIT)
    main_menu.enable()

    # Create double_menu object
    double_menu.add.text_input('IP address: ', default=bind_ip,maxchar=16, input_underline='_', onchange=change_IP)
    double_menu.add.button('Start a New Game', wait_server)
    double_menu.add.button('Join a Game', wait_client)
    double_menu.add.button('Return to Menu', pygame_menu.events.BACK)
    
    # Create help_menu object
    help_menu.add.label('1. There are 3 modes(AI vs AI, Player vs Ai, Player vs Player).', max_char=-1, font_size=30)
    help_menu.add.label('2. Use the up and down arrow keys to move.', max_char=-1, font_size=30)
    help_menu.add.label('3. Players can press Esc to leave the game.', max_char=-1, font_size=30)
    help_menu.add.label('4. In single player mode, the player is on the left and the AI is on the right.', max_char=-1, font_size=30)
    help_menu.add.label('5. In the double player mode, the server side is on the left and the client side is on the right side. Both parties must enter the IP of the server side.', max_char=-1, font_size=30)
    help_menu.add.button('Return to Menu', pygame_menu.events.BACK)

    while True:
        events = pygame.event.get()
        main_menu.update(events)
        main_menu.draw(screen)
        pygame.display.update()

menu()
