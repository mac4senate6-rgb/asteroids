import pygame

VECTOR_GLYPHS = {  # Store the vector drawing instructions for each character.

    "A": [  # Define the letter A.
        [(0, 0), (0, 4), (2, 7), (4, 4), (4, 0)],  # Draw the outer shape.
        [(0, 3), (4, 3)],  # Draw the crossbar.
    ],

    "S": [  # Define the letter S.
        [(0, 1), (1, 0), (3, 0), (4, 1), (4, 3),
         (3, 4), (1, 4), (0, 5), (0, 6), (1, 7),
         (3, 7), (4, 6)],  # Draw the continuous S-shaped stroke.
    ],

    "T": [  # Define the letter T.
        [(2, 0), (2, 7)],  # Draw the vertical stem.
        [(0, 7), (4, 7)],  # Draw the horizontal top.
    ],

    "E": [  # Define the letter E.
        [(4, 0), (0, 0), (0, 7), (4, 7)],  # Draw the lower, left, and upper edges.
        [(0, 3.5), (3, 3.5)],  # Draw the middle horizontal stroke.
    ],

    "R": [  # Define the letter R.
        [(0, 0), (0, 7), (3, 7), (4, 6),
         (4, 4), (3, 3), (0, 3)],  # Draw the upright stem and upper loop.
        [(2, 3), (4, 0)],  # Draw the diagonal leg.
    ],

    "O": [  # Define the letter O.
        [(0, 1), (0, 6), (1, 7), (3, 7),
         (4, 6), (4, 1), (3, 0), (1, 0),
         (0, 1)],  # Draw the complete closed-looking outline.
    ],

    "I": [  # Define the letter I.
        [(2, 0), (2, 7)],  # Draw the vertical stem.
        [(0, 0), (4, 0)],  # Draw the bottom horizontal stroke.
        [(0, 7), (4, 7)],  # Draw the top horizontal stroke.
    ],

    "D": [  # Define the letter D.
        [(0, 0), (0, 7), (3, 7), (4, 6),
         (4, 1), (3, 0), (0, 0)],  # Draw the complete D-shaped outline.
    ],

    "1": [  # Define the digit 1.
        [(1, 5), (2, 7), (2, 0)],  # Draw the upright numeral.
        [(0, 0), (4, 0)],  # Draw its bottom base.
    ],

    "9": [  # Define the digit 9.
        [(4, 0), (4, 7), (0, 7),
         (0, 4), (4, 4)],  # Draw the digit's main outline.
    ],

    "7": [  # Define the digit 7.
        [(0, 7), (4, 7), (1, 0)],  # Draw the top bar and descending diagonal.
    ],

}

def draw_vector_title(screen: pygame.Surface, text: str, center_x: int, center_y: int) -> None:
    glyph_width = 4
    glyph_height = 7
    target_height = 64
    scale = target_height / glyph_height
    letter_spacing = 1
    stroke_width = 3

    char_width = (len(text) * glyph_width) + ((len(text) - 1) * letter_spacing)  # Add all character widths and the gaps between them.
    total_width = char_width * scale  # Convert the complete title width from vector units into pixels.

    start_x = center_x - total_width / 2
    start_y = center_y - target_height / 2

    for character_index, character in enumerate(text):
        strokes = VECTOR_GLYPHS[character]

        for stroke in strokes:

            points = []

            for x,y in stroke:
                screen_x = round(start_x + (character_index * (glyph_width + letter_spacing) + x) * scale)
                screen_y = round(start_y + (glyph_height - y) * scale)
                points.append([screen_x, screen_y])

            pygame.draw.lines(screen, (255, 255, 255), False, points, stroke_width)



