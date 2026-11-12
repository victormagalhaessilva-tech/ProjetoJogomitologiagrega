import pygame
import random
import math
import array

# Inicialização do Pygame e Mixer de Som
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Configurações da Tela (Estilo Retrô)
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Odisseia Olímpica - Desafio CCM Elias Abrahão")
FPS = 60

# Paleta de Cores Retrô
PRETO = (15, 15, 25)
BRANCO = (255, 255, 255)
DOURADO = (255, 215, 0)
AZUL_CEU = (30, 60, 140)
VERMELHO_HADES = (180, 20, 40)
VERDE_MEDUSA = (50, 200, 80)
CIANO_RAIO = (0, 255, 255)
CINZA_PEDRA = (120, 120, 130)

# Fontes
fonte_titulo = pygame.font.SysFont("Courier", 42, bold=True)
fonte_hud = pygame.font.SysFont("Courier", 22, bold=True)
fonte_pequena = pygame.font.SysFont("Courier", 16, bold=True)

# --- GERADOR DE EFEITOS SONOROS 8-BIT (Sem arquivos externos) ---
def criar_som_8bit(frequencia, duracao_ms, tipo="quadrada"):
    sample_rate = 44100
    n_samples = int(sample_rate * (duracao_ms / 1000.0))
    buf = array.array('h', [0] * n_samples)
    amplitude = 4000
    for i in range(n_samples):
        t = i / sample_rate
        if tipo == "quadrada":
            val = amplitude if math.sin(2 * math.pi * frequencia * t) > 0 else -amplitude
        elif tipo == "queda":
            freq_atual = frequencia * (1 - (i / n_samples) * 0.7)
            val = amplitude if math.sin(2 * math.pi * freq_atual * t) > 0 else -amplitude
        buf[i] = int(val)
    return pygame.mixer.Sound(buffer=buf)

SOM_TIRO = criar_som_8bit(880, 100, "queda")
SOM_EXPLOSAO = criar_som_8bit(150, 250, "queda")
SOM_DANO = criar_som_8bit(110, 300, "quadrada")
SOM_VITORIA = criar_som_8bit(660, 400, "quadrada")

# --- DESENHOS EM PIXEL ART VIA MATRIZ ---
def desenhar_pixel_art(superficie, matriz, x, y, tamanho_pixel, paleta):
    for linha_idx, linha in enumerate(matriz):
        for col_idx, char in enumerate(linha):
            if char in paleta:
                pygame.draw.rect(
                    superficie,
                    paleta[char],
                    (x + col_idx * tamanho_pixel, y + linha_idx * tamanho_pixel, tamanho_pixel, tamanho_pixel)
                )

# Sprites Pixel Art (10x10)
SPRITE_HEROI = [
    "   DDDD   ",
    "  DDDDDD  ",
    "  PPPPPP  ",
    "  PBPBPP  ",
    "  PPPPPP  ",
    " BBBBBBBB ",
    "B BBBBBB B",
    "  BBBBBB  ",
    "  PP  PP  ",
    " DD    DD "
]
PALETA_HEROI = {"D": DOURADO, "P": (240, 190, 150), "B": BRANCO}

SPRITE_MEDUSA = [
    "  VVVVVV  ",
    " V VVVV V ",
    "VVVVVVVVVV",
    " VPPPPPPV ",
    " VRPPRPPV ",
    "  PPPPPP  ",
    "  VVVVVV  ",
    " V VVVV V ",
    "   VVVV   ",
    "  V    V  "
]
PALETA_MEDUSA = {"V": VERDE_MEDUSA, "P": (180, 230, 180), "R": VERMELHO_HADES}

SPRITE_HADES = [
    " C      C ",
    " CC    CC ",
    "CCCCCCCCCC",
    "CCHHHHHHCC",
    "CHVHHHHVHC",
    "CHHHHHHHHC",
    "HHHHHHHHHH",
    "HHHHHHHHHH",
    " HHHHHHHH ",
    "  HH  HH  "
]
PALETA_HADES = {"C": CIANO_RAIO, "H": (40, 40, 60), "V": VERMELHO_HADES}

# --- CLASSES DO JOGO ---
class Jogador:
    def __init__(self):
        self.largura = 40
        self.altura = 40
        self.x = 60
        self.y = ALTURA // 2
        self.velocidade = 6
        self.vidas = 3
        self.pontos = 0
        self.cooldown_tiro = 0

    def mover(self, teclas):
        if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and self.y > 50:
            self.y -= self.velocidade
        if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and self.y < ALTURA - self.altura - 10:
            self.y += self.velocidade
        if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and self.x > 10:
            self.x -= self.velocidade
        if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and self.x < LARGURA // 2:
            self.x += self.velocidade

        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1

    def desenhar(self):
        desenhar_pixel_art(TELA, SPRITE_HEROI, self.x, self.y, 4, PALETA_HEROI)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


class Raio:
    def __init__(self, x, y, velocidade=10, cor=CIANO_RAIO):
        self.x = x
        self.y = y
        self.velocidade = velocidade
        self.cor = cor
        self.rect = pygame.Rect(x, y, 20, 6)

    def atualizar(self):
        self.x += self.velocidade
        self.rect.x = self.x

    def desenhar(self):
        pygame.draw.rect(TELA, self.cor, self.rect)
        pygame.draw.rect(TELA, BRANCO, (self.x + 4, self.y + 2, 12, 2))


class Inimigo:
    def __init__(self, fase):
        self.largura = 40
        self.altura = 40
        self.x = LARGURA + random.randint(10, 100)
        self.y = random.randint(60, ALTURA - 60)
        self.velocidade = random.randint(3, 5) + fase
        self.tipo = "medusa" if fase == 1 else "ciclope"

    def atualizar(self):
        self.x -= self.velocidade

    def desenhar(self):
        if self.tipo == "medusa":
            desenhar_pixel_art(TELA, SPRITE_MEDUSA, self.x, self.y, 4, PALETA_MEDUSA)
        else:
            # Ciclope desenhado em formas geométricas retrô
            pygame.draw.rect(TELA, CINZA_PEDRA, (self.x, self.y, 40, 40))
            pygame.draw.rect(TELA, BRANCO, (self.x + 8, self.y + 10, 14, 14))
            pygame.draw.rect(TELA, VERMELHO_HADES, (self.x + 10, self.y + 14, 6, 6))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


class ChefaoHades:
    def __init__(self):
        self.largura = 100
        self.altura = 100
        self.x = LARGURA - 150
        self.y = ALTURA // 2 - 50
        self.vida_max = 30
        self.vida = self.vida_max
        self.direcao_y = 3
        self.timer_ataque = 0

    def atualizar(self):
        self.y += self.direcao_y
        if self.y <= 60 or self.y >= ALTURA - self.altura - 10:
            self.direcao_y *= -1
        self.timer_ataque += 1

    def desenhar(self):
        desenhar_pixel_art(TELA, SPRITE_HADES, self.x, self.y, 10, PALETA_HADES)
        # Barra de Vida do Chefão
        pygame.draw.rect(TELA, PRETO, (LARGURA // 2 - 152, 13, 304, 24))
        largura_vida = int((self.vida / self.vida_max) * 300)
        pygame.draw.rect(TELA, VERMELHO_HADES, (LARGURA // 2 - 150, 15, largura_vida, 20))
        txt_boss = fonte_pequena.render("HADES - SENHOR DO SUBMUNDO", True, BRANCO)
        TELA.blit(txt_boss, (LARGURA // 2 - txt_boss.get_width() // 2, 17))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# --- FUNÇÃO PRINCIPAL DO JOGO ---
def jogar():
    clock = pygame.time.Clock()
    estado = "MENU"  # MENU, JOGANDO, GAME_OVER, VITORIA
    jogador = Jogador()
    raios_jogador = []
    raios_inimigos = []
    inimigos = []
    chefao = None
    fase = 1
    timer_spawn = 0

    # Estrelas/Colunas de fundo para efeito parallax
    estrelas = [[random.randint(0, LARGURA), random.randint(50, ALTURA)] for _ in range(40)]

    rodando = True
    while rodando:import pygame
import random
import math
import array

# Inicialização do Pygame e Mixer de Som
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Configurações da Tela (Estilo Retrô)
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Odisseia Olímpica - Desafio CCM Elias Abrahão")
FPS = 60

# Paleta de Cores Retrô
PRETO = (15, 15, 25)
BRANCO = (255, 255, 255)
DOURADO = (255, 215, 0)
AZUL_CEU = (30, 60, 140)
VERMELHO_HADES = (180, 20, 40)
VERDE_MEDUSA = (50, 200, 80)
CIANO_RAIO = (0, 255, 255)
CINZA_PEDRA = (120, 120, 130)

# Fontes
fonte_titulo = pygame.font.SysFont("Courier", 42, bold=True)
fonte_hud = pygame.font.SysFont("Courier", 22, bold=True)
fonte_pequena = pygame.font.SysFont("Courier", 16, bold=True)

# --- GERADOR DE EFEITOS SONOROS 8-BIT (Sem arquivos externos) ---
def criar_som_8bit(frequencia, duracao_ms, tipo="quadrada"):
    sample_rate = 44100
    n_samples = int(sample_rate * (duracao_ms / 1000.0))
    buf = array.array('h', [0] * n_samples)
    amplitude = 4000
    for i in range(n_samples):
        t = i / sample_rate
        if tipo == "quadrada":
            val = amplitude if math.sin(2 * math.pi * frequencia * t) > 0 else -amplitude
        elif tipo == "queda":
            freq_atual = frequencia * (1 - (i / n_samples) * 0.7)
            val = amplitude if math.sin(2 * math.pi * freq_atual * t) > 0 else -amplitude
        buf[i] = int(val)
    return pygame.mixer.Sound(buffer=buf)

SOM_TIRO = criar_som_8bit(880, 100, "queda")
SOM_EXPLOSAO = criar_som_8bit(150, 250, "queda")
SOM_DANO = criar_som_8bit(110, 300, "quadrada")
SOM_VITORIA = criar_som_8bit(660, 400, "quadrada")

# --- DESENHOS EM PIXEL ART VIA MATRIZ ---
def desenhar_pixel_art(superficie, matriz, x, y, tamanho_pixel, paleta):
    for linha_idx, linha in enumerate(matriz):
        for col_idx, char in enumerate(linha):
            if char in paleta:
                pygame.draw.rect(
                    superficie,
                    paleta[char],
                    (x + col_idx * tamanho_pixel, y + linha_idx * tamanho_pixel, tamanho_pixel, tamanho_pixel)
                )

# Sprites Pixel Art (10x10)
SPRITE_HEROI = [
    "   DDDD   ",
    "  DDDDDD  ",
    "  PPPPPP  ",
    "  PBPBPP  ",
    "  PPPPPP  ",
    " BBBBBBBB ",
    "B BBBBBB B",
    "  BBBBBB  ",
    "  PP  PP  ",
    " DD    DD "
]
PALETA_HEROI = {"D": DOURADO, "P": (240, 190, 150), "B": BRANCO}

SPRITE_MEDUSA = [
    "  VVVVVV  ",
    " V VVVV V ",
    "VVVVVVVVVV",
    " VPPPPPPV ",
    " VRPPRPPV ",
    "  PPPPPP  ",
    "  VVVVVV  ",
    " V VVVV V ",
    "   VVVV   ",
    "  V    V  "
]
PALETA_MEDUSA = {"V": VERDE_MEDUSA, "P": (180, 230, 180), "R": VERMELHO_HADES}

SPRITE_HADES = [
    " C      C ",
    " CC    CC ",
    "CCCCCCCCCC",
    "CCHHHHHHCC",
    "CHVHHHHVHC",
    "CHHHHHHHHC",
    "HHHHHHHHHH",
    "HHHHHHHHHH",
    " HHHHHHHH ",
    "  HH  HH  "
]
PALETA_HADES = {"C": CIANO_RAIO, "H": (40, 40, 60), "V": VERMELHO_HADES}

# --- CLASSES DO JOGO ---
class Jogador:
    def __init__(self):
        self.largura = 40
        self.altura = 40
        self.x = 60
        self.y = ALTURA // 2
        self.velocidade = 6
        self.vidas = 3
        self.pontos = 0
        self.cooldown_tiro = 0

    def mover(self, teclas):
        if (teclas[pygame.K_UP] or teclas[pygame.K_w]) and self.y > 50:
            self.y -= self.velocidade
        if (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) and self.y < ALTURA - self.altura - 10:
            self.y += self.velocidade
        if (teclas[pygame.K_LEFT] or teclas[pygame.K_a]) and self.x > 10:
            self.x -= self.velocidade
        if (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) and self.x < LARGURA // 2:
            self.x += self.velocidade

        if self.cooldown_tiro > 0:
            self.cooldown_tiro -= 1

    def desenhar(self):
        desenhar_pixel_art(TELA, SPRITE_HEROI, self.x, self.y, 4, PALETA_HEROI)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


class Raio:
    def __init__(self, x, y, velocidade=10, cor=CIANO_RAIO):
        self.x = x
        self.y = y
        self.velocidade = velocidade
        self.cor = cor
        self.rect = pygame.Rect(x, y, 20, 6)

    def atualizar(self):
        self.x += self.velocidade
        self.rect.x = self.x

    def desenhar(self):
        pygame.draw.rect(TELA, self.cor, self.rect)
        pygame.draw.rect(TELA, BRANCO, (self.x + 4, self.y + 2, 12, 2))


class Inimigo:
    def __init__(self, fase):
        self.largura = 40
        self.altura = 40
        self.x = LARGURA + random.randint(10, 100)
        self.y = random.randint(60, ALTURA - 60)
        self.velocidade = random.randint(3, 5) + fase
        self.tipo = "medusa" if fase == 1 else "ciclope"

    def atualizar(self):
        self.x -= self.velocidade

    def desenhar(self):
        if self.tipo == "medusa":
            desenhar_pixel_art(TELA, SPRITE_MEDUSA, self.x, self.y, 4, PALETA_MEDUSA)
        else:
            # Ciclope desenhado em formas geométricas retrô
            pygame.draw.rect(TELA, CINZA_PEDRA, (self.x, self.y, 40, 40))
            pygame.draw.rect(TELA, BRANCO, (self.x + 8, self.y + 10, 14, 14))
            pygame.draw.rect(TELA, VERMELHO_HADES, (self.x + 10, self.y + 14, 6, 6))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


class ChefaoHades:
    def __init__(self):
        self.largura = 100
        self.altura = 100
        self.x = LARGURA - 150
        self.y = ALTURA // 2 - 50
        self.vida_max = 30
        self.vida = self.vida_max
        self.direcao_y = 3
        self.timer_ataque = 0

    def atualizar(self):
        self.y += self.direcao_y
        if self.y <= 60 or self.y >= ALTURA - self.altura - 10:
            self.direcao_y *= -1
        self.timer_ataque += 1

    def desenhar(self):
        desenhar_pixel_art(TELA, SPRITE_HADES, self.x, self.y, 10, PALETA_HADES)
        # Barra de Vida do Chefão
        pygame.draw.rect(TELA, PRETO, (LARGURA // 2 - 152, 13, 304, 24))
        largura_vida = int((self.vida / self.vida_max) * 300)
        pygame.draw.rect(TELA, VERMELHO_HADES, (LARGURA // 2 - 150, 15, largura_vida, 20))
        txt_boss = fonte_pequena.render("HADES - SENHOR DO SUBMUNDO", True, BRANCO)
        TELA.blit(txt_boss, (LARGURA // 2 - txt_boss.get_width() // 2, 17))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.largura, self.altura)


# --- FUNÇÃO PRINCIPAL DO JOGO ---
def jogar():
    clock = pygame.time.Clock()
    estado = "MENU"  # MENU, JOGANDO, GAME_OVER, VITORIA
    jogador = Jogador()
    raios_jogador = []
    raios_inimigos = []
    inimigos = []
    chefao = None
    fase = 1
    timer_spawn = 0

    # Estrelas/Colunas de fundo para efeito parallax
    estrelas = [[random.randint(0, LARGURA), random.randint(50, ALTURA)] for _ in range(40)]

    rodando = True
    while rodando:
        clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if estado == "MENU" and evento.key == pygame.K_RETURN:
                    estado = "JOGANDO"
                elif estado in ["GAME_OVER", "VITORIA"] and evento.key == pygame.K_r:
                    jogar()
                    return

        # --- TELA DE MENU ---
        if estado == "MENU":
            TELA.fill(AZUL_CEU)
            titulo = fonte_titulo.render("ODISSEIA OLIMPICA", True, DOURADO)
            sub = fonte_hud.render("Mitologia Grega - Estilo Retro", True, BRANCO)
            inst1 = fonte_pequena.render("Setas ou WASD: Voar | ESPACO: Lancar Raio de Zeus", True, CIANO_RAIO)
            inst2 = fonte_hud.render("Pressione ENTER para Iniciar", True, BRANCO)

            TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 150))
            TELA.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 210))
            TELA.blit(inst1, (LARGURA // 2 - inst1.get_width() // 2, 320))
            TELA.blit(inst2, (LARGURA // 2 - inst2.get_width() // 2, 420))
            pygame.display.flip()
            continue

        # --- TELA DE GAME OVER OU VITÓRIA ---
        if estado in ["GAME_OVER", "VITORIA"]:
            TELA.fill(PRETO)
            msg = "VOCE VENCEU O OLIMPO!" if estado == "VITORIA" else "DERROTADO NO SUBMUNDO"
            cor_msg = DOURADO if estado == "VITORIA" else VERMELHO_HADES
            txt1 = fonte_titulo.render(msg, True, cor_msg)
            txt2 = fonte_hud.render(f"Pontuacao Final: {jogador.pontos}", True, BRANCO)
            txt3 = fonte_pequena.render("Pressione R para jogar novamente", True, CIANO_RAIO)

            TELA.blit(txt1, (LARGURA // 2 - txt1.get_width() // 2, 200))
            TELA.blit(txt2, (LARGURA // 2 - txt2.get_width() // 2, 280))
            TELA.blit(txt3, (LARGURA // 2 - txt3.get_width() // 2, 360))
            pygame.display.flip()
            continue

        # --- LÓGICA DO JOGO ---
        teclas = pygame.key.get_pressed()
        jogador.mover(teclas)

        # Atirar Raios
        if teclas[pygame.K_SPACE] and jogador.cooldown_tiro == 0:
            raios_jogador.append(Raio(jogador.x + 35, jogador.y + 18))
            jogador.cooldown_tiro = 15
            SOM_TIRO.play()

        # Progressão de Fases
        if jogador.pontos >= 100 and fase == 1:
            fase = 2
            inimigos.clear()
        elif jogador.pontos >= 250 and fase == 2:
            fase = 3  # Fase do Chefão
            inimigos.clear()
            chefao = ChefaoHades()

        # Spawn de Inimigos (Fases 1 e 2)
        if fase in [1, 2]:
            timer_spawn += 1
            if timer_spawn >= 45:
                inimigos.append(Inimigo(fase))
                timer_spawn = 0

        # Atualizar Raios do Jogador
        for raio in raios_jogador[:]:
            raio.atualizar()
            if raio.x > LARGURA:
                raios_jogador.remove(raio)

        # Atualizar Inimigos Comuns
        for inimigo in inimigos[:]:
            inimigo.atualizar()
            if inimigo.x < -50:
                inimigos.remove(inimigo)
                continue

            # Colisão Raio -> Inimigo
            for raio in raios_jogador[:]:
                if inimigo.get_rect().colliderect(raio.rect):
                    SOM_EXPLOSAO.play()
                    jogador.pontos += 15
                    if inimigo in inimigos:
                        inimigos.remove(inimigo)
                    if raio in raios_jogador:
                        raios_jogador.remove(raio)
                    break

            # Colisão Inimigo -> Jogador
            if inimigo.get_rect().colliderect(jogador.get_rect()):
                SOM_DANO.play()
                jogador.vidas -= 1
                inimigos.remove(inimigo)
                if jogador.vidas <= 0:
                    estado = "GAME_OVER"

        # Lógica do Chefão Hades (Fase 3)
        if fase == 3 and chefao:
            chefao.atualizar()
            # Ataque de fogo do Hades
            if chefao.timer_ataque % 50 == 0:
                raios_inimigos.append(Raio(chefao.x, chefao.y + 45, velocidade=-7, cor=VERMELHO_HADES))

            # Colisão Raio do Jogador -> Hades
            for raio in raios_jogador[:]:
                if chefao.get_rect().colliderect(raio.rect):
                    SOM_EXPLOSAO.play()
                    chefao.vida -= 1
                    jogador.pontos += 10
                    raios_jogador.remove(raio)
                    if chefao.vida <= 0:
                        SOM_VITORIA.play()
                        estado = "VITORIA"

        # Atualizar Raios do Chefão
        for r_inimigo in raios_inimigos[:]:
            r_inimigo.atualizar()
            if r_inimigo.x < 0:
                raios_inimigos.remove(r_inimigo)
            elif r_inimigo.rect.colliderect(jogador.get_rect()):
                SOM_DANO.play()
                jogador.vidas -= 1
                raios_inimigos.remove(r_inimigo)
                if jogador.vidas <= 0:
                    estado = "GAME_OVER"

        # --- RENDERIZAÇÃO DA TELA ---
        cor_fundo = AZUL_CEU if fase == 1 else ((60, 40, 80) if fase == 2 else (40, 10, 15))
        TELA.fill(cor_fundo)

        # Fundo animado
        for estrela in estrelas:
            estrela[0] -= 2
            if estrela[0] < 0:
                estrela[0] = LARGURA
            pygame.draw.rect(TELA, BRANCO, (estrela[0], estrela[1], 3, 3))

        jogador.desenhar()
        for raio in raios_jogador:
            raio.desenhar()
        for r_inimigo in raios_inimigos:
            r_inimigo.desenhar()
        for inimigo in inimigos:
            inimigo.desenhar()
        if chefao:
            chefao.desenhar()

        # Barra Superior (HUD)
        pygame.draw.rect(TELA, PRETO, (0, 0, LARGURA, 45))
        txt_vidas = fonte_hud.render(f"VIDAS: {'♥ ' * jogador.vidas}", True, VERMELHO_HADES)
        txt_pontos = fonte_hud.render(f"PONTOS: {jogador.pontos}", True, DOURADO)
        nome_fase = "FASE 1: MEDUSAS" if fase == 1 else ("FASE 2: CICLOPES" if fase == 2 else "FASE FINAL: HADES")
        txt_fase = fonte_pequena.render(nome_fase, True, BRANCO)

        TELA.blit(txt_vidas, (15, 10))
        TELA.blit(txt_pontos, (LARGURA - 200, 10))
        if fase != 3:
            TELA.blit(txt_fase, (LARGURA // 2 - txt_fase.get_width() // 2, 14))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    jogar()
        clock.tick(FPS)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False

            if evento.type == pygame.KEYDOWN:
                if estado == "MENU" and evento.key == pygame.K_RETURN:
                    estado = "JOGANDO"
                elif estado in ["GAME_OVER", "VITORIA"] and evento.key == pygame.K_r:
                    jogar()
                    return

        # --- TELA DE MENU ---
        if estado == "MENU":
            TELA.fill(AZUL_CEU)
            titulo = fonte_titulo.render("ODISSEIA OLIMPICA", True, DOURADO)
            sub = fonte_hud.render("Mitologia Grega - Estilo Retro", True, BRANCO)
            inst1 = fonte_pequena.render("Setas ou WASD: Voar | ESPACO: Lancar Raio de Zeus", True, CIANO_RAIO)
            inst2 = fonte_hud.render("Pressione ENTER para Iniciar", True, BRANCO)

            TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 150))
            TELA.blit(sub, (LARGURA // 2 - sub.get_width() // 2, 210))
            TELA.blit(inst1, (LARGURA // 2 - inst1.get_width() // 2, 320))
            TELA.blit(inst2, (LARGURA // 2 - inst2.get_width() // 2, 420))
            pygame.display.flip()
            continue

        # --- TELA DE GAME OVER OU VITÓRIA ---
        if estado in ["GAME_OVER", "VITORIA"]:
            TELA.fill(PRETO)
            msg = "VOCE VENCEU O OLIMPO!" if estado == "VITORIA" else "DERROTADO NO SUBMUNDO"
            cor_msg = DOURADO if estado == "VITORIA" else VERMELHO_HADES
            txt1 = fonte_titulo.render(msg, True, cor_msg)
            txt2 = fonte_hud.render(f"Pontuacao Final: {jogador.pontos}", True, BRANCO)
            txt3 = fonte_pequena.render("Pressione R para jogar novamente", True, CIANO_RAIO)

            TELA.blit(txt1, (LARGURA // 2 - txt1.get_width() // 2, 200))
            TELA.blit(txt2, (LARGURA // 2 - txt2.get_width() // 2, 280))
            TELA.blit(txt3, (LARGURA // 2 - txt3.get_width() // 2, 360))
            pygame.display.flip()
            continue

        # --- LÓGICA DO JOGO ---
        teclas = pygame.key.get_pressed()
        jogador.mover(teclas)

        # Atirar Raios
        if teclas[pygame.K_SPACE] and jogador.cooldown_tiro == 0:
            raios_jogador.append(Raio(jogador.x + 35, jogador.y + 18))
            jogador.cooldown_tiro = 15
            SOM_TIRO.play()

        # Progressão de Fases
        if jogador.pontos >= 100 and fase == 1:
            fase = 2
            inimigos.clear()
        elif jogador.pontos >= 250 and fase == 2:
            fase = 3  # Fase do Chefão
            inimigos.clear()
            chefao = ChefaoHades()

        # Spawn de Inimigos (Fases 1 e 2)
        if fase in [1, 2]:
            timer_spawn += 1
            if timer_spawn >= 45:
                inimigos.append(Inimigo(fase))
                timer_spawn = 0

        # Atualizar Raios do Jogador
        for raio in raios_jogador[:]:
            raio.atualizar()
            if raio.x > LARGURA:
                raios_jogador.remove(raio)

        # Atualizar Inimigos Comuns
        for inimigo in inimigos[:]:
            inimigo.atualizar()
            if inimigo.x < -50:
                inimigos.remove(inimigo)
                continue

            # Colisão Raio -> Inimigo
            for raio in raios_jogador[:]:
                if inimigo.get_rect().colliderect(raio.rect):
                    SOM_EXPLOSAO.play()
                    jogador.pontos += 15
                    if inimigo in inimigos:
                        inimigos.remove(inimigo)
                    if raio in raios_jogador:
                        raios_jogador.remove(raio)
                    break

            # Colisão Inimigo -> Jogador
            if inimigo.get_rect().colliderect(jogador.get_rect()):
                SOM_DANO.play()
                jogador.vidas -= 1
                inimigos.remove(inimigo)
                if jogador.vidas <= 0:
                    estado = "GAME_OVER"

        # Lógica do Chefão Hades (Fase 3)
        if fase == 3 and chefao:
            chefao.atualizar()
            # Ataque de fogo do Hades
            if chefao.timer_ataque % 50 == 0:
                raios_inimigos.append(Raio(chefao.x, chefao.y + 45, velocidade=-7, cor=VERMELHO_HADES))

            # Colisão Raio do Jogador -> Hades
            for raio in raios_jogador[:]:
                if chefao.get_rect().colliderect(raio.rect):
                    SOM_EXPLOSAO.play()
                    chefao.vida -= 1
                    jogador.pontos += 10
                    raios_jogador.remove(raio)
                    if chefao.vida <= 0:
                        SOM_VITORIA.play()
                        estado = "VITORIA"

        # Atualizar Raios do Chefão
        for r_inimigo in raios_inimigos[:]:
            r_inimigo.atualizar()
            if r_inimigo.x < 0:
                raios_inimigos.remove(r_inimigo)
            elif r_inimigo.rect.colliderect(jogador.get_rect()):
                SOM_DANO.play()
                jogador.vidas -= 1
                raios_inimigos.remove(r_inimigo)
                if jogador.vidas <= 0:
                    estado = "GAME_OVER"

        # --- RENDERIZAÇÃO DA TELA ---
        cor_fundo = AZUL_CEU if fase == 1 else ((60, 40, 80) if fase == 2 else (40, 10, 15))
        TELA.fill(cor_fundo)

        # Fundo animado
        for estrela in estrelas:
            estrela[0] -= 2
            if estrela[0] < 0:
                estrela[0] = LARGURA
            pygame.draw.rect(TELA, BRANCO, (estrela[0], estrela[1], 3, 3))

        jogador.desenhar()
        for raio in raios_jogador:
            raio.desenhar()
        for r_inimigo in raios_inimigos:
            r_inimigo.desenhar()
        for inimigo in inimigos:
            inimigo.desenhar()
        if chefao:
            chefao.desenhar()

        # Barra Superior (HUD)
        pygame.draw.rect(TELA, PRETO, (0, 0, LARGURA, 45))
        txt_vidas = fonte_hud.render(f"VIDAS: {'♥ ' * jogador.vidas}", True, VERMELHO_HADES)
        txt_pontos = fonte_hud.render(f"PONTOS: {jogador.pontos}", True, DOURADO)
        nome_fase = "FASE 1: MEDUSAS" if fase == 1 else ("FASE 2: CICLOPES" if fase == 2 else "FASE FINAL: HADES")
        txt_fase = fonte_pequena.render(nome_fase, True, BRANCO)

        TELA.blit(txt_vidas, (15, 10))
        TELA.blit(txt_pontos, (LARGURA - 200, 10))
        if fase != 3:
            TELA.blit(txt_fase, (LARGURA // 2 - txt_fase.get_width() // 2, 14))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    jogar()