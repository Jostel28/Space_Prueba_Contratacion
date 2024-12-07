import pygame
import random

# Inicialización
pygame.font.init()
pygame.mixer.init()  # Inicialización del mezclador de sonido

# Dimensiones de la pantalla
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Defender")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Recursos
spaceship_img = pygame.image.load("Assets/nave.png")
enemy_img = pygame.image.load("Assets/enemigo.png")

# Cargar sonidos
disparo_sound = pygame.mixer.Sound("Assets/disparos.wav")
explosion_sound = pygame.mixer.Sound("Assets/explosion.wav")

# Clase para la nave del jugador
class Player:
    def __init__(self, x, y):
        self.image = pygame.transform.scale(spaceship_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.speed = 5
        self.bullets = []

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

    def shoot(self):
        bullet = Bullet(self.rect.centerx, self.rect.top)
        self.bullets.append(bullet)
        disparo_sound.play()  # Reproducir sonido de disparo

    def draw(self):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw()

# Clase para los disparos del jugador
class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 5, y, 10, 20)
        self.speed = -7

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)

# Clase para los disparos de los enemigos
class EnemyBullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 5, y, 10, 20)
        self.speed = 5

    def update(self):
        self.rect.y += self.speed

    def draw(self):
        pygame.draw.rect(screen, WHITE, self.rect)

# Clase para los enemigos
class Enemy:
    def __init__(self):
        self.image = pygame.transform.scale(enemy_img, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - 50)
        self.rect.y = random.randint(-150, -50)
        self.speed = random.randint(2, 4)
        self.bullets = []
        self.shoot_delay = random.randint(30, 120)  # Intervalo de disparo

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.rect.y = random.randint(-150, -50)
            self.rect.x = random.randint(0, WIDTH - 50)

        # Disparar periódicamente
        self.shoot_delay -= 1
        if self.shoot_delay <= 0:
            self.shoot()
            self.shoot_delay = random.randint(30, 120)

    def shoot(self):
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        self.bullets.append(bullet)

    def draw(self):
        screen.blit(self.image, self.rect)
        for bullet in self.bullets:
            bullet.draw()

# Mostrar texto en pantalla
def draw_text(text, font_size, x, y, color=WHITE):
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Función principal del juego
def main():
    clock = pygame.time.Clock()
    running = True
    game_state = "menu"  # Estados: "menu", "playing", "paused", "gameover"
    score = 0

    # Crear jugador y enemigos
    player = Player(WIDTH // 2, HEIGHT - 60)
    enemies = [Enemy() for _ in range(5)]

    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_state == "menu" and event.key == pygame.K_RETURN:
                    game_state = "playing"
                elif game_state == "playing" and event.key == pygame.K_p:
                    game_state = "paused"
                elif game_state == "paused" and event.key == pygame.K_r:
                    game_state = "playing"
                elif game_state == "playing" and event.key == pygame.K_SPACE:
                    player.shoot()

        if game_state == "menu":
            draw_text("SPACE DEFENDER", 64, WIDTH // 2 - 200, HEIGHT // 2 - 100)
            draw_text("Presiona ENTER para iniciar", 32, WIDTH // 2 - 150, HEIGHT // 2)

        elif game_state == "playing":
            # Controles del jugador
            keys = pygame.key.get_pressed()
            player.move(keys)

            # Actualizar disparos del jugador
            for bullet in player.bullets:
                bullet.update()
                if bullet.rect.bottom < 0:
                    player.bullets.remove(bullet)

            # Actualizar enemigos y sus disparos
            for enemy in enemies:
                enemy.update()
                for bullet in enemy.bullets:
                    bullet.update()
                    if bullet.rect.top > HEIGHT:
                        enemy.bullets.remove(bullet)
                    if bullet.rect.colliderect(player.rect):
                        game_state = "gameover"

                if player.rect.colliderect(enemy.rect):
                    game_state = "gameover"

                for bullet in player.bullets:
                    if bullet.rect.colliderect(enemy.rect):
                        score += 1
                        player.bullets.remove(bullet)
                        enemies.remove(enemy)
                        enemies.append(Enemy())
                        explosion_sound.play()  # Reproducir sonido de explosión
                        break

            # Dibujar objetos
            player.draw()
            for enemy in enemies:
                enemy.draw()

            # Actualizar puntaje
            draw_text(f"Puntaje: {score}", 36, 10, 10)

        elif game_state == "paused":
            draw_text("PAUSA", 64, WIDTH // 2 - 100, HEIGHT // 2 - 100)
            draw_text("Presiona R para reanudar", 32, WIDTH // 2 - 150, HEIGHT // 2)

        elif game_state == "gameover":
            draw_text("GAME OVER", 64, WIDTH // 2 - 150, HEIGHT // 2 - 100)
            draw_text(f"Puntaje final: {score}", 32, WIDTH // 2 - 100, HEIGHT // 2)
            draw_text("Presiona ENTER para reiniciar", 32, WIDTH // 2 - 200, HEIGHT // 2 + 100)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    main()
                    return  # Salir del estado actual y reiniciar el juego
            
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()