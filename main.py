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
BLOCK_REDUCTION = 0.3
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
    "Fire_Wizard": {
        "display": "Fire Wizard",
        "role": "Atesci",
        "tip": "Ates topu firlatir",
        "punch": 7,
        "kick": 11,
        "special": 28,
        "speed": 0.97,
    },
    "Lightning_Mage": {
        "display": "Lightning Mage",
        "role": "Seker",
        "tip": "Simsek yagdirir",
        "punch": 6,
        "kick": 10,
        "special": 30,
        "speed": 1.06,
    },
    "Wanderer_Magician": {
        "display": "Wanderer Magician",
        "role": "Gezgin",
        "tip": "Sihirli okllar",
        "punch": 7,
        "kick": 12,
        "special": 26,
        "speed": 1.02,
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


def web_is_input_focused():
    if web_platform is None:
        return False
    try:
        return bool(web_platform.window.eval("globalThis.dovus_input_focused"))
    except Exception:
        return False

# --- Network Helpers ---
def web_get_network_mode():
    if web_platform is None:
        return "OFFLINE"
    try:
        net = getattr(web_platform.window, "dovus_network", None)
        if net:
            return str(getattr(net, "mode", "OFFLINE"))
    except Exception:
        pass
    try:
        return str(web_platform.window.eval("globalThis.dovus_network ? globalThis.dovus_network.mode : 'OFFLINE'"))
    except Exception:
        return "OFFLINE"


def web_get_network_username():
    if web_platform is None:
        return "Oyuncu"
    try:
        net = getattr(web_platform.window, "dovus_network", None)
        if net:
            return str(getattr(net, "username", "Oyuncu"))
    except Exception:
        pass
    return "Oyuncu"


def web_get_remote_username():
    if web_platform is None:
        return "Rakip"
    try:
        net = getattr(web_platform.window, "dovus_network", None)
        if net:
            return str(getattr(net, "remoteUsername", "Rakip"))
    except Exception:
        pass
    return "Rakip"


def web_get_remote_keys():
    """Client'in bastigi tuslari Host tarafinda oku"""
    if web_platform is None:
        return []
    try:
        net = getattr(web_platform.window, "dovus_network", None)
        if net:
            keys = getattr(net, "remoteKeys", None)
            if keys:
                return list(keys)
    except Exception:
        pass
    return []


def web_get_incoming_state():
    """Host'tan Client'a gelen oyun durumunu oku"""
    if web_platform is None:
        return None
    try:
        net = getattr(web_platform.window, "dovus_network", None)
        if net:
            state = getattr(net, "inState", None)
            if state:
                result = {
                    "p1x": float(getattr(state, "p1x", 0)),
                    "p1y": float(getattr(state, "p1y", 0)),
                    "p2x": float(getattr(state, "p2x", 0)),
                    "p2y": float(getattr(state, "p2y", 0)),
                    "p1h": float(getattr(state, "p1h", 100)),
                    "p2h": float(getattr(state, "p2h", 100)),
                    "p1s": float(getattr(state, "p1s", 0)),
                    "p2s": float(getattr(state, "p2s", 0)),
                    "p1f": int(getattr(state, "p1f", 1)),
                    "p2f": int(getattr(state, "p2f", -1)),
                    "p1a": str(getattr(state, "p1a", "Idle")),
                    "p2a": str(getattr(state, "p2a", "Idle")),
                    "p1ko": bool(getattr(state, "p1ko", False)),
                    "p2ko": bool(getattr(state, "p2ko", False)),
                    "timer": int(getattr(state, "timer", 99)),
                    "gstate": str(getattr(state, "gstate", "FIGHT")),
                    "flash": int(getattr(state, "flash", 0)),
                }
                return result
    except Exception:
        pass
    return None


def web_publish_game_state(game):
    """Host olarak oyun durumunu JS tarafina yaz"""
    if web_platform is None:
        return
    try:
        state_js = (
            "{p1x:%.1f,p1y:%.1f,p2x:%.1f,p2y:%.1f,"
            "p1h:%.1f,p2h:%.1f,p1s:%.1f,p2s:%.1f,"
            "p1f:%d,p2f:%d,"
            "p1a:'%s',p2a:'%s',"
            "p1ko:%s,p2ko:%s,"
            "timer:%d,gstate:'%s',flash:%d}"
        ) % (
            game.p1.pos[0], game.p1.pos[1],
            game.p2.pos[0], game.p2.pos[1],
            game.p1.health, game.p2.health,
            game.p1.special_meter, game.p2.special_meter,
            game.p1.facing, game.p2.facing,
            game.p1.current_anim, game.p2.current_anim,
            "true" if game.p1.is_ko else "false",
            "true" if game.p2.is_ko else "false",
            game.timer, game.state,
            getattr(game, "flash_alpha", 0),
        )
        web_platform.window.eval(f"globalThis.dovus_network.outState = {state_js}")
    except Exception:
        pass


def screen_to_game(pos):
    win_w, win_h = screen.get_size()
    x = pos[0] * WIDTH / win_w
    y = pos[1] * HEIGHT / win_h
    return max(0, min(WIDTH - 1, int(x))), max(0, min(HEIGHT - 1, int(y)))


def finger_to_game(event):
    win_w, win_h = screen.get_size()
    return screen_to_game((event.x * win_w, event.y * win_h))


def present_game():
    screen.blit(game_surface, (0, 0))

class TouchButton:
    def __init__(self, rect, key, text, color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(rect)
        self.key = key
        self.text = text
        self.base_color = color
        self.text_color = text_color
        self.is_pressed = False

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
            self._set_touch(event.finger_id, self._hit_test(*game_pos))
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


class _DictKeys:
    """Dict tabanli key durumu okuyucu — AI input icin kullanilir."""
    def __init__(self, d):
        self.d = d
    def __getitem__(self, k):
        return self.d.get(k, False)



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
            "Attack_3.png": ["Charge.png", "Fireball.png", "Flame_jet.png", "Light_charge.png", "Magic_sphere.png", "Attack_4.png", "Attack_2.png", "Attack.png"],
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
        except Exception as e:
            print(f"[SpriteManager] Sprite yuklenemedi: {full_path} ({e})")
            return [pygame.Surface((128, 128))]
        frame_h = sheet.get_height()
        frame_w = frame_h
        num_frames = sheet.get_width() // frame_w
        frames = []
        target_scale = SPRITE_SCALE * (128 / frame_h)
        is_dead = (anim_file == "Dead.png")
        for i in range(max(1, num_frames)):
            frame = sheet.subsurface(pygame.Rect(i * frame_w, 0, frame_w, frame_h))
            frame = pygame.transform.scale(frame, (int(frame_w * target_scale), int(frame_h * target_scale)))
            if is_dead:
                # Gorunur piksel alanini hesapla ve frame'i crop et
                bbox = frame.get_bounding_rect()
                if bbox.width > 0 and bbox.height > 0:
                    cropped = pygame.Surface((bbox.width, bbox.height), pygame.SRCALPHA)
                    cropped.blit(frame, (0, 0), bbox)
                    frame = cropped
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

class SoundManager:
    def __init__(self, base_path):
        self.sounds = {}
        self.base_path = base_path
        self.enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except Exception as e:
            print(f"[SoundManager] Mixer baslatilamadi: {e}")
            self.enabled = False

    def load(self, name, filename):
        if not self.enabled: return
        path = os.path.join(self.base_path, "sounds", filename)
        if os.path.exists(path):
            try:
                self.sounds[name] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"[SoundManager] Ses yuklenemedi: {path} ({e})")

    def play(self, name):
        if self.enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except Exception as e:
                print(f"[SoundManager] Ses calinamadi: {name} ({e})")

assets_path = os.path.join(BASE_DIR, "assets")
assets = SpriteManager(assets_path)
sounds = SoundManager(assets_path)
sounds.load("punch", "punch.ogg")
sounds.load("kick", "kick.ogg")
sounds.load("special", "special.ogg")
sounds.load("block", "block.ogg")
sounds.load("ko", "ko.ogg")
sounds.load("hit", "hit.ogg")


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

class Projectile:
    def __init__(self, x, y, vel_x, owner, damage):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.owner = owner
        self.damage = damage
        self.rect = pygame.Rect(x - 20, y - 20, 40, 40)
        self.active = True
        self.hit_connected = False
        
        if owner.character_id == "Fire_Wizard": self.color = (255, 80, 0)
        elif owner.character_id == "Lightning_Mage": self.color = (100, 200, 255)
        elif owner.character_id == "Wanderer_Magician": self.color = (180, 100, 255)
        else: self.color = (255, 255, 255)
        
        self.trail_timer = 0
        
    def update(self):
        self.x += self.vel_x
        self.rect.centerx = int(self.x)
        self.trail_timer += 1
        if self.x < -400 or self.x > WIDTH + 400:
            self.active = False
            
    def draw(self, surface, cam, particles):
        cx, cy = int(self.x + cam[0]), int(self.y + cam[1])
        pygame.draw.circle(surface, self.color, (cx, cy), 18)
        pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 8)
        if self.trail_timer % 2 == 0 and particles:
            particles.emit(self.x, self.y, self.color, 1)

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
        if getattr(fighter, 'stun_timer', 0) > 0: return  # Sersemletilmis, hareket edemiyor
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
        sounds.play(self.anim_name.lower())
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
    def enter(self, fighter): 
        super().enter(fighter); fighter.special_meter = 0
        fighter.projectile_fired = False

    def update(self, fighter, keys):
        fighter.anim_timer += 1
        if not getattr(fighter, 'is_ranged', False):
            fighter.vel[0] = fighter.facing * self.move_speed
            if self.active_start <= fighter.anim_timer <= self.active_end:
                hx = fighter.pos[0] + (self.h_dx if fighter.facing == 1 else -self.h_dx - self.h_w)
                hy = fighter.pos[1] - self.h_dy
                fighter.hitbox = pygame.Rect(hx, hy, self.h_w, self.h_h)
                fighter.current_damage = fighter.damage_for(self.anim_name, self.damage)
            else: fighter.hitbox = None
        else:
            fighter.vel[0] = 0
            fighter.hitbox = None
            fighter.current_damage = fighter.damage_for(self.anim_name, self.damage)
            if fighter.anim_timer == self.active_start and not fighter.projectile_fired:
                fighter.projectile_fired = True
                px = fighter.pos[0] + (60 * fighter.facing)
                py = fighter.pos[1] - 80
                p_vel = 14 * fighter.facing
                fighter.active_projectiles.append(Projectile(px, py, p_vel, fighter, fighter.current_damage))
                sounds.play("punch") # or special sound
                
        if fighter.anim_timer >= self.duration: fighter.change_state(IdleState())

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
        fighter.set_anim("KO", loop=False)
        fighter.vel[1] = 0
        fighter.vel[0] = 0
        fighter.hitbox = None
    def update(self, fighter, keys):
        pass  # Karakter yerde hareketsiz duruyor

# --- Fighter ---
class Fighter:
    def __init__(self, pid, character_id, color, x, facing, controls):
        self.pid = pid; self.character_id = character_id; self.color = color
        self.stats = CHARACTER_STATS.get(character_id, CHARACTER_STATS["Fighter"])
        self.name = self.stats["display"]
        self.walk_speed = WALK_SPEED * self.stats.get("speed", 1.0)
        self.pos = [x, GROUND_Y]; self.vel = [0, 0]; self.facing = facing
        self.anim_timer = 0
        self.health = MAX_HEALTH; self.special_meter = 0
        self.combo_count = 0; self.combo_timer = 0
        self.controls = controls
        self.hurtbox = pygame.Rect(0, 0, 50, 100); self.hitbox = None
        self.hit_connected = False; self.current_damage = 0
        self.is_ko = False; self.rounds_won = 0
        self.current_anim = "Idle"
        self.is_ranged = character_id in ["Fire_Wizard", "Lightning_Mage", "Wanderer_Magician"]
        self.active_projectiles = []
        
        # Passive abilities
        self.lifesteal = 0.05 if "Vampire" in self.character_id else 0.0
        self.crit_chance = 0.15 if self.character_id == "Samurai" else 0.0
        self.dodge_chance = 0.10 if self.character_id == "Shinobi" else 0.0
        self.reflect_damage = 0.15 if "Satyr" in self.character_id else 0.0
        # Wizard passives
        self.burn_on_special = self.character_id == "Fire_Wizard"       # Ozel saldiri sonrasi yanma efekti
        self.stun_on_special = self.character_id == "Lightning_Mage"     # Ozel saldiri sonrasi sersemletme
        self.spell_amp = 0.20 if self.character_id == "Wanderer_Magician" else 0.0  # Ozel saldiri hasari %20 artis
        self.burn_timer = 0   # Yanma suresi (kare sayisi)
        self.stun_timer = 0   # Sersemletme suresi
        
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
        mult = 2.0 if self.character_id == "Gotoku" else 1.5
        self.special_meter = min(100, self.special_meter + amount * mult)

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
        
        if self.combo_timer > 0:
            self.combo_timer -= 1
            if self.combo_timer <= 0: self.combo_count = 0
        
        for p in self.active_projectiles:
            p.update()
        self.active_projectiles = [p for p in self.active_projectiles if p.active]
        
        # Yanma hasari (Fire Wizard ozel etkisi)
        if self.burn_timer > 0:
            self.burn_timer -= 1
            if self.burn_timer % 20 == 0:  # Her 20 karede bir hasar
                self.take_damage(3)
        
        # Sersemletme (Lightning Mage ozel etkisi) - girdileri bloklar
        if self.stun_timer > 0:
            self.stun_timer -= 1

    def draw(self, surface, cam, particles=None):
        cx, cy = int(self.pos[0] + cam[0]), int(self.pos[1] + cam[1])
        pygame.draw.ellipse(surface, (20,20,20), (cx-26, GROUND_Y+cam[1]-9, 52, 18))
        if len(self.frames) > 0:
            img = self.frames[int(self.frame_index)]
            if self.facing == -1: img = pygame.transform.flip(img, True, False)
            img_rect = img.get_rect(midbottom=(cx, cy + 12))
            surface.blit(img, img_rect)
        for p in self.active_projectiles:
            p.draw(surface, cam, particles)

# --- AI Controller ---
class AIController:
    def __init__(self, controls, difficulty="Normal"): 
        self.controls = controls; self.cooldown = 0
        self.difficulty = difficulty
        
    def generate_input(self, ai_f, p_f):
        keys = {k: False for k in self.controls.values()}
        if self.difficulty == "Antrenman": return keys
        
        if ai_f.is_ko or p_f.is_ko: return keys
        if getattr(ai_f, 'stun_timer', 0) > 0: return keys  # Sersemletilmis, hareket edemiyor
        self.cooldown -= 1
        dist = abs(ai_f.pos[0] - p_f.pos[0])
        ai_f.facing = 1 if p_f.pos[0] > ai_f.pos[0] else -1
        
        if self.cooldown <= 0:
            if self.difficulty == "Kolay": self.cooldown = random.randint(30, 50); block_chance = 0.2
            elif self.difficulty == "Zor": self.cooldown = random.randint(5, 15); block_chance = 0.7
            else: self.cooldown = random.randint(15, 30); block_chance = 0.45
            
            if dist > 150: keys[self.controls['right'] if ai_f.facing == 1 else self.controls['left']] = True
            elif dist > 70:
                action = random.choice(['walk', 'kick', 'jump'])
                if action == 'walk': keys[self.controls['right'] if ai_f.facing == 1 else self.controls['left']] = True
                elif action == 'kick': keys[self.controls['kick']] = True
                elif action == 'jump': keys[self.controls['up']] = True
            else:
                if p_f.hitbox and random.random() < block_chance: keys[self.controls['block']] = True; self.cooldown = 15
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
        self.slow_mo_frames = 0
        self.flash_alpha = 0
        
        self.ctrl_p1 = {'up': pygame.K_w, 'left': pygame.K_a, 'right': pygame.K_d, 'punch': pygame.K_j, 'kick': pygame.K_k, 'special': pygame.K_l, 'block': pygame.K_u}
        self.ctrl_p2 = {'up': pygame.K_UP, 'left': pygame.K_LEFT, 'right': pygame.K_RIGHT, 'punch': pygame.K_KP1, 'kick': pygame.K_KP2, 'special': pygame.K_KP3, 'block': pygame.K_KP0}

    def update_finish_animations(self):
        no_keys = _DictKeys({})
        for fighter in (getattr(self, "p1", None), getattr(self, "p2", None)):
            if fighter and (fighter.is_ko or fighter.health <= 0):
                if not isinstance(fighter.state, KOState):
                    fighter.is_ko = True
                    fighter.change_state(KOState())
                fighter.update(no_keys)
        self.camera.update()

    def start_fight(self, vs_ai, next_arcade_level=False):
        if not next_arcade_level:
            self.touch_ui.clear()
            self.match_id += 1
            self.arcade_level = 1
        
        # Read game mode and difficulty
        difficulty = "Normal"
        self.game_mode = "Hizli Mac"
        if web_platform:
            try:
                diff = getattr(web_platform.window, "dovus_difficulty", None)
                if diff: difficulty = str(diff)
                mode = getattr(web_platform.window, "dovus_game_mode", None)
                if mode: self.game_mode = str(mode)
            except Exception:
                pass
            
        if self.game_mode == "Antrenman": difficulty = "Antrenman"
            
        self.ai_mode = vs_ai; self.ai = AIController(self.ctrl_p2, difficulty) if vs_ai else None
        p1_character = web_selected_character()
        
        if self.game_mode == "Arcade":
            arcade_opponents = ["Fighter", "Samurai", "Shinobi", "Countess_Vampire", "Satyr_2", "Satyr_3"]
            p2_character = arcade_opponents[min(self.arcade_level - 1, 5)]
        else:
            opponents = [c for c in CHARACTER_STATS if c != p1_character]
            p2_character = random.choice(opponents) if opponents else "Shinobi"
            
        self.p1 = Fighter("P1", p1_character, P1_COLOR, 300, 1, self.ctrl_p1)
        self.p2 = Fighter("P2", p2_character, P2_COLOR, 700, -1, self.ctrl_p2)
        
        # Network mode: override names and AI
        self.network_mode = web_get_network_mode()
        if self.network_mode in ("HOST", "CLIENT"):
            self.ai_mode = False
            self.ai = None
            self.p1.name = web_get_network_username()
            self.p2.name = web_get_remote_username()
        elif vs_ai:
            if self.game_mode == "Arcade":
                self.p2.name = f"{self.p2.name} (Bolum {self.arcade_level})"
            elif self.game_mode == "Antrenman":
                self.p2.name = f"{self.p2.name} (Antrenman)"
            else:
                self.p2.name = f"{self.p2.name} AI ({difficulty})"
        self.reset_round(); self.state = "FIGHT"

    def reset_round(self):
        self.touch_ui.clear()
        self.p1.health = self.p2.health = MAX_HEALTH
        self.p1.special_meter = self.p2.special_meter = 0
        self.p1.pos, self.p2.pos = [250, GROUND_Y], [774, GROUND_Y]
        self.p1.change_state(IdleState()); self.p2.change_state(IdleState())
        self.p1.is_ko = self.p2.is_ko = False
        self.p1.combo_count = self.p2.combo_count = 0
        self.p1.combo_timer = self.p2.combo_timer = 0
        self.timer = ROUND_TIME; self.last_tick = pygame.time.get_ticks()
        self.particles.particles.clear()
        self.slow_mo_frames = 0; self.flash_alpha = 0
        
        self.arena_theme = random.choice([
            {"bg": (13, 27, 42), "bot": (65, 90, 119), "ground": (43, 43, 43)},
            {"bg": (30, 5, 5), "bot": (90, 20, 20), "ground": (40, 15, 15)},
            {"bg": (5, 25, 15), "bot": (20, 80, 40), "ground": (15, 35, 20)},
            {"bg": (50, 20, 0), "bot": (120, 50, 0), "ground": (50, 25, 10)},
            {"bg": (10, 10, 10), "bot": (40, 40, 40), "ground": (25, 25, 25)}
        ])

    def update(self):
        if getattr(self, "flash_alpha", 0) > 0: 
            self.flash_alpha = max(0, self.flash_alpha - 5)
            
        if self.state == "MENU":
            return
        if self.state == "GAME_OVER":
            self.update_finish_animations()
            return
        if self.state == "ROUND_END":
            self.update_finish_animations()
            return
        
        net_mode = getattr(self, "network_mode", "OFFLINE")
        
        # --- CLIENT MODE: Fiziksiz, sadece Host'tan gelen veriyi goster ---
        if net_mode == "CLIENT":
            incoming = web_get_incoming_state()
            if incoming:
                # Pozisyonlari dogrudan atamak yerine yumusatiyoruz (lerp), boylece
                # ag gecikmesi/dusuk paket hizinda karakterler "teleport" gibi degil
                # akici hareket ediyormus gibi gorunur. Buyuk sicramalarda (ornegin
                # round basinda pozisyon sifirlanirken) lerp yerine dogrudan atama
                # yapariz ki karakter yanlislikla ekranda surunmesin.
                LERP_FACTOR = 0.35
                SNAP_DISTANCE = 150  # bu mesafeden buyuk farklarda dogrudan atla
                for fighter, key_x, key_y in ((self.p1, "p1x", "p1y"), (self.p2, "p2x", "p2y")):
                    target_x, target_y = incoming[key_x], incoming[key_y]
                    if abs(fighter.pos[0] - target_x) > SNAP_DISTANCE:
                        fighter.pos[0] = target_x
                    else:
                        fighter.pos[0] += (target_x - fighter.pos[0]) * LERP_FACTOR
                    if abs(fighter.pos[1] - target_y) > SNAP_DISTANCE:
                        fighter.pos[1] = target_y
                    else:
                        fighter.pos[1] += (target_y - fighter.pos[1]) * LERP_FACTOR
                self.p1.health = incoming["p1h"]
                self.p2.health = incoming["p2h"]
                self.p1.special_meter = incoming["p1s"]
                self.p2.special_meter = incoming["p2s"]
                self.p1.facing = incoming["p1f"]
                self.p2.facing = incoming["p2f"]
                self.p1.set_anim(incoming["p1a"])
                self.p2.set_anim(incoming["p2a"])
                self.p1.is_ko = incoming["p1ko"]
                self.p2.is_ko = incoming["p2ko"]
                self.timer = incoming["timer"]
                self.flash_alpha = incoming["flash"]
                if incoming["gstate"] in ("ROUND_END", "GAME_OVER"):
                    self.state = incoming["gstate"]
                    self.timer_end = pygame.time.get_ticks()
                self.p1.hurtbox.midbottom = (self.p1.pos[0], self.p1.pos[1])
                self.p2.hurtbox.midbottom = (self.p2.pos[0], self.p2.pos[1])
                # Animate frames
                for f in (self.p1, self.p2):
                    if len(f.frames) > 0:
                        f.frame_index += f.anim_speed
                        if f.frame_index >= len(f.frames):
                            if f.loop_anim: f.frame_index = 0
                            else: f.frame_index = len(f.frames) - 1
            self.camera.update()
            return
        
        # --- HOST or OFFLINE MODE: Normal fizik ---
        real_keys = pygame.key.get_pressed()
        combined_keys = CombinedKeys(real_keys, self.touch_ui.virtual_keys)
        
        self.p1.state.handle_input(self.p1, combined_keys)
        
        if net_mode == "HOST":
            # Host modunda P2'yi uzaktan gelen tuslarla kontrol et
            remote_keys = web_get_remote_keys()
            KEY_MAP = {"a": pygame.K_a, "d": pygame.K_d, "w": pygame.K_w, "j": pygame.K_j, "k": pygame.K_k, "l": pygame.K_l, "u": pygame.K_u}
            remote_dict = {v: False for v in self.ctrl_p2.values()}
            for k_name in remote_keys:
                # Remote keys come as P1 key names, remap to P2 controls
                p1_to_action = {"a": "left", "d": "right", "w": "up", "j": "punch", "k": "kick", "l": "special", "u": "block"}
                action = p1_to_action.get(str(k_name))
                if action and action in self.ctrl_p2:
                    remote_dict[self.ctrl_p2[action]] = True
            p2_keys = _DictKeys(remote_dict)
            self.p2.state.handle_input(self.p2, p2_keys)
            self.p2.update(p2_keys)
        elif self.ai_mode:
            ai_keys = self.ai.generate_input(self.p2, self.p1)
            comb = {k: real_keys[k] for k in range(len(real_keys))}
            comb.update(ai_keys)
            p2_keys = _DictKeys(comb)
            self.p2.state.handle_input(self.p2, p2_keys)
            self.p2.update(p2_keys)
        else:
            self.p2.state.handle_input(self.p2, real_keys)
            self.p2.update(real_keys)

        if not isinstance(self.p1.state, AttackState) and not isinstance(self.p2.state, AttackState):
            self.p1.facing, self.p2.facing = (1, -1) if self.p1.pos[0] < self.p2.pos[0] else (-1, 1)

        self.p1.update(combined_keys)
        self.check_collisions(); self.camera.update()
        self.p1.special_meter = min(100, self.p1.special_meter + SPECIAL_RECHARGE_RATE)
        self.p2.special_meter = min(100, self.p2.special_meter + SPECIAL_RECHARGE_RATE)
        
        if getattr(self, "game_mode", "") == "Antrenman":
            self.p1.special_meter = 100
            if self.p2.health <= 0:
                self.p2.health = MAX_HEALTH
                self.p2.is_ko = False
                self.p2.change_state(IdleState())
        
        if self.slow_mo_frames > 0: self.slow_mo_frames -= 1
        
        if pygame.time.get_ticks() - self.last_tick >= 1000 and self.state == "FIGHT":
            self.last_tick = pygame.time.get_ticks()
            if getattr(self, "game_mode", "") != "Antrenman":
                self.timer -= 1
                if self.timer <= 0: self.handle_round_end(True)

    def check_collisions(self):
        for attacker, defender in [(self.p1, self.p2), (self.p2, self.p1)]:
            if defender.is_ko or defender.health <= 0:
                continue
                
            hit_detected = False
            is_projectile = False
            active_proj = None
            
            if attacker.hitbox and attacker.hitbox.colliderect(defender.hurtbox) and not attacker.hit_connected:
                hit_detected = True
            else:
                for p in attacker.active_projectiles:
                    if p.active and not p.hit_connected and p.rect.colliderect(defender.hurtbox):
                        hit_detected = True
                        is_projectile = True
                        active_proj = p
                        break
                        
            if hit_detected:
                # Dodge check
                if random.random() < defender.dodge_chance and not isinstance(defender.state, BlockState):
                    self.particles.emit_text(defender.pos[0], defender.pos[1]-145, "DODGE!", (150, 255, 150))
                    if is_projectile:
                        active_proj.hit_connected = True
                        active_proj.active = False
                    else:
                        attacker.hit_connected = True
                    continue
                    
                if is_projectile:
                    active_proj.hit_connected = True
                    active_proj.active = False
                    self.particles.emit(active_proj.x, active_proj.y, active_proj.color, 15)
                    base_damage = active_proj.damage
                else:
                    attacker.hit_connected = True
                    base_damage = attacker.current_damage
                    
                attacker.special_meter = min(100, attacker.special_meter + 10)
                
                if isinstance(defender.state, BlockState) and defender.facing != attacker.facing:
                    # BLOK basarili: SIFIR HASAR (Can azalmaz)
                    sounds.play("block")
                    self.particles.emit_block(defender.pos[0], defender.pos[1]-60)
                    self.particles.emit_text(defender.pos[0], defender.pos[1]-145, "BLOK", (120, 210, 255))
                    attacker.combo_count = 0 
                    
                    if defender.reflect_damage > 0:
                        reflect = base_damage * defender.reflect_damage
                        attacker.take_damage(reflect)
                        self.particles.emit_text(attacker.pos[0], attacker.pos[1]-145, f"REFLECT {int(reflect)}", (255, 100, 255))
                else:
                    attacker.combo_count += 1
                    attacker.combo_timer = 90
                    combo_bonus = 1.0 + (attacker.combo_count - 1) * 0.15
                    
                    damage = base_damage * combo_bonus
                    
                    if random.random() < attacker.crit_chance:
                        damage *= 2.0
                        self.particles.emit_text(attacker.pos[0], attacker.pos[1]-180, "CRITICAL!", (255, 50, 50))
                        
                    defender.take_damage(damage)
                    
                    if attacker.lifesteal > 0:
                        heal = damage * attacker.lifesteal
                        attacker.health = min(MAX_HEALTH, attacker.health + heal)
                        self.particles.emit_text(attacker.pos[0], attacker.pos[1]-145, f"+{int(heal)} HP", (50, 255, 50))
                    elif attacker.character_id == "Yurei" and (isinstance(attacker.state, SpecialState) or is_projectile):
                        heal = damage * 0.3
                        attacker.health = min(MAX_HEALTH, attacker.health + heal)
                        self.particles.emit_text(attacker.pos[0], attacker.pos[1]-145, f"+{int(heal)} HP", (50, 255, 50))
                    
                    # Wizard ozel etkiler (sadece Special saldirida)
                    if isinstance(attacker.state, SpecialState) or is_projectile:
                        if attacker.burn_on_special:
                            defender.burn_timer = 120  # 2 saniye yanma
                            self.particles.emit_text(defender.pos[0], defender.pos[1]-160, "YANMA!", (255, 80, 0))
                        if attacker.stun_on_special:
                            defender.stun_timer = 40  # ~0.6 saniye sersemletme
                            self.particles.emit_text(defender.pos[0], defender.pos[1]-160, "SERSEM!", (150, 180, 255))
                        if attacker.spell_amp > 0:
                            bonus = damage * attacker.spell_amp
                            defender.take_damage(bonus)
                            self.particles.emit_text(attacker.pos[0], attacker.pos[1]-170, "BUYULU!", (180, 100, 255))
                    
                    sounds.play("hit")
                    defender.change_state(HitStunState())
                    self.particles.emit_hit(defender.pos[0], defender.pos[1]-60); self.camera.shake(intensity=8 + attacker.combo_count*2)
                    self.particles.emit_text(defender.pos[0], defender.pos[1]-145, f"-{int(damage)}", (255, 230, 80))
                    
                    if attacker.combo_count >= 3:
                        self.particles.emit_text(attacker.pos[0], attacker.pos[1]-160, f"{attacker.combo_count} COMBO!", (255, 100, 50))
                
                if defender.health <= 0 and self.state == "FIGHT":
                    sounds.play("ko")
                    defender.is_ko = True
                    defender.change_state(KOState())
                    self.slow_mo_frames = 60
                    self.flash_alpha = 255
                    self.camera.shake(frames=30, intensity=15)
                    self.handle_round_end(False, attacker)

    def handle_round_end(self, timeout, winner=None):
        self.state = "ROUND_END"; self.timer_end = pygame.time.get_ticks()
        self.touch_ui.clear()
        self.is_draw = False
        if timeout:
            if self.p1.health > self.p2.health:
                winner = self.p1
            elif self.p2.health > self.p1.health:
                winner = self.p2
            else:
                self.is_draw = True
        if winner:
            winner.rounds_won += 1
            if winner.rounds_won >= ROUNDS_TO_WIN: 
                if getattr(self, "game_mode", "") == "Arcade" and winner == self.p1 and getattr(self, "arcade_level", 1) < 6:
                    self.arcade_level += 1
                    self.start_fight(True, next_arcade_level=True)
                else:
                    self.state = "GAME_OVER"
                    if getattr(self, "game_mode", "") == "Arcade" and winner == self.p1 and getattr(self, "arcade_level", 1) == 6:
                        if web_platform:
                            try:
                                web_platform.window.eval("globalThis.dovus_arcade_won = true;")
                            except Exception:
                                pass

    def draw(self, surface):
        bg = getattr(self, 'arena_theme', {"bg": BG_TOP, "bot": BG_BOT, "ground": GROUND_COLOR})
        for i in range(HEIGHT):
            color = [bg["bg"][j] + (bg["bot"][j]-bg["bg"][j])*(i/HEIGHT) for j in range(3)]
            pygame.draw.line(surface, color, (0, i), (WIDTH, i))
        pygame.draw.rect(surface, bg["ground"], (0, GROUND_Y + self.camera.offset[1], WIDTH, HEIGHT))

        if self.state == "MENU":
            pygame.draw.rect(surface, (8, 16, 28), (0, 0, WIDTH, HEIGHT))
            for radius, ring_color in ((360, (20, 64, 95)), (260, (35, 80, 112)), (180, (25, 70, 100))):
                pygame.draw.circle(surface, ring_color, (WIDTH // 2, HEIGHT // 2), radius, 2)
            for i in range(HEIGHT // 2, HEIGHT):
                t = (i - HEIGHT // 2) / (HEIGHT // 2)
                color = [8 + (65 - 8) * t, 16 + (90 - 16) * t, 28 + (119 - 28) * t]
                pygame.draw.line(surface, color, (0, i), (WIDTH, i))
            pygame.draw.line(surface, HIGHLIGHT, (WIDTH // 2 - 220, 148), (WIDTH // 2 + 220, 148), 3)
            return

        self.p1.draw(surface, self.camera.offset, self.particles)
        self.p2.draw(surface, self.camera.offset, self.particles)
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

        if self.p1.combo_count >= 2:
            combo_txt = font_med.render(f"{self.p1.combo_count} HIT COMBO", True, (255, 120, 50))
            surface.blit(combo_txt, (50, 110))

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

        if self.p2.combo_count >= 2:
            combo_txt = font_med.render(f"{self.p2.combo_count} HIT COMBO", True, (255, 120, 50))
            surface.blit(combo_txt, (WIDTH - 50 - combo_txt.get_width(), 110))

        t_surf = font_large.render(str(self.timer), True, HIGHLIGHT)
        surface.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 20))

        if self.state == "ROUND_END":
            if getattr(self, "is_draw", False):
                txt = font_large.render("BERABERE!", True, (200, 200, 80))
            elif self.p1.is_ko or self.p2.is_ko:
                txt = font_large.render("K.O.", True, (255, 50, 50))
            else:
                txt = font_large.render("TIME UP", True, (255, 50, 50))
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2))
        elif self.state == "GAME_OVER":
            winner = self.p1.name if self.p1.rounds_won >= ROUNDS_TO_WIN else self.p2.name
            txt = font_large.render(f"{winner} KAZANDI!", True, HIGHLIGHT)
            surface.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 120))
            hint = font_small.render("Yeni mac icin TEKRAR BASLAT butonuna bas.", True, (180, 180, 180))
            surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 70))
        
        if getattr(self, "flash_alpha", 0) > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill((255, 255, 255))
            flash_surf.set_alpha(self.flash_alpha)
            surface.blit(flash_surf, (0, 0))

    def restart(self):
        self.touch_ui.clear()
        self.state = "MENU"
        self.is_draw = False


# --- Asenkron Ana Dongu (Pygbag Uyumlu) ---
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
                    if not web_is_input_focused():
                        game.start_fight(True)
                elif event.key == pygame.K_r and game.state in ("ROUND_END", "GAME_OVER"):
                    game.start_fight(True)
            
            # Dokunmatik (Touch) girdilerini isleme (sadece oyun icerisinde)
            if game.state == "FIGHT":
                game.touch_ui.process_event(event)

        if web_start_requested():
            if game.state == "MENU":
                game.start_fight(True)
            elif game.state == "GAME_OVER":
                game.start_fight(True)

        if web_restart_requested():
            if game.state == "ROUND_END":
                game.reset_round()
                game.state = "FIGHT"
            else:
                game.start_fight(True)

        if web_home_requested():
            game.restart()

        game.update()
        publish_web_state(game)
        
        # Network sync: Host yayini
        if getattr(game, "network_mode", "OFFLINE") == "HOST" and game.state != "MENU":
            web_publish_game_state(game)
        
        game.draw(game_surface)
        present_game()
        pygame.display.flip()
        
        current_fps = 20 if getattr(game, 'slow_mo_frames', 0) > 0 else FPS
        clock.tick(current_fps)
        
        # Tarayici sekmesinin donmasini engellemek icin asyncio uyku komutu (Zorunlu)
        await asyncio.sleep(0)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())