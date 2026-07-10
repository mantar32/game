import pygame
import random
import math
import sys
import os
import asyncio

# --- Constants & Settings ---
WIDTH, HEIGHT = 1024, 600
FPS = 60
GROUND_Y = 480
GRAVITY = 0.8
WALK_SPEED = 5
JUMP_FORCE = -14
PUNCH_DAMAGE = 8
KICK_DAMAGE = 12
SPECIAL_DAMAGE = 20
BLOCK_REDUCTION = 0.5
MAX_HEALTH = 100
ROUND_TIME = 99
ROUNDS_TO_WIN = 2

# Colors
BG_TOP = (13, 27, 42)
BG_BOT = (65, 90, 119)
GROUND_COLOR = (43, 43, 43)
P1_COLOR = (60, 140, 255)
P2_COLOR = (255, 60, 100)
TEXT_COLOR = (240, 240, 240)
HIGHLIGHT = (255, 215, 0)

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dövüş Oyunu - Mobil Sürüm")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont("impact", 72)
font_med = pygame.font.SysFont("impact", 48)
font_small = pygame.font.SysFont("arial", 24, bold=True)

# --- Sanal Dokunmatik Kontroller (Touch UI) ---
class TouchButton:
    def __init__(self, rect, key, text, color=(100, 100, 100, 120)):
        self.rect = pygame.Rect(rect)
        self.key = key
        self.text = text
        self.color = color
        self.is_pressed = False

class TouchController:
    def __init__(self):
        self.buttons = [
            # Sol Taraf (Yön)
            TouchButton((20, HEIGHT - 120, 80, 80), pygame.K_a, "<"),
            TouchButton((120, HEIGHT - 120, 80, 80), pygame.K_d, ">"),
            TouchButton((70, HEIGHT - 210, 80, 80), pygame.K_w, "ZILA"),
            TouchButton((70, HEIGHT - 40, 80, 40), pygame.K_u, "BLOK"),
            
            # Sağ Taraf (Aksiyon)
            TouchButton((WIDTH - 200, HEIGHT - 100, 80, 80), pygame.K_j, "YUMRUK", (200, 50, 50, 120)),
            TouchButton((WIDTH - 100, HEIGHT - 160, 80, 80), pygame.K_k, "TEKME", (50, 200, 50, 120)),
            TouchButton((WIDTH - 100, HEIGHT - 60, 80, 60), pygame.K_l, "ÖZEL", (50, 50, 200, 120)),
        ]
        self.active_touches = {}
        self.virtual_keys = {k.key: False for k in self.buttons}

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for b in self.buttons:
                if b.rect.collidepoint(event.pos):
                    b.is_pressed = True
                    self.virtual_keys[b.key] = True
                    self.active_touches['mouse'] = b
        elif event.type == pygame.MOUSEBUTTONUP:
            if 'mouse' in self.active_touches:
                b = self.active_touches['mouse']
                b.is_pressed = False
                self.virtual_keys[b.key] = False
                del self.active_touches['mouse']
        
        elif event.type == pygame.FINGERDOWN:
            x, y = event.x * WIDTH, event.y * HEIGHT
            for b in self.buttons:
                if b.rect.collidepoint(x, y):
                    b.is_pressed = True
                    self.virtual_keys[b.key] = True
                    self.active_touches[event.finger_id] = b
        elif event.type == pygame.FINGERUP:
            if event.finger_id in self.active_touches:
                b = self.active_touches[event.finger_id]
                b.is_pressed = False
                self.virtual_keys[b.key] = False
                del self.active_touches[event.finger_id]

    def draw(self, surface):
        for b in self.buttons:
            s = pygame.Surface((b.rect.width, b.rect.height), pygame.SRCALPHA)
            color = (255, 255, 255, 200) if b.is_pressed else b.color
            pygame.draw.rect(s, color, (0, 0, b.rect.width, b.rect.height), border_radius=40)
            surface.blit(s, b.rect.topleft)
            txt = font_small.render(b.text, True, (255,255,255) if not b.is_pressed else (0,0,0))
            surface.blit(txt, (b.rect.centerx - txt.get_width()//2, b.rect.centery - txt.get_height()//2))

class CombinedKeys:
    def __init__(self, real_keys, virtual_keys):
        self.real_keys = real_keys
        self.virtual_keys = virtual_keys
    def __getitem__(self, key):
        return self.real_keys[key] or self.virtual_keys.get(key, False)


# --- Sprite Loader ---
class SpriteManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.sprites = {"P1": {}, "P2": {}}
        self.load_all()
        
    def load_anim(self, folder_name, anim_file):
        full_path = os.path.join(self.base_path, folder_name, anim_file)
        if not os.path.exists(full_path):
            surf = pygame.Surface((128, 128), pygame.SRCALPHA)
            surf.fill((255,0,0) if folder_name=="Fighter" else (0,0,255))
            return [surf]
        try:
            sheet = pygame.image.load(full_path).convert_alpha()
        except:
            return [pygame.Surface((128, 128))]
        frame_w, frame_h = 128, 128
        num_frames = sheet.get_width() // frame_w
        frames = []
        for i in range(max(1, num_frames)):
            frame = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h))
            frame = pygame.transform.scale(frame, (frame_w * 2, frame_h * 2))
            frames.append(frame)
        return frames

    def load_all(self):
        mapping = [("P1", "Fighter"), ("P2", "Shinobi")]
        anim_map = {
            "Idle": "Idle.png", "Walk": "Run.png", "Jump": "Jump.png",
            "Punch": "Attack_1.png", "Kick": "Attack_2.png", "Special": "Attack_3.png",
            "Block": "Shield.png", "HitStun": "Hurt.png", "KO": "Dead.png"
        }
        for p_id, folder in mapping:
            for anim_name, file_name in anim_map.items():
                self.sprites[p_id][anim_name] = self.load_anim(folder, file_name)

assets_path = r"assets"
assets = SpriteManager(assets_path)


# --- Camera & Particles ---
class Camera:
    def __init__(self):
        self.offset = [0, 0]; self.shake_frames = 0; self.intensity = 0
    def shake(self, frames=10, intensity=8):
        self.shake_frames = frames; self.intensity = intensity
    def update(self):
        if self.shake_frames > 0:
            self.offset[0] = random.randint(-self.intensity, self.intensity)
            self.offset[1] = random.randint(-self.intensity, self.intensity)
            self.shake_frames -= 1
        else: self.offset = [0, 0]

class ParticleSystem:
    def __init__(self): self.particles = []
    def emit_hit(self, x, y):
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2); speed = random.uniform(2, 8)
            self.particles.append([x, y, HIGHLIGHT, math.cos(angle)*speed, math.sin(angle)*speed, random.randint(10, 30), 30])
    def emit_block(self, x, y):
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2); speed = random.uniform(1, 5)
            self.particles.append([x, y, (100, 200, 255), math.cos(angle)*speed, math.sin(angle)*speed, random.randint(10, 20), 20])
    def update_and_draw(self, surface, cam):
        for p in self.particles[:]:
            p[0] += p[3]; p[1] += p[4]; p[5] -= 1
            if p[5] <= 0: self.particles.remove(p)
            else:
                alpha = int(255 * (p[5] / p[6]))
                surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*p[2], alpha), (3, 3), 3)
                surface.blit(surf, (p[0] + cam[0] - 3, p[1] + cam[1] - 3))

# --- State Machine ---
class State:
    def enter(self, fighter): pass
    def handle_input(self, fighter, keys): pass
    def update(self, fighter, keys): pass
    def exit(self, fighter): pass

class IdleState(State):
    def enter(self, fighter): fighter.set_anim("Idle")
    def update(self, fighter, keys): fighter.vel[0] = 0
    def handle_input(self, fighter, keys):
        if fighter.is_ko: return
        if keys[fighter.controls['punch']]: fighter.change_state(PunchState())
        elif keys[fighter.controls['kick']]: fighter.change_state(KickState())
        elif keys[fighter.controls['special']] and fighter.special_meter >= 100: fighter.change_state(SpecialState())
        elif keys[fighter.controls['block']]: fighter.change_state(BlockState())
        elif keys[fighter.controls['up']]: fighter.change_state(JumpState())
        elif keys[fighter.controls['left']] or keys[fighter.controls['right']]: fighter.change_state(WalkState())

class WalkState(State):
    def enter(self, fighter): fighter.set_anim("Walk")
    def update(self, fighter, keys):
        if fighter.is_ko: fighter.change_state(IdleState()); return
        if keys[fighter.controls['left']]: fighter.vel[0] = -WALK_SPEED; fighter.facing = -1
        elif keys[fighter.controls['right']]: fighter.vel[0] = WALK_SPEED; fighter.facing = 1
        else: fighter.change_state(IdleState())
    def handle_input(self, fighter, keys):
        if keys[fighter.controls['punch']]: fighter.change_state(PunchState())
        elif keys[fighter.controls['kick']]: fighter.change_state(KickState())
        elif keys[fighter.controls['special']] and fighter.special_meter >= 100: fighter.change_state(SpecialState())
        elif keys[fighter.controls['block']]: fighter.change_state(BlockState())
        elif keys[fighter.controls['up']]: fighter.change_state(JumpState())

class JumpState(State):
    def enter(self, fighter):
        fighter.vel[1] = JUMP_FORCE; fighter.set_anim("Jump", loop=False)
    def update(self, fighter, keys):
        if keys[fighter.controls['left']]: fighter.vel[0] = -WALK_SPEED
        elif keys[fighter.controls['right']]: fighter.vel[0] = WALK_SPEED
        else: fighter.vel[0] = 0
        if fighter.pos[1] >= GROUND_Y:
            fighter.pos[1] = GROUND_Y; fighter.change_state(IdleState())

class AttackState(State):
    def __init__(self, anim_name, duration, active_start, active_end, damage, h_w, h_h, h_dx, h_dy):
        self.anim_name = anim_name; self.duration = duration
        self.active_start = active_start; self.active_end = active_end
        self.damage = damage
        self.h_w, self.h_h = h_w, h_h; self.h_dx, self.h_dy = h_dx, h_dy
    def enter(self, fighter):
        fighter.set_anim(self.anim_name, loop=False)
        fighter.anim_timer = 0; fighter.vel[0] = 0; fighter.hit_connected = False
    def update(self, fighter, keys):
        fighter.anim_timer += 1
        if self.active_start <= fighter.anim_timer <= self.active_end:
            hx = fighter.pos[0] + (self.h_dx if fighter.facing == 1 else -self.h_dx - self.h_w)
            hy = fighter.pos[1] - self.h_dy
            fighter.hitbox = pygame.Rect(hx, hy, self.h_w, self.h_h)
            fighter.current_damage = self.damage
        else: fighter.hitbox = None
        if fighter.anim_timer >= self.duration: fighter.change_state(IdleState())

class PunchState(AttackState):
    def __init__(self): super().__init__("Punch", 24, 8, 16, PUNCH_DAMAGE, 60, 40, 20, 90)
class KickState(AttackState):
    def __init__(self): super().__init__("Kick", 30, 10, 20, KICK_DAMAGE, 70, 30, 20, 60)
class SpecialState(AttackState):
    def __init__(self): super().__init__("Special", 40, 15, 30, SPECIAL_DAMAGE, 100, 100, 10, 120)
    def enter(self, fighter): super().enter(fighter); fighter.special_meter = 0

class BlockState(State):
    def enter(self, fighter): fighter.set_anim("Block")
    def update(self, fighter, keys):
        fighter.vel[0] = 0
        if not keys[fighter.controls['block']]: fighter.change_state(IdleState())

class HitStunState(State):
    def enter(self, fighter):
        fighter.set_anim("HitStun", loop=False)
        fighter.anim_timer = 0; fighter.hitbox = None
    def update(self, fighter, keys):
        fighter.anim_timer += 1
        fighter.vel[0] = -fighter.facing * 3
        if fighter.anim_timer >= 20:
            if fighter.health <= 0: fighter.is_ko = True; fighter.change_state(KOState())
            else: fighter.change_state(IdleState())

class KOState(State):
    def enter(self, fighter):
        fighter.set_anim("KO", loop=False); fighter.vel[0] = 0; fighter.hitbox = None
    def update(self, fighter, keys): pass

# --- Fighter ---
class Fighter:
    def __init__(self, pid, name, color, x, facing, controls):
        self.pid = pid; self.name = name; self.color = color
        self.pos = [x, GROUND_Y]; self.vel = [0, 0]; self.facing = facing
        self.health = MAX_HEALTH; self.special_meter = 0
        self.controls = controls
        self.hurtbox = pygame.Rect(0, 0, 50, 100); self.hitbox = None
        self.hit_connected = False; self.current_damage = 0
        self.is_ko = False; self.rounds_won = 0
        self.current_anim = "Idle"
        self.frames = assets.sprites[self.pid][self.current_anim]
        self.frame_index = 0; self.anim_speed = 0.2; self.loop_anim = True
        self.state = IdleState(); self.state.enter(self)

    def set_anim(self, name, loop=True):
        if self.current_anim != name:
            self.current_anim = name; self.frames = assets.sprites[self.pid][name]
            self.frame_index = 0; self.loop_anim = loop
            if name in ["Punch", "Kick", "Special"]:
                self.anim_speed = len(self.frames) / self.state.duration if hasattr(self.state, 'duration') else 0.3
            elif name == "HitStun": self.anim_speed = len(self.frames) / 20.0
            elif name == "KO": self.anim_speed = 0.15
            else: self.anim_speed = 0.2

    def change_state(self, new_state):
        self.state.exit(self); self.state = new_state; self.state.enter(self)

    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0: self.health = 0
        self.special_meter = min(100, self.special_meter + amount * 1.5)

    def update(self, keys):
        self.state.update(self, keys)
        if self.pos[1] < GROUND_Y or self.vel[1] < 0: self.vel[1] += GRAVITY
        self.pos[0] += self.vel[0]; self.pos[1] += self.vel[1]
        if self.pos[1] > GROUND_Y: self.pos[1] = GROUND_Y; self.vel[1] = 0
        self.pos[0] = max(30, min(WIDTH - 30, self.pos[0]))
        self.hurtbox.midbottom = (self.pos[0], self.pos[1])
        if len(self.frames) > 0:
            self.frame_index += self.anim_speed
            if self.frame_index >= len(self.frames):
                if self.loop_anim: self.frame_index = 0
                else: self.frame_index = len(self.frames) - 1

    def draw(self, surface, cam):
        cx, cy = int(self.pos[0] + cam[0]), int(self.pos[1] + cam[1])
        pygame.draw.ellipse(surface, (20,20,20), (cx-30, GROUND_Y+cam[1]-10, 60, 20))
        if len(self.frames) > 0:
            img = self.frames[int(self.frame_index)]
            if self.facing == -1: img = pygame.transform.flip(img, True, False)
            img_rect = img.get_rect(midbottom=(cx, cy + 18))
            surface.blit(img, img_rect)

# --- AI Controller ---
class AIController:
    def __init__(self, controls): self.controls = controls; self.cooldown = 0
    def generate_input(self, ai_f, p_f):
        keys = {k: False for k in self.controls.values()}
        if ai_f.is_ko or p_f.is_ko: return keys
        self.cooldown -= 1
        dist = abs(ai_f.pos[0] - p_f.pos[0])
        ai_f.facing = 1 if p_f.pos[0] > ai_f.pos[0] else -1
        if self.cooldown <= 0:
            self.cooldown = random.randint(10, 30)
            if dist > 150: keys[self.controls['right'] if ai_f.facing == 1 else self.controls['left']] = True
            elif dist > 70:
                action = random.choice(['walk', 'kick', 'jump'])
                if action == 'walk': keys[self.controls['right'] if ai_f.facing == 1 else self.controls['left']] = True
                elif action == 'kick': keys[self.controls['kick']] = True
                elif action == 'jump': keys[self.controls['up']] = True
            else:
                if p_f.hitbox and random.random() < 0.6: keys[self.controls['block']] = True; self.cooldown = 20
                else: action = random.choice(['punch', 'kick', 'special', 'block']); keys[self.controls[action]] = True
        return keys

# --- GameManager ---
class GameManager:
    def __init__(self):
        self.state = "INTRO"
        self.intro_start = pygame.time.get_ticks()
        self.camera = Camera(); self.particles = ParticleSystem()
        self.timer = ROUND_TIME; self.last_tick = 0
        self.touch_ui = TouchController()
        
        self.ctrl_p1 = {'up': pygame.K_w, 'left': pygame.K_a, 'right': pygame.K_d, 'punch': pygame.K_j, 'kick': pygame.K_k, 'special': pygame.K_l, 'block': pygame.K_u}
        self.ctrl_p2 = {'up': pygame.K_UP, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'punch': pygame.K_KP1, 'kick': pygame.K_KP2, 'special': pygame.K_KP3, 'block': pygame.K_KP0}
        self.start_fight(True)

    def start_fight(self, vs_ai):
        self.ai_mode = vs_ai; self.ai = AIController(self.ctrl_p2) if vs_ai else None
        self.p1 = Fighter("P1", "Fighter Ninja", P1_COLOR, 300, 1, self.ctrl_p1)
        self.p2 = Fighter("P2", "Shinobi AI" if vs_ai else "Shinobi", P2_COLOR, 700, -1, self.ctrl_p2)
        self.reset_round(); self.state = "FIGHT"

    def reset_round(self):
        self.p1.health = self.p2.health = MAX_HEALTH
        self.p1.pos, self.p2.pos = [300, GROUND_Y], [700, GROUND_Y]
        self.p1.change_state(IdleState()); self.p2.change_state(IdleState())
        self.p1.is_ko = self.p2.is_ko = False
        self.timer = ROUND_TIME; self.last_tick = pygame.time.get_ticks()
        self.particles.particles.clear()

    def update(self):
        if self.state == "INTRO": return
        
        real_keys = pygame.key.get_pressed()
        combined_keys = CombinedKeys(real_keys, self.touch_ui.virtual_keys)
        
        self.p1.state.handle_input(self.p1, combined_keys)
        
        if self.ai_mode:
            ai_keys = self.ai.generate_input(self.p2, self.p1)
            class FakeKeys:
                def __init__(self, d): self.d = d
                def __getitem__(self, k): return self.d.get(k, False)
            comb = {k: real_keys[k] for k in range(512)}
            comb.update(ai_keys)
            self.p2.state.handle_input(self.p2, FakeKeys(comb))
            self.p2.update(FakeKeys(comb))
        else:
            self.p2.state.handle_input(self.p2, real_keys)
            self.p2.update(real_keys)

        if not isinstance(self.p1.state, AttackState) and not isinstance(self.p2.state, AttackState):
            self.p1.facing, self.p2.facing = (1, -1) if self.p1.pos[0] < self.p2.pos[0] else (-1, 1)

        self.p1.update(combined_keys)
        self.check_collisions(); self.camera.update()
        
        if pygame.time.get_ticks() - self.last_tick >= 1000 and self.state == "FIGHT":
            self.timer -= 1; self.last_tick = pygame.time.get_ticks()
            if self.timer <= 0: self.handle_round_end(True)

    def check_collisions(self):
        for attacker, defender in [(self.p1, self.p2), (self.p2, self.p1)]:
            if attacker.hitbox and attacker.hitbox.colliderect(defender.hurtbox) and not attacker.hit_connected:
                attacker.hit_connected = True
                attacker.special_meter = min(100, attacker.special_meter + 10)
                if isinstance(defender.state, BlockState) and defender.facing != attacker.facing:
                    defender.take_damage(attacker.current_damage * BLOCK_REDUCTION)
                    self.particles.emit_block(defender.pos[0], defender.pos[1]-60)
                else:
                    defender.take_damage(attacker.current_damage)
                    defender.change_state(HitStunState())
                    self.particles.emit_hit(defender.pos[0], defender.pos[1]-60); self.camera.shake()
                if defender.health <= 0 and self.state == "FIGHT": self.handle_round_end(False, attacker)

    def handle_round_end(self, timeout, winner=None):
        self.state = "ROUND_END"; self.timer_end = pygame.time.get_ticks()
        if not timeout and winner:
            winner.rounds_won += 1
            if winner.rounds_won >= ROUNDS_TO_WIN: self.state = "GAME_OVER"

    def draw(self, surface):
        for i in range(HEIGHT):
            color = [BG_TOP[j] + (BG_BOT[j]-BG_TOP[j])*(i/HEIGHT) for j in range(3)]
            pygame.draw.line(surface, color, (0, i), (WIDTH, i))
        pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y + self.camera.offset[1], WIDTH, HEIGHT))

        if self.state == "INTRO":
            elapsed = (pygame.time.get_ticks() - self.intro_start) // 1000
            countdown = 3 - elapsed
            if countdown <= 0:
                self.state = "FIGHT"
                return
            title = font_large.render("STREET FIGHTER PY", True, HIGHLIGHT)
            surface.blit(title, (WIDTH//2 - title.get_width()//2, 150))
            c = font_large.render(str(countdown), True, (255, 100, 100))
            surface.blit(c, (WIDTH//2 - c.get_width()//2, HEIGHT//2))
            sub = font_small.render("Hazır ol!", True, TEXT_COLOR)
            surface.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 90))
            return

        self.p1.draw(surface, self.camera.offset); self.p2.draw(surface, self.camera.offset)
        self.particles.update_and_draw(surface, self.camera.offset)

        pygame.draw.rect(surface, (255,0,0), (50, 30, 400, 30))
        pygame.draw.rect(surface, (0,255,0), (50, 30, 400 * (self.p1.health/MAX_HEALTH), 30))
        pygame.draw.rect(surface, (0,0,255), (50, 65, 200 * (self.p1.special_meter/100), 10))
        surface.blit(font_small.render(self.p1.name, True, TEXT_COLOR), (50, 5))
        for i in range(ROUNDS_TO_WIN): pygame.draw.circle(surface, HIGHLIGHT if i < self.p1.rounds_won else (100,100,100), (50 + i*25, 85), 10)

        pygame.draw.rect(surface, (255,0,0), (WIDTH-450, 30, 400, 30))
        pygame.draw.rect(surface, (0,255,0), (WIDTH-450 + 400*(1-self.p2.health/MAX_HEALTH), 30, 400*(self.p2.health/MAX_HEALTH), 30))
        pygame.draw.rect(surface, (0,0,255), (WIDTH-250, 65, 200 * (self.p2.special_meter/100), 10))
        name_surf = font_small.render(self.p2.name, True, TEXT_COLOR)
        surface.blit(name_surf, (WIDTH - 50 - name_surf.get_width(), 5))
        for i in range(ROUNDS_TO_WIN): pygame.draw.circle(surface, HIGHLIGHT if i < self.p2.rounds_won else (100,100,100), (WIDTH - 50 - i*25, 85), 10)

        t_surf = font_large.render(str(self.timer), True, HIGHLIGHT)
        surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 20))

        if self.state == "ROUND_END":
            txt = font_large.render("K.O." if self.p1.is_ko or self.p2.is_ko else "TIME UP", True, (255,50,50))
            surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
            if pygame.time.get_ticks() - self.timer_end > 3000: self.reset_round(); self.state = "FIGHT"
        elif self.state == "GAME_OVER":
            winner = self.p1.name if self.p1.rounds_won >= ROUNDS_TO_WIN else self.p2.name
            txt = font_large.render(f"{winner} KAZANDI!", True, HIGHLIGHT)
            surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 100))
            
            pygame.draw.rect(surface, (50, 50, 150), (WIDTH//2 - 200, HEIGHT//2 + 20, 400, 80), border_radius=20)
            sub = font_med.render("YENİDEN OYNA", True, TEXT_COLOR)
            surface.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 35))
            
            if pygame.key.get_pressed()[pygame.K_r]: self.__restart()

    def __restart(self):
        self.intro_start = pygame.time.get_ticks()
        self.state = "INTRO"
        self.start_fight(True)

        # Mobil / Dokunmatik kontrolleri çiz
        self.touch_ui.draw(surface)


# --- Asenkron Ana Döngü (Pygbag Uyumlu) ---
async def main():
    game = GameManager()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game.state == "GAME_OVER":
                    game._GameManager__restart()
            elif event.type in (pygame.MOUSEBUTTONDOWN, pygame.FINGERDOWN):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                else:
                    mx, my = event.x * WIDTH, event.y * HEIGHT
                if game.state == "GAME_OVER":
                    if HEIGHT//2 + 20 <= my <= HEIGHT//2 + 100:
                        game._GameManager__restart()
            
            # Dokunmatik (Touch) girdilerini işleme
            if game.state == "FIGHT":
                game.touch_ui.process_event(event)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        
        # Tarayıcı sekmesinin donmasını engellemek için asyncio uyku komutu (Zorunlu)
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

# Script çalıştırıldığında asenkron ana döngüyü başlat
if __name__ == "__main__":
    asyncio.run(main())
