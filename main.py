from PIL import Image, ImageDraw, ImageFilter
import numpy as np


class FullHitsplat:
    def __init__(self, val, background):
        assert isinstance(background, Background)
        assert isinstance(val, int)
        self.subsplats = [HitsplatNumber(int(i)) for i in str(val)]
        self.background = background
        self.image = self.gen_image()

    def gen_numbers(self):
        width = 0
        height = self.subsplats[0].image.height
        for i, subsplat in enumerate(self.subsplats):
            width += subsplat.image.width
            if i < len(self.subsplats) - 1:
                if subsplat.val == 1:
                    width += 1
                else:
                    width += 2
        numbers = Image.new('RGBA', (width, height), (255, 0, 0, 0))

        # Append the number images together
        curr_pos = (0, 0)
        for subsplat in self.subsplats:
            curr_image = subsplat.image
            numbers.paste(curr_image, curr_pos, curr_image)
            curr_pos = (
                curr_pos[0] + curr_image.width + (1 if subsplat.val == 1 else 2),
                curr_pos[1])

        # Apply a shadow effect
        as_arr = np.array(numbers)

        red, green, blue, alpha = as_arr[:, :, 0], as_arr[:, :, 1], as_arr[:, :, 2], as_arr[:, :, 3]
        mask = (red == 255) & (green == 255) & (blue == 255) & (alpha == 255)
        as_arr[:, :, :4][mask] = [0, 0, 0, 255]

        shadows = Image.fromarray(as_arr)
        with_shadows = Image.new('RGBA', (width + 1, height + 1), (255, 0, 0, 0))
        with_shadows.paste(shadows, (1, 1))
        with_shadows.paste(numbers, (0, 0), numbers)
        return with_shadows

    def gen_image(self):
        numbers = self.gen_numbers()
        final_image = self.background.image.convert("RGBA")
        final_image.paste(numbers, (12 - (numbers.width + 1) // 2, 7), numbers)
        return final_image


class HitsplatNumber:
    def __init__(self, val):
        assert isinstance(val, int)
        assert val in range(10)
        self.val = val
        self.image = Image.open(f'resources/{val}.png')


class Background:
    valid_types = {
        'normal': 'hitsplat.png',
        'venom': 'venom.png'
    }

    def __init__(self, background_type):
        assert background_type in self.valid_types.keys()
        self.background_type = background_type
        self.image = Image.open(f'resources/{self.valid_types[background_type]}')


if __name__ == '__main__':
    boaty = FullHitsplat(73, background=Background('venom'))
    boaty.image.show()
