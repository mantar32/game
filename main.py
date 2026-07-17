import pygame
import random
import math
import sys
import os
import asyncio
try:
    import platform as web_platform
except Exception:
    web_platform = None

# --- Constants & Settings ---
WIDTH, HEIGHT = 1024, 600
FPS = 60
GROUND_Y = 480
GRAVITY = 0.8
WALK_SPEED = 5
JUMP_FORCE = -14
SPRITE_SCALE = 1.62
PUNCH_DAMAGE = 8
KICK_DAMAGE = 12
SPECIAL_DAMAGE = 20
BLOCK_REDUCTION = 0.0
SPECIAL_RECHARGE_RATE = 0.08
MAX_HEALTH = 100
ROUND_TIME = 99
ROUNDS_TO_WIN = 1

CHARACTER_STATS = {
    "Fighter": {
        "display": "Fighter Ninja",
        "role": "Dengeli",
        "tip": "Guclu tekme",
        "punch": PUNCH_DAMAGE,
        "kick": 15,
        "special": 18,
        "speed": 1.0,
    },
    "Shinobi": {
        "display": "Shinobi",
        "role": "Hizli",
        "tip": "Seri hareket",
        "punch": 7,
        "kick": 12,
        "special": SPECIAL_DAMAGE,
        "speed": 1.08,
    },
    "Samurai": {
        "display": "Samurai",
        "role": "Guclu",
        "tip": "Agir hasar",
        "punch": 9,
        "kick": 13,
        "special": 22,
        "speed": 0.94,
    },
    "Gotoku": {
        "display": "Gotoku",
        "role": "Hayalet",
        "tip": "Dengeli ruh",
        "punch": 8,
        "kick": 13,
        "special": 21,
        "speed": 1.02,
    },
    "Onre": {
        "display": "Onre",
        "role": "Ucucu",
        "tip": "Hizli saldiri",
        "punch": 7,
        "kick": 14,
        "special": 19,
        "speed": 1.12,
    },
    "Yurei": {
        "display": "Yurei",
        "role": "Efsunlu",
        "tip": "Ozel guc",
        "punch": 8,
        "kick": 12,
        "special": 24,
        "speed": 0.98,
    },
    "Converted_Vampire": {
        "display": "Converted Vampire",
        "role": "Vampir",
        "tip": "Dengeli isirik",
        "punch": 8,
        "kick": 13,
        "special": 22,
        "speed": 1.03,
    },
    "Countess_Vampire": {
        "display": "Countess Vampire",
        "role": "Kontes",
        "tip": "Kan buyusu",
        "punch": 7,
        "kick": 12,
        "special": 25,
        "speed": 1.0,
    },
    "Vampire_Girl": {
        "display": "Vampire Girl",
        "role": "Atik",
        "tip": "Seri vampir",
        "punch": 8,
        "kick": 14,
        "special": 21,
        "speed": 1.09,
    },
    "Satyr_1": {
        "display": "Satyr Scout",
        "role": "Hizli",
        "tip": "Seri boynuz hamlesi",
        "punch": 8,
        "kick": 13,
        "special": 20,
        "speed": 1.14,
    },
    "Satyr_2": {
        "display": "Satyr Warrior",
        "role": "Guclu",
        "tip": "Agir yakin dovus",
        "punch": 9,
        "kick": 15,
        "special": 23,
        "speed": 0.98,
    },
    "Satyr_3": {
        "display": "Satyr Shaman",
        "role": "Buyucu",
        "tip": "Charge gucu",
        "punch": 7,
        "kick": 12,
        "special": 26,
        "speed": 1.04,
    },
}

# Colors
BG_TOP = (13, 27, 42)
BG_BOT = (65, 90, 119)
GROUND_COLOR = (43, 43, 43)
P1_COLOR = (60, 140, 255)
P2_COLOR = (255, 60, 100)
TEXT_COLOR = (240, 240, 240)
HIGHLIGHT = (255, 215, 0)

BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()

pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    pass
screen = pygame.display.set_mode((WIDTH, HEIGHT))
game_surface = pygame.Surface((WIDTH, HEIGHT)).convert()
pygame.display.set_caption("Dovus Oyunu - Mobil Surum")
clock = pygame.time.Clock()
font_large = pygame.font.SysFont("impact", 72)
font_med = pygame.font.SysFont("impact", 48)
font_small = pygame.font.SysFont("arial", 24, bold=True)
font_touch = pygame.font.SysFont("arial", 18, bold=True)

WEB_KEY_NAMES = {
    pygame.K_a: "a",
    pygame.K_d: "d",
    pygame.K_w: "w",
    pygame.K_j: "j",
    pygame.K_k: "k",
    pygame.K_l: "l",
    pygame.K_u: "u",
}


def web_get_bool(name):
    if web_platform is None:
        return False
    try:
        return bool(getattr(web_platform.window, name, False))
    except Exception:
        pass
    try:
        return bool(web_platform.window[name])
    except Exception:
        pass
    try:
        return bool(web_platform.window.eval(f"Boolean(globalThis.{name})"))
    except Exception:
        return False


def web_set_bool(name, value):
    if web_platform is None:
        return
    try:
        setattr(web_platform.window, name, value)
    except Exception:
        pass
    try:
        web_platform.window.eval(f"globalThis.{name} = {'true' if value else 'false'}")
    except Exception:
        pass


def web_key_state(key_name):
    if web_platform is None:
        return False
    for store_name in ("dovus_keys", "__dovus_keys"):
        try:
            keys = getattr(web_platform.window, store_name, None)
            if keys is not None:
                try:
                    return bool(keys[key_name])
                except Exception:
                    if bool(getattr(keys, key_name, False)):
                        return True
        except Exception:
            pass
        try:
            if bool(web_platform.window.eval(f"Boolean(globalThis.{store_name} && globalThis.{store_name}['{key_name}'])")):
                return True
        except Exception:
            pass
    return False


def web_key_pressed(key):
    key_name = WEB_KEY_NAMES.get(key)
    if not key_name:
        return False
    return web_key_state(key_name)


def web_start_requested():
    if web_get_bool("dovus_start") or web_get_bool("__dovus_start"):
        web_set_bool("dovus_start", False)
        web_set_bool("__dovus_start", False)
        return True
    return False


def web_restart_requested():
    if web_get_bool("dovus_restart") or web_get_bool("__dovus_restart"):
        web_set_bool("dovus_restart", False)
        web_set_bool("__dovus_restart", False)
        return True
    return False


def web_home_requested():
    if web_get_bool("dovus_home") or web_get_bool("__dovus_home"):
        web_set_bool("dovus_home", False)
        web_set_bool("__dovus_home", False)
        return True
    return False


def web_selected_character():
    if web_platform is None:
        return "Fighter"
    value = None
    try:
        value = getattr(web_platform.window, "dovus_character", None)
    except Exception:
        pass
    if not value:
        try:
            value = web_platform.window.eval("globalThis.dovus_character || 'Fighter'")
        except Exception:
            value = None
    return value if value in CHARACTER_STATS else "Fighter"


def publish_web_state(game):
    if web_platform is None:
        return
    try:
        active_match = bool(hasattr(game, "p1") and game.state != "MENU")
        p1_dead = bool(active_match and game.p1.health <= 0)
        p2_dead = bool(active_match and game.p2.health <= 0)
        player_dead = p1_dead or p2_dead
        p1_won = bool(hasattr(game, "p1") and game.state == "GAME_OVER" and game.p1.rounds_won >= ROUNDS_TO_WIN)
        match_id = getattr(game, "match_id", 0)
        timer_end = getattr(game, "timer_end", pygame.time.get_ticks())
        restart_ready = bool(game.state in ("ROUND_END", "GAME_OVER") and pygame.time.get_ticks() - timer_end >= 1000)
        setattr(web_platform.window, "dovus_state", game.state)
        setattr(web_platform.window, "dovus_player_dead", player_dead)
        setattr(web_platform.window, "dovus_p1_dead", p1_dead)
        setattr(web_platform.window, "dovus_p2_dead", p2_dead)
        setattr(web_platform.window, "dovus_game_over", game.state == "GAME_OVER")
        setattr(web_platform.window, "dovus_p1_won", p1_won)
        setattr(web_platform.window, "dovus_match_id", match_id)
        setattr(web_platform.window, "dovus_restart_ready", restart_ready)
        web_platform.window.eval(
            "globalThis.dovus_state = %r; globalThis.dovus_player_dead = %s; globalThis.dovus_game_over = %s; "
            "globalThis.dovus_p1_won = %s; globalThis.dovus_match_id = %d; "
            "globalThis.dovus_p1_dead = %s; globalThis.dovus_p2_dead = %s; globalThis.dovus_restart_ready = %s"
            % (
                game.state,
                "true" if player_dead else "false",
                "true" if game.state == "GAME_OVER" else "false",
                "true" if p1_won else "false",
                match_id,
                "true" if p1_dead else "false",
                "true" if p2_dead else "false",
                "true" if restart_ready else "false",
            )
        )
    except Exception:
        pass


def game_viewport(window_size=None):
    return pygame.Rect(0, 0, WIDTH, HEIGHT)


def screen_to_game(pos):
    viewport = game_viewport()
    x = (pos[0] - viewport.x) * WIDTH / viewport.width
    y = (pos[1] - viewport.y) * HEIGHT / viewport.height
    return max(0, min(WIDTH - 1, int(x))), max(0, min(HEIGHT - 1, int(y)))


def finger_to_game(event):
    win_w, win_h = screen.get_size()
    return screen_to_game((event.x * win_w, event.y * win_h))


def present_game():
    screen.blit(game_surface, (0, 0))

# --- Sanal Dokunmatik Kontroller (Touch UI) ---
class TouchButton:
    def __init__(self, rect, key, text, color, text_color=(255,255,255)):
        self.rect = pygame.Rect(rect)
        self.key = key
        self.text = text
        self.base_color = color
        self.text_color = text_color
        self.is_pressed = False

class TouchController:
    PAD = 18       # kenar boşluğu
    BTN = 80       # D-pad buton boyutu
    ABTN = 90      # aksiyon buton boyutu

    def __init__(self):
        P = self.PAD; B = self.BTN; A = self.ABTN
        BY = HEIGHT - P - B          # en alttaki buton Y
        LX = P                       # sol başlangıç X

        # --- SOL D-PAD ---
        self.buttons = [
            # Sol
            TouchButton((LX,              BY, B, B), pygame.K_a, "<", (60, 60, 60)),
            # Sağ
            TouchButton((LX + B + P,      BY, B, B), pygame.K_d, ">", (60, 60, 60)),
            # Zıpla (ortada üstte)
            TouchButton((LX + (B+P)//2,   BY - B - P, B, B), pygame.K_w, "^", (60, 80, 60)),

            # --- SAĞ AKSİYON BUTONLARI ---
            # Yumruk - sol
            TouchButton((WIDTH - P - A*2 - P,  BY,      A, A), pygame.K_j, "YUM", (200, 60, 60)),
            # Tekme - sağ
            TouchButton((WIDTH - P - A,         BY,      A, A), pygame.K_k, "TEK", (60, 180, 60)),
            # Özel - üst orta
            TouchButton((WIDTH - P - A - A//2 - P//2, BY - A - P, A, A), pygame.K_l, "OZEL", (60, 60, 200)),
            # Blok - üst sağ
            TouchButton((WIDTH - P - A,          BY - A - P, A, A), pygame.K_u, "BLOK", (120, 80, 20)),
        ]
        self.active_touches = {}
        self.virtual_keys = {b.key: False for b in self.buttons}

    def _hit_test(self, x, y):
        for b in self.buttons:
            if b.rect.collidepoint(x, y):
                return b
        return None

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            b = self._hit_test(*event.pos)
            if b:
                b.is_pressed = True
                self.virtual_keys[b.key] = True
                self.active_touches['mouse'] = b
        elif event.type == pygame.MOUSEBUTTONUP:
            b = self.active_touches.pop('mouse', None)
            if b:
                b.is_pressed = False
                self.virtual_keys[b.key] = False
        elif event.type == pygame.FINGERDOWN:
            x, y = event.x * WIDTH, event.y * HEIGHT
            b = self._hit_test(x, y)
            if b:
                b.is_pressed = True
                self.virtual_keys[b.key] = True
                self.active_touches[event.finger_id] = b
        elif event.type == pygame.FINGERUP:
            b = self.active_touches.pop(event.finger_id, None)
            if b:
                b.is_pressed = False
                self.virtual_keys[b.key] = False

    def draw(self, surface):
        for b in self.buttons:
            # Yarı saydam arka yüzey
            s = pygame.Surface((b.rect.width, b.rect.height), pygame.SRCALPHA)
            alpha = 230 if b.is_pressed else 160
            col = (min(255, b.base_color[0]+80), min(255, b.base_color[1]+80), min(255, b.base_color[2]+80)) if b.is_pressed else b.base_color
            pygame.draw.rect(s, (*col, alpha), (0, 0, b.rect.width, b.rect.height), border_radius=20)
            # Kenarlık
            border_col = (255, 255, 0) if b.is_pressed else (180, 180, 180)
            pygame.draw.rect(s, (*border_col, 255), (0, 0, b.rect.width, b.rect.height), 3, border_radius=20)
            surface.blit(s, b.rect.topleft)
            # Yazı
            lbl = font_small.render(b.text, True, b.text_color)
            surface.blit(lbl, (b.rect.centerx - lbl.get_width()//2, b.rect.centery - lbl.get_height()//2))



class MobileTouchController:
    PAD = 22
    BTN = 86
    ABTN = 88
    SAFE_BOTTOM = 74
    ACTION_KEYS = {pygame.K_j, pygame.K_k, pygame.K_l, pygame.K_u}

    def __init__(self):
        p = self.PAD
        b = self.BTN
        a = self.ABTN
        by = HEIGHT - self.SAFE_BOTTOM - b
        lx = p

        self.buttons = [
            TouchButton((lx, by, b, b), pygame.K_a, "<\nSOL", (45, 56, 68)),
            TouchButton((lx + b + p, by, b, b), pygame.K_d, ">\nSAG", (45, 56, 68)),
            TouchButton((lx + (b + p)//2, by - b - p, b, b), pygame.K_w, "^\nZIPLA", (47, 94, 79)),
            TouchButton((WIDTH - p - a*2 - p, by, a, a), pygame.K_j, "VUR", (205, 55, 55)),
            TouchButton((WIDTH - p - a, by, a, a), pygame.K_k, "TEKME", (55, 155, 75)),
            TouchButton((WIDTH - p - a*2 - p, by - a - p, a, a), pygame.K_l, "OZEL", (68, 83, 190)),
            TouchButton((WIDTH - p - a, by - a - p, a, a), pygame.K_u, "KORUN", (158, 105, 38)),
        ]
        self.active_touches = {}
        self.virtual_keys = {button.key: False for button in self.buttons}

    def _hit_test(self, x, y):
        for button in self.buttons:
            if button.rect.collidepoint(x, y):
                return button
        return None

    def _button_at_event_pos(self, pos):
        direct = self._hit_test(*pos)
        if direct:
            return direct
        game_pos = screen_to_game(pos)
        return self._hit_test(*game_pos) if game_pos else None

    def _set_touch(self, touch_id, button):
        old_button = self.active_touches.get(touch_id)
        if old_button is button:
            return
        if old_button:
            old_button.is_pressed = False
            self.virtual_keys[old_button.key] = False
        if button:
            if button.key in self.ACTION_KEYS:
                for other in self.buttons:
                    if other.key in self.ACTION_KEYS and other.key != button.key:
                        other.is_pressed = False
                        self.virtual_keys[other.key] = False
            button.is_pressed = True
            self.virtual_keys[button.key] = True
            self.active_touches[touch_id] = button
        else:
            self.active_touches.pop(touch_id, None)

    def clear(self):
        for button in self.buttons:
            button.is_pressed = False
            self.virtual_keys[button.key] = False
        self.active_touches.clear()

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self._set_touch("mouse", self._button_at_event_pos(event.pos))
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
            self._set_touch("mouse", self._button_at_event_pos(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP:
            self._set_touch("mouse", None)
        elif event.type == pygame.FINGERDOWN:
            game_pos = finger_to_game(event)
            self._set_touch(event.finger_id, self._hit_test(*game_pos) if game_pos else None)
        elif event.type == pygame.FINGERMOTION:
            game_pos = finger_to_game(event)
            self._set_touch(event.finger_id, self._hit_test(*game_pos) if game_pos else None)
        elif event.type == pygame.FINGERUP:
            self._set_touch(event.finger_id, None)

    def draw(self, surface, special_ready=True):
        for button in self.buttons:
            is_special_locked = button.key == pygame.K_l and not special_ready
            panel = pygame.Surface((button.rect.width, button.rect.height), pygame.SRCALPHA)
            alpha = 150 if is_special_locked else (245 if button.is_pressed else 215)
            color = (70, 70, 82) if is_special_locked else button.base_color
            if button.is_pressed and not is_special_locked:
                color = tuple(min(255, channel + 70) for channel in button.base_color)
            pygame.draw.rect(panel, (*color, alpha), panel.get_rect(), border_radius=14)
            border = (110, 110, 125) if is_special_locked else ((255, 255, 0) if button.is_pressed else (235, 235, 235))
            pygame.draw.rect(panel, (*border, 255), panel.get_rect(), 4, border_radius=14)
            surface.blit(panel, button.rect.topleft)

            lines = button.text.split("\n")
            line_height = font_touch.get_height()
            top = button.rect.centery - (line_height * len(lines)) // 2
            for index, line in enumerate(lines):
                label = font_touch.render(line, True, button.text_color)
                surface.blit(label, (button.rect.centerx - label.get_width()//2, top + index * line_height))


class CombinedKeys:
    def __init__(self, real_keys, virtual_keys):
        self.real_keys = real_keys
        self.virtual_keys = virtual_keys
    def __getitem__(self, key):
        return self.real_keys[key] or self.virtual_keys.get(key, False) or web_key_pressed(key)


# --- Sprite Loader ---
class SpriteManager:
    def __init__(self, base_path):
        self.base_path = base_path
        self.sprites = {}
        self.anim_map = {
            "Idle": "Idle.png", "Walk": "Run.png", "Jump": "Jump.png",
            "Punch": "Attack_1.png", "Kick": "Attack_2.png", "Special": "Attack_3.png",
            "Block": "Shield.png", "HitStun": "Hurt.png", "KO": "Dead.png"
        }
        
    def resolve_anim_path(self, folder_name, anim_file):
        fallbacks = {
            "Run.png": ["Walk.png", "Idle.png"],
            "Jump.png": ["Flight.png", "Run.png", "Walk.png", "Idle.png"],
            "Shield.png": ["Protect.png", "Idle.png"],
            "Attack_1.png": ["Attack.png"],
            "Attack_2.png": ["Attack.png", "Attack_1.png"],
            "Attack_3.png": ["Charge.png", "Attack_4.png", "Attack_2.png", "Attack.png"],
        }
        for file_name in [anim_file] + fallbacks.get(anim_file, []):
            full_path = os.path.join(self.base_path, folder_name, file_name)
            if os.path.exists(full_path):
                return full_path
        return os.path.join(self.base_path, folder_name, anim_file)

    def load_anim(self, folder_name, anim_file):
        full_path = self.resolve_anim_path(folder_name, anim_file)
        if not os.path.exists(full_path):
            surf = pygame.Surface((128, 128), pygame.SRCALPHA)
            fallback_color = (255, 0, 0) if folder_name == "Fighter" else (0, 0, 255)
            if folder_name == "Samurai":
                fallback_color = (255, 170, 40)
            elif folder_name in ("Gotoku", "Onre", "Yurei"):
                fallback_color = (165, 120, 255)
            surf.fill(fallback_color)
            return [surf]
        try:
            sheet = pygame.image.load(full_path).convert_alpha()
        except:
            return [pygame.Surface((128, 128))]
        frame_h = sheet.get_height()
        frame_w = frame_h
        num_frames = sheet.get_width() // frame_w
        frames = []
        target_scale = SPRITE_SCALE * (128 / frame_h)
        for i in range(max(1, num_frames)):
            frame = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h))
            frame = pygame.transform.scale(frame, (int(frame_w * target_scale), int(frame_h * target_scale)))
            frames.append(frame)
        return frames

    def load_character(self, character_id):
        if character_id in self.sprites:
            return
        self.sprites[character_id] = {}
        for anim_name, file_name in self.anim_map.items():
            self.sprites[character_id][anim_name] = self.load_anim(character_id, file_name)

    def get_frames(self, character_id, anim_name):
        if character_id not in CHARACTER_STATS:
            character_id = "Fighter"
        self.load_character(character_id)
        return self.sprites[character_id][anim_name]

assets_path = os.path.join(BASE_DIR, "assets")
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
    def __init__(self):
        self.particles = []
        self.floaters = []

    def emit_hit(self, x, y):
        for _ in range(15):
            angle = random.uniform(0, math.pi * 2); speed = random.uniform(2, 8)
            self.particles.append([x, y, HIGHLIGHT, math.cos(angle)*speed, math.sin(angle)*speed, random.randint(10, 30), 30])

    def emit_block(self, x, y):
        for _ in range(10):
            angle = random.uniform(0, math.pi * 2); speed = random.uniform(1, 5)
            self.particles.append([x, y, (100, 200, 255), math.cos(angle)*speed, math.sin(angle)*speed, random.randint(10, 20), 20])

    def emit_text(self, x, y, text, color):
        self.floaters.append([x, y, text, color, 44, 44])

    def update_and_draw(self, surface, cam):
        for p in self.particles[:]:
            p[0] += p[3]; p[1] += p[4]; p[5] -= 1
            if p[5] <= 0: self.particles.remove(p)
            else:
                alpha = int(255 * (p[5] / p[6]))
                surf = pygame.Surface((6, 6), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*p[2], alpha), (3, 3), 3)
                surface.blit(surf, (p[0] + cam[0] - 3, p[1] + cam[1] - 3))
        for floater in self.floaters[:]:
            floater[1] -= 0.9
            floater[4] -= 1
            if floater[4] <= 0:
                self.floaters.remove(floater)
            else:
                alpha = int(255 * (floater[4] / floater[5]))
                label = font_small.render(floater[2], True, floater[3])
                label.set_alpha(alpha)
                surface.blit(label, (floater[0] + cam[0] - label.get_width() // 2, floater[1] + cam[1]))

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
        if keys[fighter.controls['kick']]: fighter.change_state(KickState())
        elif keys[fighter.controls['punch']]: fighter.change_state(PunchState())
        elif keys[fighter.controls['special']] and fighter.special_meter >= 100: fighter.change_state(SpecialState())
        elif keys[fighter.controls['block']]: fighter.change_state(BlockState())
        elif keys[fighter.controls['up']]: fighter.change_state(JumpState())
        elif keys[fighter.controls['left']] or keys[fighter.controls['right']]: fighter.change_state(WalkState())

class WalkState(State):
    def enter(self, fighter): fighter.set_anim("Walk")
    def update(self, fighter, keys):
        if fighter.is_ko: fighter.change_state(IdleState()); return
        if keys[fighter.controls['left']]: fighter.vel[0] = -fighter.walk_speed; fighter.facing = -1
        elif keys[fighter.controls['right']]: fighter.vel[0] = fighter.walk_speed; fighter.facing = 1
        else: fighter.change_state(IdleState())
    def handle_input(self, fighter, keys):
        if keys[fighter.controls['kick']]: fighter.change_state(KickState())
        elif keys[fighter.controls['punch']]: fighter.change_state(PunchState())
        elif keys[fighter.controls['special']] and fighter.special_meter >= 100: fighter.change_state(SpecialState())
        elif keys[fighter.controls['block']]: fighter.change_state(BlockState())
        elif keys[fighter.controls['up']]: fighter.change_state(JumpState())

class JumpState(State):
    def enter(self, fighter):
        fighter.vel[1] = JUMP_FORCE; fighter.set_anim("Jump", loop=False)
    def update(self, fighter, keys):
        if keys[fighter.controls['left']]: fighter.vel[0] = -fighter.walk_speed
        elif keys[fighter.controls['right']]: fighter.vel[0] = fighter.walk_speed
        else: fighter.vel[0] = 0
        if fighter.pos[1] >= GROUND_Y:
            fighter.pos[1] = GROUND_Y; fighter.change_state(IdleState())

class AttackState(State):
    def __init__(self, anim_name, duration, active_start, active_end, damage, h_w, h_h, h_dx, h_dy, move_speed=0):
        self.anim_name = anim_name; self.duration = duration
        self.active_start = active_start; self.active_end = active_end
        self.damage = damage
        self.h_w, self.h_h = h_w, h_h; self.h_dx, self.h_dy = h_dx, h_dy
        self.move_speed = move_speed
    def enter(self, fighter):
        fighter.set_anim(self.anim_name, loop=False)
        fighter.anim_timer = 0; fighter.vel[0] = 0; fighter.hit_connected = False
    def update(self, fighter, keys):
        fighter.anim_timer += 1
        fighter.vel[0] = fighter.facing * self.move_speed
        if self.active_start <= fighter.anim_timer <= self.active_end:
            hx = fighter.pos[0] + (self.h_dx if fighter.facing == 1 else -self.h_dx - self.h_w)
            hy = fighter.pos[1] - self.h_dy
            fighter.hitbox = pygame.Rect(hx, hy, self.h_w, self.h_h)
            fighter.current_damage = fighter.damage_for(self.anim_name, self.damage)
        else: fighter.hitbox = None
        if fighter.anim_timer >= self.duration: fighter.change_state(IdleState())

class PunchState(AttackState):
    def __init__(self): super().__init__("Punch", 24, 8, 16, PUNCH_DAMAGE, 60, 40, 20, 90)
class KickState(AttackState):
    def __init__(self): super().__init__("Kick", 30, 9, 21, KICK_DAMAGE, 86, 34, 24, 62, move_speed=2.4)
class SpecialState(AttackState):
    def __init__(self): super().__init__("Special", 40, 15, 30, SPECIAL_DAMAGE, 100, 100, 10, 120, move_speed=0.8)
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
    def __init__(self, pid, character_id, color, x, facing, controls):
        self.pid = pid; self.character_id = character_id; self.color = color
        self.stats = CHARACTER_STATS.get(character_id, CHARACTER_STATS["Fighter"])
        self.name = self.stats["display"]
        self.walk_speed = WALK_SPEED * self.stats.get("speed", 1.0)
        self.pos = [x, GROUND_Y]; self.vel = [0, 0]; self.facing = facing
        self.health = MAX_HEALTH; self.special_meter = 0
        self.controls = controls
        self.hurtbox = pygame.Rect(0, 0, 50, 100); self.hitbox = None
        self.hit_connected = False; self.current_damage = 0
        self.is_ko = False; self.rounds_won = 0
        self.current_anim = "Idle"
        self.frames = assets.get_frames(self.character_id, self.current_anim)
        self.frame_index = 0; self.anim_speed = 0.2; self.loop_anim = True
        self.state = IdleState(); self.state.enter(self)

    def damage_for(self, anim_name, fallback):
        key = {"Punch": "punch", "Kick": "kick", "Special": "special"}.get(anim_name)
        return self.stats.get(key, fallback) if key else fallback

    def set_anim(self, name, loop=True):
        if self.current_anim != name:
            self.current_anim = name; self.frames = assets.get_frames(self.character_id, name)
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
        pygame.draw.ellipse(surface, (20,20,20), (cx-26, GROUND_Y+cam[1]-9, 52, 18))
        if len(self.frames) > 0:
            img = self.frames[int(self.frame_index)]
            if self.facing == -1: img = pygame.transform.flip(img, True, False)
            img_rect = img.get_rect(midbottom=(cx, cy + 12))
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


class EmptyKeys:
    def __getitem__(self, key):
        return False


# --- GameManager ---
class GameManager:
    def __init__(self):
        self.state = "MENU"
        self.camera = Camera(); self.particles = ParticleSystem()
        self.timer = ROUND_TIME; self.last_tick = 0
        self.match_id = 0
        self.touch_ui = MobileTouchController()
        
        self.ctrl_p1 = {'up': pygame.K_w, 'left': pygame.K_a, 'right': pygame.K_d, 'punch': pygame.K_j, 'kick': pygame.K_k, 'special': pygame.K_l, 'block': pygame.K_u}
        self.ctrl_p2 = {'up': pygame.K_UP, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'punch': pygame.K_KP1, 'kick': pygame.K_KP2, 'special': pygame.K_KP3, 'block': pygame.K_KP0}

    def update_finish_animations(self):
        no_keys = EmptyKeys()
        for fighter in (getattr(self, "p1", None), getattr(self, "p2", None)):
            if fighter and (fighter.is_ko or fighter.health <= 0):
                if not isinstance(fighter.state, KOState):
                    fighter.is_ko = True
                    fighter.change_state(KOState())
                fighter.update(no_keys)
        self.camera.update()

    def start_fight(self, vs_ai):
        self.touch_ui.clear()
        self.match_id += 1
        self.ai_mode = vs_ai; self.ai = AIController(self.ctrl_p2) if vs_ai else None
        p1_character = web_selected_character()
        opponents = [character_id for character_id in CHARACTER_STATS if character_id != p1_character]
        p2_character = random.choice(opponents) if opponents else "Shinobi"
        self.p1 = Fighter("P1", p1_character, P1_COLOR, 300, 1, self.ctrl_p1)
        self.p2 = Fighter("P2", p2_character, P2_COLOR, 700, -1, self.ctrl_p2)
        if vs_ai:
            self.p2.name = f"{self.p2.name} AI"
        self.reset_round(); self.state = "FIGHT"

    def reset_round(self):
        self.touch_ui.clear()
        self.p1.health = self.p2.health = MAX_HEALTH
        self.p1.special_meter = self.p2.special_meter = 100
        self.p1.pos, self.p2.pos = [250, GROUND_Y], [774, GROUND_Y]
        self.p1.change_state(IdleState()); self.p2.change_state(IdleState())
        self.p1.is_ko = self.p2.is_ko = False
        self.timer = ROUND_TIME; self.last_tick = pygame.time.get_ticks()
        self.particles.particles.clear()

    def update(self):
        if self.state == "MENU":
            return
        if self.state == "GAME_OVER":
            self.update_finish_animations()
            return
        if self.state == "ROUND_END":
            self.update_finish_animations()
            return
        
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
        self.p1.special_meter = min(100, self.p1.special_meter + SPECIAL_RECHARGE_RATE)
        self.p2.special_meter = min(100, self.p2.special_meter + SPECIAL_RECHARGE_RATE)
        
        if pygame.time.get_ticks() - self.last_tick >= 1000 and self.state == "FIGHT":
            self.timer -= 1; self.last_tick = pygame.time.get_ticks()
            if self.timer <= 0: self.handle_round_end(True)

    def check_collisions(self):
        for attacker, defender in [(self.p1, self.p2), (self.p2, self.p1)]:
            if attacker.hitbox and attacker.hitbox.colliderect(defender.hurtbox) and not attacker.hit_connected:
                attacker.hit_connected = True
                attacker.special_meter = min(100, attacker.special_meter + 10)
                if isinstance(defender.state, BlockState) and defender.facing != attacker.facing:
                    damage = attacker.current_damage * BLOCK_REDUCTION
                    defender.take_damage(damage)
                    self.particles.emit_block(defender.pos[0], defender.pos[1]-60)
                    self.particles.emit_text(defender.pos[0], defender.pos[1]-145, "BLOK", (120, 210, 255))
                else:
                    damage = attacker.current_damage
                    defender.take_damage(damage)
                    defender.change_state(HitStunState())
                    self.particles.emit_hit(defender.pos[0], defender.pos[1]-60); self.camera.shake()
                    self.particles.emit_text(defender.pos[0], defender.pos[1]-145, f"-{int(damage)}", (255, 230, 80))
                if defender.health <= 0 and self.state == "FIGHT":
                    defender.is_ko = True
                    defender.change_state(KOState())
                    self.handle_round_end(False, attacker)

    def handle_round_end(self, timeout, winner=None):
        self.state = "ROUND_END"; self.timer_end = pygame.time.get_ticks()
        self.touch_ui.clear()
        if timeout:
            if self.p1.health > self.p2.health:
                winner = self.p1
            elif self.p2.health > self.p1.health:
                winner = self.p2
        if winner:
            winner.rounds_won += 1
            if winner.rounds_won >= ROUNDS_TO_WIN: self.state = "GAME_OVER"

    def draw(self, surface):
        for i in range(HEIGHT):
            color = [BG_TOP[j] + (BG_BOT[j]-BG_TOP[j])*(i/HEIGHT) for j in range(3)]
            pygame.draw.line(surface, color, (0, i), (WIDTH, i))
        pygame.draw.rect(surface, GROUND_COLOR, (0, GROUND_Y + self.camera.offset[1], WIDTH, HEIGHT))

        if self.state == "MENU":
            # Başlık
            pygame.draw.rect(surface, (8, 16, 28), (0, 0, WIDTH, 250))
            for radius, ring_color in ((360, (20, 64, 95)), (260, (35, 80, 112))):
                pygame.draw.circle(surface, ring_color, (WIDTH // 2, 110), radius, 2)
            pygame.draw.line(surface, HIGHLIGHT, (WIDTH // 2 - 190, 178), (WIDTH // 2 + 190, 178), 3)

            title_shadow = font_large.render("STREET FIGHTER PY", True, (0, 0, 0))
            title = font_large.render("STREET FIGHTER PY", True, HIGHLIGHT)
            title_x = WIDTH // 2 - title.get_width() // 2
            surface.blit(title_shadow, (title_x + 4, 76))
            surface.blit(title, (title_x, 72))
            sub = font_small.render("ARENA SENI BEKLIYOR!", True, TEXT_COLOR)
            surface.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 158))

            hint = font_touch.render("Karakterini sec, arenaya gir, coin kazan.", True, (210, 220, 230))
            surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 202))
            return

        self.p1.draw(surface, self.camera.offset); self.p2.draw(surface, self.camera.offset)
        self.particles.update_and_draw(surface, self.camera.offset)

        pygame.draw.rect(surface, (255,0,0), (50, 30, 400, 30))
        pygame.draw.rect(surface, (0,255,0), (50, 30, 400 * (self.p1.health/MAX_HEALTH), 30))
        pygame.draw.rect(surface, TEXT_COLOR, (50, 30, 400, 30), 2)
        pygame.draw.rect(surface, (0,0,255), (50, 65, 200 * (self.p1.special_meter/100), 10))
        pygame.draw.rect(surface, TEXT_COLOR, (50, 65, 200, 10), 1)
        surface.blit(font_small.render(self.p1.name, True, TEXT_COLOR), (50, 5))
        if self.p1.special_meter >= 100 and self.state == "FIGHT":
            surface.blit(font_touch.render("OZEL HAZIR", True, HIGHLIGHT), (260, 61))
        for i in range(ROUNDS_TO_WIN): pygame.draw.circle(surface, HIGHLIGHT if i < self.p1.rounds_won else (100,100,100), (50 + i*25, 85), 10)

        pygame.draw.rect(surface, (255,0,0), (WIDTH-450, 30, 400, 30))
        pygame.draw.rect(surface, (0,255,0), (WIDTH-450 + 400*(1-self.p2.health/MAX_HEALTH), 30, 400*(self.p2.health/MAX_HEALTH), 30))
        pygame.draw.rect(surface, TEXT_COLOR, (WIDTH-450, 30, 400, 30), 2)
        pygame.draw.rect(surface, (0,0,255), (WIDTH-250, 65, 200 * (self.p2.special_meter/100), 10))
        pygame.draw.rect(surface, TEXT_COLOR, (WIDTH-250, 65, 200, 10), 1)
        name_surf = font_small.render(self.p2.name, True, TEXT_COLOR)
        surface.blit(name_surf, (WIDTH - 50 - name_surf.get_width(), 5))
        if self.p2.special_meter >= 100 and self.state == "FIGHT":
            ready = font_touch.render("OZEL HAZIR", True, HIGHLIGHT)
            surface.blit(ready, (WIDTH - 260 - ready.get_width(), 61))
        for i in range(ROUNDS_TO_WIN): pygame.draw.circle(surface, HIGHLIGHT if i < self.p2.rounds_won else (100,100,100), (WIDTH - 50 - i*25, 85), 10)

        t_surf = font_large.render(str(self.timer), True, HIGHLIGHT)
        surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 20))

        if self.state == "ROUND_END":
            txt = font_large.render("K.O." if self.p1.is_ko or self.p2.is_ko else "TIME UP", True, (255,50,50))
            surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
        elif self.state == "GAME_OVER":
            winner = self.p1.name if self.p1.rounds_won >= ROUNDS_TO_WIN else self.p2.name
            txt = font_large.render(f"{winner} KAZANDI!", True, HIGHLIGHT)
            surface.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 120))

            hint = font_small.render("Yeni mac icin TEKRAR BASLAT butonuna bas.", True, (180, 180, 180))
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 70))
            return

    def __restart(self):
        self.touch_ui.clear()
        self.state = "MENU"


# --- Asenkron Ana Döngü (Pygbag Uyumlu) ---
async def main():
    global screen
    game = GameManager()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_1) and game.state == "MENU":
                    game.start_fight(True)
                elif event.key == pygame.K_r and game.state in ("ROUND_END", "GAME_OVER"):
                    game.start_fight(True)
            
            # Dokunmatik (Touch) girdilerini işleme (sadece oyun icerisinde)
            if game.state == "FIGHT":
                game.touch_ui.process_event(event)

        if web_start_requested():
            if game.state == "MENU":
                game.start_fight(True)
            elif game.state == "GAME_OVER":
                game.start_fight(True)

        if web_restart_requested():
            game.start_fight(True)

        if web_home_requested():
            game._GameManager__restart()

        game.update()
        publish_web_state(game)
        game.draw(game_surface)
        present_game()
        pygame.display.flip()
        clock.tick(FPS)
        
        # Tarayıcı sekmesinin donmasını engellemek için asyncio uyku komutu (Zorunlu)
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

# Script çalıştırıldığında asenkron ana döngüyü başlat
if __name__ == "__main__":
    asyncio.run(main())
