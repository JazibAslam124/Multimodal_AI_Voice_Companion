# # avatar.py - Kira avatar overlay
# # Displays sprite sheet animation in bottom right corner
# # Black background is removed (treated as transparent)
# # Switches between idle and talking animations automatically
#
# import pygame
# import threading
# import time
# import os
# import sys
#
# # ── Config ────────────────────────────────────────────────────────────────────
# IDLE_SPRITE    = "idle.png"      # rename your idle sprite sheet to this
# TALKING_SPRITE = "talking.png"   # rename your talking sprite sheet to this
#
# COLS           = 3               # columns in sprite sheet
# ROWS           = 3               # rows in sprite sheet
# FRAME_COUNT    = 9               # total frames
# FPS            = 9               # frames per second (2s animation / 9 frames = ~4.5fps, use 9 for snappier)
#
# # Display size — scale down from 503x640 to fit nicely on screen
# DISPLAY_W      = 300
# DISPLAY_H      = 380
#
# # Black background removal threshold (0-255, higher = more aggressive)
# BLACK_THRESHOLD = 30
#
#
# class KiraAvatar:
#     def __init__(self):
#         self.is_talking  = False
#         self.running     = False
#         self._thread     = None
#
#     def set_talking(self, talking: bool):
#         self.is_talking = talking
#
#     def _remove_black(self, surface: pygame.Surface) -> pygame.Surface:
#         """Converts black pixels to transparent."""
#         surface = surface.convert_alpha()
#         arr = pygame.surfarray.pixels3d(surface)
#         alpha = pygame.surfarray.pixels_alpha(surface)
#
#         # Where all RGB channels are below threshold → set alpha to 0
#         mask = (
#             (arr[:, :, 0] < BLACK_THRESHOLD) &
#             (arr[:, :, 1] < BLACK_THRESHOLD) &
#             (arr[:, :, 2] < BLACK_THRESHOLD)
#         )
#         alpha[mask] = 0
#         del arr, alpha
#         return surface
#
#     def _load_frames(self, path: str) -> list:
#         """Loads and slices a sprite sheet into individual frames."""
#         sheet = pygame.image.load(path).convert_alpha()
#         sw, sh = sheet.get_size()
#         fw = sw // COLS
#         fh = sh // ROWS
#         frames = []
#         for row in range(ROWS):
#             for col in range(COLS):
#                 rect   = pygame.Rect(col * fw, row * fh, fw, fh)
#                 frame  = pygame.Surface((fw, fh), pygame.SRCALPHA)
#                 frame.blit(sheet, (0, 0), rect)
#                 frame  = self._remove_black(frame)
#                 frame  = pygame.transform.scale(frame, (DISPLAY_W, DISPLAY_H))
#                 frames.append(frame)
#         return frames
#
#     def _run(self):
#         pygame.init()
#
#         # Get screen size for positioning
#         info   = pygame.display.Info()
#         sw, sh = info.current_w, info.current_h
#
#         # Position: bottom right corner
#         os.environ["SDL_VIDEO_WINDOW_POS"] = f"{sw - DISPLAY_W - 20},{sh - DISPLAY_H - 60}"
#
#         # Transparent window
#         screen = pygame.display.set_mode(
#             (DISPLAY_W, DISPLAY_H),
#             pygame.NOFRAME | pygame.SRCALPHA
#         )
#         pygame.display.set_caption("Kira")
#
#         # Make window always on top and transparent on Windows
#         try:
#             import ctypes
#             hwnd = pygame.display.get_wm_info()["window"]
#             # Always on top
#             ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
#             # Layered window for transparency
#             GWL_EXSTYLE = -20
#             WS_EX_LAYERED = 0x80000
#             style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
#             ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
#             ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, 0x1)
#         except Exception as e:
#             print(f"   [Avatar] Window transparency setup: {e}")
#
#         # Load sprite sheets
#         try:
#             idle_frames    = self._load_frames(IDLE_SPRITE)
#             talking_frames = self._load_frames(TALKING_SPRITE)
#             print("   [Avatar] Sprites loaded successfully.")
#         except Exception as e:
#             print(f"   [Avatar] Failed to load sprites: {e}")
#             return
#
#         clock       = pygame.time.Clock()
#         frame_index = 0
#         self.running = True
#
#         while self.running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False
#
#             # Pick current animation
#             frames = talking_frames if self.is_talking else idle_frames
#
#             # Draw
#             screen.fill((0, 0, 0, 0))  # fully transparent background
#             screen.blit(frames[frame_index], (0, 0))
#             pygame.display.flip()
#
#             # Advance frame
#             frame_index = (frame_index + 1) % len(frames)
#             clock.tick(FPS)
#
#         pygame.quit()
#
#     def start(self):
#         """Start avatar in a background thread."""
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()
#         print("   [Avatar] Started in background.")
#
#     def stop(self):
#         self.running = False
#
#
# # Global instance — imported by tts.py and lena.py
# avatar = KiraAvatar()
#
#
# if __name__ == "__main__":
#     # Test mode — run avatar standalone
#     print("Running avatar in test mode...")
#     avatar.start()
#     time.sleep(3)
#     print("Switching to talking...")
#     avatar.set_talking(True)
#     time.sleep(3)
#     print("Back to idle...")
#     avatar.set_talking(False)
#     time.sleep(3)
#     avatar.stop()









#
#
# # avatar.py - Kira avatar overlay
# # Displays sprite sheet animation in bottom right corner
# # Switches between idle and talking animations automatically
# # Expects PNG files with proper transparency (use remove.bg to process)
#
# import pygame
# import threading
# import time
# import os
# import math
#
# # ── Config ────────────────────────────────────────────────────────────────────
# IDLE_SPRITE    = "idle.png"      # transparent PNG sprite sheet
# TALKING_SPRITE = "talking.png"   # transparent PNG sprite sheet
#
# COLS        = 3    # columns in sprite sheet
# ROWS        = 3    # rows in sprite sheet
# FRAME_COUNT = 9    # total frames
# FPS         = 6    # frames per second
#
# # Display size
# DISPLAY_W   = 280
# DISPLAY_H   = 350
#
# # Float effect — gentle up/down bob
# FLOAT_AMPLITUDE = 4    # pixels up/down
# FLOAT_SPEED     = 1.5  # cycles per second
#
#
# class KiraAvatar:
#     def __init__(self):
#         self.is_talking = False
#         self.running    = False
#         self._thread    = None
#
#     def set_talking(self, talking: bool):
#         self.is_talking = talking
#
#     def _load_frames(self, path: str) -> list:
#         """Loads and slices a transparent sprite sheet into individual frames."""
#         sheet  = pygame.image.load(path).convert_alpha()
#         sw, sh = sheet.get_size()
#         fw     = sw // COLS
#         fh     = sh // ROWS
#         frames = []
#         for row in range(ROWS):
#             for col in range(COLS):
#                 rect  = pygame.Rect(col * fw, row * fh, fw, fh)
#                 frame = pygame.Surface((fw, fh), pygame.SRCALPHA)
#                 frame.blit(sheet, (0, 0), rect)
#                 frame = pygame.transform.smoothscale(frame, (DISPLAY_W, DISPLAY_H))
#                 frames.append(frame)
#         return frames
#
#     def _run(self):
#         pygame.init()
#
#         # Position: bottom right corner
#         info   = pygame.display.Info()
#         sw, sh = info.current_w, info.current_h
#         win_x  = sw - DISPLAY_W - 20
#         win_y  = sh - DISPLAY_H - 60
#         os.environ["SDL_VIDEO_WINDOW_POS"] = f"{win_x},{win_y}"
#
#         screen = pygame.display.set_mode(
#             (DISPLAY_W, DISPLAY_H + int(FLOAT_AMPLITUDE * 2)),
#             pygame.NOFRAME | pygame.SRCALPHA
#         )
#         pygame.display.set_caption("Kira")
#
#         # Always on top + transparent window (Windows)
#         try:
#             import ctypes
#             hwnd = pygame.display.get_wm_info()["window"]
#             ctypes.windll.user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002)
#             GWL_EXSTYLE    = -20
#             WS_EX_LAYERED  = 0x80000
#             style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
#             ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_LAYERED)
#             ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, 0x1)
#         except Exception as e:
#             print(f"   [Avatar] Window setup: {e}")
#
#         # Load sprites
#         try:
#             idle_frames    = self._load_frames(IDLE_SPRITE)
#             talking_frames = self._load_frames(TALKING_SPRITE)
#             print("   [Avatar] Sprites loaded.")
#         except Exception as e:
#             print(f"   [Avatar] Failed to load sprites: {e}")
#             return
#
#         clock       = pygame.time.Clock()
#         frame_index = 0
#         start_time  = time.time()
#         self.running = True
#
#         while self.running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False
#
#             # Float offset — gentle sine wave bob
#             elapsed    = time.time() - start_time
#             float_y    = int(math.sin(elapsed * FLOAT_SPEED * 2 * math.pi) * FLOAT_AMPLITUDE)
#
#             # Pick animation
#             frames = talking_frames if self.is_talking else idle_frames
#
#             # Draw
#             screen.fill((0, 0, 0, 0))
#             screen.blit(frames[frame_index], (0, float_y + int(FLOAT_AMPLITUDE)))
#             pygame.display.flip()
#
#             frame_index = (frame_index + 1) % len(frames)
#             clock.tick(FPS)
#
#         pygame.quit()
#
#     def start(self):
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()
#         print("   [Avatar] Started.")
#
#     def stop(self):
#         self.running = False
#
#
# # Global instance
# avatar = KiraAvatar()
#
#
# if __name__ == "__main__":
#     print("Testing avatar...")
#     avatar.start()
#     time.sleep(4)
#     print("Switching to talking...")
#     avatar.set_talking(True)
#     time.sleep(4)
#     print("Back to idle...")
#     avatar.set_talking(False)
#     time.sleep(4)
#     avatar.stop()















# # avatar.py - Kira avatar overlay
# # Sprite sheet animation, black background removed
# # Always on top, transparent, click-through
#
# import pygame
# import threading
# import time
# import os
# import math
# import numpy as np
#
# # ── Config ────────────────────────────────────────────────────────────────────
# IDLE_SPRITE    = "idle.png"
# TALKING_SPRITE = "talking.png"
#
# # Frame grid — must match your sprite sheet
# COLS      = 9
# ROWS      = 8
# FRAME_W   = 400
# FRAME_H   = 225
#
# # Display size — keep 16:9 ratio
# DISPLAY_W = 400
# DISPLAY_H = 225
#
# FPS       = 12   # playback speed
#
# # Black removal — only pure black becomes transparent
# BLACK_THRESHOLD = 30
#
# # Float effect
# FLOAT_AMPLITUDE = 3
# FLOAT_SPEED     = 1.2
#
#
# def remove_black(surface: pygame.Surface) -> pygame.Surface:
#     """Replace black pixels with transparency."""
#     surface = surface.convert_alpha()
#     arr     = pygame.surfarray.pixels3d(surface)
#     alpha   = pygame.surfarray.pixels_alpha(surface)
#     mask = (
#         (arr[:, :, 0] < BLACK_THRESHOLD) &
#         (arr[:, :, 1] < BLACK_THRESHOLD) &
#         (arr[:, :, 2] < BLACK_THRESHOLD)
#     )
#     alpha[mask] = 0
#     del arr, alpha
#     return surface
#
#
# def load_frames(path: str) -> list:
#     """Load and slice sprite sheet into individual frames."""
#     if not os.path.exists(path):
#         print(f"   [Avatar] File not found: {path}")
#         return []
#
#     sheet  = pygame.image.load(path).convert_alpha()
#     frames = []
#     for row in range(ROWS):
#         for col in range(COLS):
#             rect  = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
#             frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
#             frame.blit(sheet, (0, 0), rect)
#             frame = remove_black(frame)
#             frame = pygame.transform.smoothscale(frame, (DISPLAY_W, DISPLAY_H))
#             frames.append(frame)
#
#     print(f"   [Avatar] Loaded {len(frames)} frames from {path}")
#     return frames
#
#
# class KiraAvatar:
#     def __init__(self):
#         self.is_talking = False
#         self.running    = False
#         self._thread    = None
#
#     def set_talking(self, talking: bool):
#         self.is_talking = talking
#
#     def _run(self):
#         pygame.display.init()
#
#         info   = pygame.display.Info()
#         sw, sh = info.current_w, info.current_h
#         os.environ["SDL_VIDEO_WINDOW_POS"] = f"{sw - DISPLAY_W - 20},{sh - DISPLAY_H - 80}"
#
#         screen = pygame.display.set_mode(
#             (DISPLAY_W, DISPLAY_H + int(FLOAT_AMPLITUDE * 2)),
#             pygame.NOFRAME | pygame.SRCALPHA
#         )
#         pygame.display.set_caption("Kira")
#
#         # Windows: always on top + transparent + click-through
#         try:
#             import ctypes
#             hwnd = pygame.display.get_wm_info()["window"]
#
#             GWL_EXSTYLE       = -20
#             WS_EX_LAYERED     = 0x00080000
#             WS_EX_TRANSPARENT = 0x00000020
#             WS_EX_TOOLWINDOW  = 0x00000080
#             HWND_TOPMOST      = -1
#             SWP_NOMOVE        = 0x0002
#             SWP_NOSIZE        = 0x0001
#             LWA_COLORKEY      = 0x1
#
#             ctypes.windll.user32.SetWindowPos(
#                 hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
#             )
#             style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
#             ctypes.windll.user32.SetWindowLongW(
#                 hwnd, GWL_EXSTYLE,
#                 style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
#             )
#             ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, LWA_COLORKEY)
#             print("   [Avatar] Always-on-top overlay active.")
#         except Exception as e:
#             print(f"   [Avatar] Window setup: {e}")
#
#         # Load sprites
#         idle_frames    = load_frames(IDLE_SPRITE)
#         talking_frames = load_frames(TALKING_SPRITE)
#
#         if not idle_frames:
#             print("   [Avatar] No frames loaded — exiting.")
#             return
#         if not talking_frames:
#             talking_frames = idle_frames
#
#         clock       = pygame.time.Clock()
#         frame_index = 0
#         start_time  = time.time()
#         self.running = True
#         print("   [Avatar] Running.")
#
#         while self.running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False
#
#             # Float effect
#             elapsed = time.time() - start_time
#             float_y = int(math.sin(elapsed * FLOAT_SPEED * 2 * math.pi) * FLOAT_AMPLITUDE)
#
#             frames = talking_frames if self.is_talking else idle_frames
#
#             screen.fill((0, 0, 0, 0))
#             screen.blit(frames[frame_index], (0, float_y + int(FLOAT_AMPLITUDE)))
#             pygame.display.flip()
#
#             frame_index = (frame_index + 1) % len(frames)
#             clock.tick(FPS)
#
#         pygame.display.quit()
#
#     def start(self):
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()
#         print("   [Avatar] Started.")
#
#     def stop(self):
#         self.running = False
#
#
# # Global instance
# avatar = KiraAvatar()
#
#
# if __name__ == "__main__":
#     print("Testing avatar — Ctrl+C to quit")
#     pygame.mixer.pre_init(44100, -16, 2, 2048)
#     pygame.init()
#     avatar.start()
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         avatar.stop()













# # avatar.py - Kira avatar overlay
# # Sprite sheet animation, black background removed
# # Always on top, transparent, click-through
#
# import pygame
# import threading
# import time
# import os
# import math
# import numpy as np
#
# # ── Config ────────────────────────────────────────────────────────────────────
# IDLE_SPRITE    = "idle.png"
# TALKING_SPRITE = "talking.png"
#
# # Frame grid
# IDLE_COLS    = 9
# TALKING_COLS = 8
# ROWS         = 8
# FRAME_W      = 400
# FRAME_H      = 225
#
# # Display size — keep 16:9 ratio
# DISPLAY_W = 400
# DISPLAY_H = 225
#
# FPS       = 12   # playback speed
#
# # Black removal — only pure black becomes transparent
# BLACK_THRESHOLD = 30
#
# # Float effect
# FLOAT_AMPLITUDE = 0
# FLOAT_SPEED     = 1.2
#
#
# def remove_black(surface: pygame.Surface) -> pygame.Surface:
#     """Replace black pixels with transparency."""
#     surface = surface.convert_alpha()
#     arr     = pygame.surfarray.pixels3d(surface)
#     alpha   = pygame.surfarray.pixels_alpha(surface)
#     mask = (
#         (arr[:, :, 0] < BLACK_THRESHOLD) &
#         (arr[:, :, 1] < BLACK_THRESHOLD) &
#         (arr[:, :, 2] < BLACK_THRESHOLD)
#     )
#     alpha[mask] = 0
#     del arr, alpha
#     return surface
#
#
# def load_frames(path: str, cols: int = 9) -> list:
#     """Load and slice sprite sheet into individual frames."""
#     if not os.path.exists(path):
#         print(f"   [Avatar] File not found: {path}")
#         return []
#
#     sheet  = pygame.image.load(path).convert_alpha()
#     frames = []
#     for row in range(ROWS):
#         for col in range(cols):
#             rect  = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
#             frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
#             frame.blit(sheet, (0, 0), rect)
#             frame = remove_black(frame)
#             frame = pygame.transform.smoothscale(frame, (DISPLAY_W, DISPLAY_H))
#             frames.append(frame)
#
#     print(f"   [Avatar] Loaded {len(frames)} frames from {path}")
#     return frames
#
#
# class KiraAvatar:
#     def __init__(self):
#         self.is_talking = False
#         self.running    = False
#         self._thread    = None
#
#     def set_talking(self, talking: bool):
#         self.is_talking = talking
#
#     def _run(self):
#         pygame.display.init()
#
#         info   = pygame.display.Info()
#         sw, sh = info.current_w, info.current_h
#         os.environ["SDL_VIDEO_WINDOW_POS"] = f"{sw - DISPLAY_W - 20},{sh - DISPLAY_H - 80}"
#
#         screen = pygame.display.set_mode(
#             (DISPLAY_W, DISPLAY_H + int(FLOAT_AMPLITUDE * 2)),
#             pygame.NOFRAME | pygame.SRCALPHA
#         )
#         pygame.display.set_caption("Kira")
#
#         # Windows: always on top + transparent + click-through
#         try:
#             import ctypes
#             hwnd = pygame.display.get_wm_info()["window"]
#
#             GWL_EXSTYLE       = -20
#             WS_EX_LAYERED     = 0x00080000
#             WS_EX_TRANSPARENT = 0x00000020
#             WS_EX_TOOLWINDOW  = 0x00000080
#             HWND_TOPMOST      = -1
#             SWP_NOMOVE        = 0x0002
#             SWP_NOSIZE        = 0x0001
#             LWA_COLORKEY      = 0x1
#
#             ctypes.windll.user32.SetWindowPos(
#                 hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
#             )
#             style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
#             ctypes.windll.user32.SetWindowLongW(
#                 hwnd, GWL_EXSTYLE,
#                 style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
#             )
#             ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, LWA_COLORKEY)
#             print("   [Avatar] Always-on-top overlay active.")
#         except Exception as e:
#             print(f"   [Avatar] Window setup: {e}")
#
#         # Load sprites
#         idle_frames    = load_frames(IDLE_SPRITE, cols=IDLE_COLS)
#         talking_frames = load_frames(TALKING_SPRITE, cols=TALKING_COLS)
#
#         if not idle_frames:
#             print("   [Avatar] No frames loaded — exiting.")
#             return
#         if not talking_frames:
#             talking_frames = idle_frames
#
#         clock       = pygame.time.Clock()
#         frame_index = 0
#         start_time  = time.time()
#         self.running = True
#         print("   [Avatar] Running.")
#
#         while self.running:
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     self.running = False
#
#             # Float effect
#             elapsed = time.time() - start_time
#             float_y = int(math.sin(elapsed * FLOAT_SPEED * 2 * math.pi) * FLOAT_AMPLITUDE)
#
#             frames = talking_frames if self.is_talking else idle_frames
#
#             # Reset frame index if switching animations with different lengths
#             if frame_index >= len(frames):
#                 frame_index = 0
#
#             screen.fill((0, 0, 0, 0))
#             screen.blit(frames[frame_index], (0, float_y + int(FLOAT_AMPLITUDE)))
#             pygame.display.flip()
#
#             frame_index = (frame_index + 1) % len(frames)
#             clock.tick(FPS)
#
#         pygame.display.quit()
#
#     def start(self):
#         self._thread = threading.Thread(target=self._run, daemon=True)
#         self._thread.start()
#         print("   [Avatar] Started.")
#
#     def stop(self):
#         self.running = False
#
#
# # Global instance
# avatar = KiraAvatar()
#
#
# if __name__ == "__main__":
#     print("Testing avatar — Ctrl+C to quit")
#     pygame.mixer.pre_init(44100, -16, 2, 2048)
#     pygame.init()
#     avatar.start()
#     try:
#         while True:
#             time.sleep(1)
#     except KeyboardInterrupt:
#         avatar.stop()








# avatar.py - Kira avatar overlay
# Sprite sheet animation, black background removed
# Always on top, transparent, click-through

import pygame
import threading
import time
import os
import math
import ctypes

# ── Config ────────────────────────────────────────────────────────────────────
IDLE_SPRITE    = "idle.png"
TALKING_SPRITE = "talking.png"

IDLE_COLS      = 9
TALKING_COLS   = 8
ROWS           = 7
FRAME_W        = 400
FRAME_H        = 225

IDLE_FRAMES    = 63   # skip last empty frame
TALKING_FRAMES = 64

DISPLAY_W      = 400
DISPLAY_H      = 225

FPS            = 12
BLACK_THRESHOLD = 30
FLOAT_AMPLITUDE = 0  # set to 0 to disable bouncing


def remove_black(surface: pygame.Surface) -> pygame.Surface:
    surface = surface.convert_alpha()
    arr     = pygame.surfarray.pixels3d(surface)
    alpha   = pygame.surfarray.pixels_alpha(surface)
    mask = (
        (arr[:, :, 0] < BLACK_THRESHOLD) &
        (arr[:, :, 1] < BLACK_THRESHOLD) &
        (arr[:, :, 2] < BLACK_THRESHOLD)
    )
    alpha[mask] = 0
    del arr, alpha
    return surface


def load_frames(path: str, cols: int = 9, max_frames: int = None) -> list:
    if not os.path.exists(path):
        print(f"   [Avatar] File not found: {path}")
        return []
    sheet  = pygame.image.load(path).convert_alpha()
    frames = []
    for row in range(ROWS):
        for col in range(cols):
            rect  = pygame.Rect(col * FRAME_W, row * FRAME_H, FRAME_W, FRAME_H)
            frame = pygame.Surface((FRAME_W, FRAME_H), pygame.SRCALPHA)
            frame.blit(sheet, (0, 0), rect)
            frame = remove_black(frame)
            frame = pygame.transform.smoothscale(frame, (DISPLAY_W, DISPLAY_H))
            frames.append(frame)
    if max_frames:
        frames = frames[:max_frames]
    print(f"   [Avatar] Loaded {len(frames)} frames from {path}")
    return frames


def force_topmost(hwnd):
    """Force window to stay on top — call periodically."""
    try:
        HWND_TOPMOST = -1
        SWP_NOMOVE   = 0x0002
        SWP_NOSIZE   = 0x0001
        ctypes.windll.user32.SetWindowPos(
            hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
        )
    except Exception:
        pass


class KiraAvatar:
    def __init__(self):
        self.is_talking = False
        self.running    = False
        self._thread    = None

    def set_talking(self, talking: bool):
        self.is_talking = talking

    def _run(self):
        pygame.display.init()

        info   = pygame.display.Info()
        sw, sh = info.current_w, info.current_h
        os.environ["SDL_VIDEO_WINDOW_POS"] = f"{sw - DISPLAY_W - 20},{sh - DISPLAY_H - 80}"

        screen = pygame.display.set_mode(
            (DISPLAY_W, DISPLAY_H + max(1, int(FLOAT_AMPLITUDE * 2))),
            pygame.NOFRAME | pygame.SRCALPHA
        )
        pygame.display.set_caption("Kira")

        # Windows: always on top + transparent + click-through
        hwnd = None
        try:
            hwnd = pygame.display.get_wm_info()["window"]

            GWL_EXSTYLE       = -20
            WS_EX_LAYERED     = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020
            WS_EX_TOOLWINDOW  = 0x00000080
            HWND_TOPMOST      = -1
            SWP_NOMOVE        = 0x0002
            SWP_NOSIZE        = 0x0001
            LWA_COLORKEY      = 0x1

            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
            )
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            ctypes.windll.user32.SetWindowLongW(
                hwnd, GWL_EXSTYLE,
                style | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW
            )
            ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, LWA_COLORKEY)
            print("   [Avatar] Always-on-top overlay active.")
        except Exception as e:
            print(f"   [Avatar] Window setup: {e}")

        # Load sprites
        idle_frames    = load_frames(IDLE_SPRITE,    cols=IDLE_COLS,    max_frames=IDLE_FRAMES)
        talking_frames = load_frames(TALKING_SPRITE, cols=TALKING_COLS, max_frames=TALKING_FRAMES)

        if not idle_frames:
            print("   [Avatar] No frames — exiting.")
            return
        if not talking_frames:
            talking_frames = idle_frames

        clock        = pygame.time.Clock()
        frame_index  = 0
        start_time   = time.time()
        topmost_tick = 0
        self.running = True
        print("   [Avatar] Running.")

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # Re-assert topmost every 2 seconds
            now = time.time()
            if hwnd and now - topmost_tick > 2.0:
                force_topmost(hwnd)
                topmost_tick = now

            # Float effect
            elapsed = now - start_time
            float_y = int(math.sin(elapsed * 1.2 * 2 * math.pi) * FLOAT_AMPLITUDE) if FLOAT_AMPLITUDE else 0

            # Pick animation — reset index if switching
            frames = talking_frames if self.is_talking else idle_frames
            if frame_index >= len(frames):
                frame_index = 0

            screen.fill((0, 0, 0, 0))
            screen.blit(frames[frame_index], (0, float_y + max(0, int(FLOAT_AMPLITUDE))))
            pygame.display.flip()

            frame_index = (frame_index + 1) % len(frames)
            clock.tick(FPS)

        pygame.display.quit()

    def start(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("   [Avatar] Started.")

    def stop(self):
        self.running = False


# Global instance
avatar = KiraAvatar()


if __name__ == "__main__":
    print("Testing avatar — Ctrl+C to quit")
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.init()
    avatar.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        avatar.stop()