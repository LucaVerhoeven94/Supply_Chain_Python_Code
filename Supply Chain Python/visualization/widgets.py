import pygame
import math
from typing import Tuple

class StatusColors:
    MAP = {
        "Running": (46, 204, 113),           # Bright Green
        "Starved": (230, 126, 34),           # Orange
        "Blocked": (231, 76, 60),            # Red
        "Completed": (52, 152, 219),         # Soft Blue
        "Suspended": (149, 165, 166),         # Grey
        "Idle": (149, 165, 166),              # Grey
        
        # --- THE ADDITION: Map the maintenance text status to an Orange alert color ---
        "Under Maintenance": (230, 126, 34)  
    }

class HelperGraphics:
    """Helper class to mathematically draw sharp flow arrowheads on any line."""
    @staticmethod
    def draw_arrow(screen: pygame.Surface, start: Tuple[int, int], end: Tuple[int, int], color: Tuple[int, int, int], size: int = 12):
        # Calculate the angle of the line from start to end
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        angle = math.atan2(dy, dx)
        
        # Calculate the tip position of the arrow (moved back slightly from the exact end point)
        tip_x = end[0]
        tip_y = end[1]
        
        # Calculate the two base corners of the triangle arrow head
        left_wing_x = tip_x - size * math.cos(angle - math.pi / 6)
        left_wing_y = tip_y - size * math.sin(angle - math.pi / 6)
        
        right_wing_x = tip_x - size * math.cos(angle + math.pi / 6)
        right_wing_y = tip_y - size * math.sin(angle + math.pi / 6)
        
        # Draw the filled triangle arrowhead
        pygame.draw.polygon(screen, color, [
            (tip_x, tip_y),
            (left_wing_x, left_wing_y),
            (right_wing_x, right_wing_y)
        ])

class TankWidget:
    @staticmethod
    def draw(screen: pygame.Surface, rect: Tuple[int, int, int, int], name: str, level: float, capacity: float, font: pygame.font.Font, font_bold: pygame.font.Font):
        x, y, w, h = rect
        pct = max(0.0, min(1.0, level / capacity)) if capacity > 0 else 0
        fill_h = pct * h
        
        pygame.draw.rect(screen, (41, 128, 185), (x, y + h - fill_h, w, fill_h))
        pygame.draw.rect(screen, (44, 53, 64), (x, y, w, h), 3)
        pygame.draw.line(screen, (44, 53, 64), (x, y), (x + w, y), 5)
        
        screen.blit(font_bold.render(name, True, (44, 62, 80)), (x, y - 35))
        screen.blit(font.render(f"{level:.1f} / {capacity:.0f} T", True, (70, 85, 105)), (x, y - 18))

class ProcessWidget:
    @staticmethod
    def draw(screen: pygame.Surface, src_rect: Tuple[int, int, int, int], dest_rect: Tuple[int, int, int, int], name: str, status: str, font: pygame.font.Font, font_bold: pygame.font.Font):
        x1, y1, w1, h1 = src_rect
        x2, y2, w2, h2 = dest_rect
        
        padding = 5  # Ensure clean buffer space outside the tank cards
        
        # 1. Determine connection anchor points based on layout orientation
        start_pos = (x1 + w1 + padding, y1 + h1 // 2)
        end_pos = (x2 - padding, y2 + h2 // 2)
        
        if abs(x1 - x2) < 50 and y2 > y1:  # Vertical line going down
            start_pos = (x1 + w1 // 2, y1 + h1 + padding)
            end_pos = (x2 + w2 // 2, y2 - padding)
        elif x1 > x2:                      # Backward line moving right-to-left
            start_pos = (x1 - padding, y1 + h1 // 2)
            end_pos = (x2 + w2 + padding, y2 + h2 // 2)
            
        color = StatusColors.MAP.get(status, (149, 165, 166))
        
        # 2. Draw the continuous pipe line
        pygame.draw.line(screen, color, start_pos, end_pos, 5)
        
        # 3. Draw the arrowhead at the target end of the line
        HelperGraphics.draw_arrow(screen, start_pos, end_pos, color, size=14)
        
        # 4. Draw labels neatly centered in space
        mid_x = (start_pos[0] + end_pos[0]) // 2
        mid_y = (start_pos[1] + end_pos[1]) // 2
        
        if start_pos[1] == end_pos[1]:
            offset_y = -38
            offset_x = -40
        else:
            offset_y = -10
            offset_x = 18
        
        screen.blit(font.render(name, True, (90, 100, 110)), (mid_x + offset_x, mid_y + offset_y))
        screen.blit(font_bold.render(status, True, color), (mid_x + offset_x, mid_y + offset_y + 15))

class TransportWidget:
    @staticmethod
    def draw(screen: pygame.Surface, src_rect: Tuple[int, int, int, int], dest_rect: Tuple[int, int, int, int], name: str, active_trucks: int, font: pygame.font.Font, font_bold: pygame.font.Font):
        x1, y1, w1, h1 = src_rect
        x2, y2, w2, h2 = dest_rect
        
        padding = 5
        
        if x1 < x2:
            start_pos = (x1 + w1 + padding, y1 + h1 // 2)
            end_pos = (x2 - padding, y2 + h2 // 2)
        else:
            start_pos = (x1 - padding, y1 + h1 // 2)
            end_pos = (x2 + w2 + padding, y2 + h2 // 2)
        
        line_color = (170, 178, 185)
        
        # 1. Draw logistics highway path
        pygame.draw.line(screen, line_color, start_pos, end_pos, 3)
        
        # 2. Draw the logistics directional arrowhead
        HelperGraphics.draw_arrow(screen, start_pos, end_pos, line_color, size=11)
        
        mid_x = (start_pos[0] + end_pos[0]) // 2
        mid_y = (start_pos[1] + end_pos[1]) // 2
        
        # 3. Draw truck counter badge
        if active_trucks > 0:
            pygame.draw.rect(screen, (241, 196, 15), (mid_x - 22, mid_y - 12, 45, 24), border_radius=4)
            screen.blit(font_bold.render(f"x{active_trucks}", True, (0, 0, 0)), (mid_x - 9, mid_y - 8))
            
        screen.blit(font.render(name, True, (52, 73, 94)), (mid_x - 50, mid_y - 32))

class SiteWidget:
    @staticmethod
    def draw(screen: pygame.Surface, rect: Tuple[int, int, int, int], name: str, font_title: pygame.font.Font):
        x, y, w, h = rect
        pygame.draw.rect(screen, (235, 242, 250), rect, border_radius=12)
        screen.blit(font_title.render(f"SITE: {name.upper()}", True, (44, 62, 80)), (x + 15, y + 15))