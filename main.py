from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from enum import Flag, auto


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
        shadows = replace_white_with_black(numbers)
        with_shadows = Image.new('RGBA', (width + 1, height + 1), (255, 0, 0, 0))
        with_shadows.paste(shadows, (1, 1))
        with_shadows.paste(numbers, (0, 0), numbers)
        return with_shadows

    def gen_image(self):
        numbers = self.gen_numbers()
        final_image = self.background.image.convert("RGBA")
        final_image.paste(numbers, (12 - (numbers.width + 1) // 2, 7), numbers)
        return final_image


def replace_white_with_black(image):
    as_arr = np.array(image)

    red, green, blue, alpha = as_arr[:, :, 0], as_arr[:, :, 1], as_arr[:, :, 2], as_arr[:, :, 3]
    mask = (red == 255) & (green == 255) & (blue == 255) & (alpha == 255)
    as_arr[:, :, :4][mask] = [0, 0, 0, 255]

    return Image.fromarray(as_arr)


class HitsplatNumber:
    def __init__(self, val):
        assert isinstance(val, int)
        assert val in range(10)
        self.val = val
        self.image = Image.open(f'resources/{val}.png').convert('RGBA')


class Snakeling:
    def __init__(self, val):
        assert isinstance(val, int)
        assert val in range(0, 7)
        self.val = val
        self.image = self.gen_image()

    def gen_image(self):
        snakeling = Image.open(f'resources/Pet_snakeling.png').convert('RGBA')
        number = HitsplatNumber(self.val).image
        number = scale(number, 2)
        final = Image.new('RGBA', (snakeling.width + number.width, snakeling.height), (255, 0, 0, 0))
        final.paste(snakeling, (0, 0))
        final.paste(number, (19, 7), number)
        return final


def scale(image, scaling):
    assert isinstance(image, Image.Image)
    assert isinstance(scaling, int)
    return image.resize((image.width * scaling, image.height * scaling), Image.BOX)


class Background:
    valid_types = {
        'normal': 'hitsplat.png',
        'venom': 'venom.png'
    }

    def __init__(self, background_type):
        assert background_type in self.valid_types.keys()
        self.background_type = background_type
        self.image = Image.open(f'resources/{self.valid_types[background_type]}').convert('RGBA')


class ImageType(Flag):
    DARK = auto()
    PRAY = auto()
    ATTACK = auto()


class Phase:
    def __init__(self, name, num_attack, num_venom, num_snakeling):
        self.name = name
        self.num_attack = num_attack
        self.num_venom = num_venom
        self.num_snakeling = num_snakeling
        self.images = {
            ImageType(0): Image.open(self.get_file(ImageType(0))).convert('RGBA'),
            ImageType.DARK: Image.open(self.get_file(ImageType.DARK)).convert('RGBA'),
            ImageType.PRAY: Image.open(self.get_file(ImageType.PRAY)).convert('RGBA'),
            ImageType.DARK | ImageType.PRAY: Image.open(self.get_file(ImageType.DARK | ImageType.PRAY)).convert('RGBA'),
        }
        self.create_attack_images()

    def get_file(self, imageType):
        suffix = ''
        if ImageType.DARK & imageType:
            suffix += '-dark'
        if ImageType.PRAY & imageType:
            suffix += '-pray'
        if ImageType.ATTACK & imageType:
            suffix += '-attack'
        return f'phases/{self.name}{suffix}.png'

    def create_attack_images(self):
        if self.num_attack > 0:
            attack_data = scale(FullHitsplat(self.num_attack, Background('normal')).image, 2)
        else:
            attack_data = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        if self.num_venom > 0:
            venom_data = scale(FullHitsplat(self.num_venom, Background('venom')).image, 2)
        else:
            venom_data = Image.new('RGBA', (1, 1), (255, 0, 0, 0))
        if self.num_snakeling > 0:
            snakeling_data = Snakeling(self.num_snakeling).image
        else:
            snakeling_data = Image.new('RGBA', (1, 1), (255, 0, 0, 0))

        attack_data_height_offset = 250
        attack_data_width_center = 130
        attack_data_width_spacing = 75
        snakeling_height_offset = attack_data_height_offset + 7
        attack_images = dict()
        for image_type, image in self.images.items():
            assert isinstance(image, Image.Image)
            new_type = image_type | ImageType.ATTACK
            if new_type in self.images:
                continue
            attack_image = image.copy().convert('RGBA')
            attack_image.paste(
                attack_data,
                (attack_data_width_center - attack_data_width_spacing, attack_data_height_offset),
                attack_data)
            attack_image.paste(
                venom_data,
                (attack_data_width_center, attack_data_height_offset),
                venom_data)
            if image_type & ImageType.DARK:
                attack_image.paste(
                    snakeling_data,
                    (attack_data_width_center + attack_data_width_spacing, snakeling_height_offset),
                    snakeling_data)
            else:
                black_text_snakeling_data = replace_white_with_black(snakeling_data)
                attack_image.paste(
                    black_text_snakeling_data,
                    (attack_data_width_center + attack_data_width_spacing, snakeling_height_offset),
                    black_text_snakeling_data)
            attack_images[new_type] = attack_image

        self.images.update(attack_images)

    def write_attack_to_file(self):
        for image_type, image in self.images.items():
            if not (ImageType.ATTACK & image_type):
                continue
            image.save(self.get_file(image_type))


def create_all_attack_phases():
    attacks = [
        # (phase name, number of attacks, number of venom cloud attacks, number of snakelings spawned)
        ('start-1', 5, 4, 0),

        ('magma-1', 5, 4, 0),
        ('magma-2', 2, 0, 0),
        ('magma-3', 4, 0, 0),

        ('magma_a-1', 5, 4, 0),
        ('magma_a-2', 2, 0, 0),
        ('magma_a-3', 4, 0, 0),
        ('magma_a-4', 5, 2, 4),
        ('magma_a-5', 2, 0, 0),
        ('magma_a-6', 5, 0, 0),
        ('magma_a-7', 0, 3, 4),
        ('magma_a-8', 5, 2, 3),
        ('magma_a-9', 10, 4, 0),
        ('magma_a-10', 2, 0, 0),

        ('magma_b-1', 5, 4, 0),
        ('magma_b-2', 2, 0, 0),
        ('magma_b-3', 4, 0, 0),
        ('magma_b-4', 0, 3, 4),
        ('magma_b-5', 5, 2, 4),
        ('magma_b-6', 2, 0, 0),
        ('magma_b-7', 5, 0, 0),
        ('magma_b-8', 5, 2, 3),
        ('magma_b-9', 10, 4, 0),
        ('magma_b-10', 2, 0, 0),

        ('normal-1', 5, 4, 0),
        ('normal-2', 5, 0, 3),
        ('normal-3', 2, 3, 3),
        ('normal-4', 5, 0, 0),
        ('normal-5', 5, 0, 0),
        ('normal-6', 5, 0, 0),
        ('normal-7', 0, 3, 3),
        ('normal-8', 5, 0, 0),
        ('normal-9', 5, 2, 3),
        ('normal-10', 10, 0, 0),
        ('normal-11', 0, 0, 4),

        ('tanz-1', 5, 4, 0),
        ('tanz-2', 6, 0, 4),
        ('tanz-3', 4, 2, 0),
        ('tanz-4', 4, 0, 4),
        ('tanz-5', 2, 2, 0),
        ('tanz-6', 4, 0, 0),
        ('tanz-7', 0, 3, 6),
        ('tanz-8', 5, 4, 0),
        ('tanz-9', 5, 0, 0),
        ('tanz-10', 4, 3, 0),
        ('tanz-11', 8, 0, 0),
        ('tanz-12', 0, 0, 4),
    ]
    for attack in attacks:
        Phase(*attack).write_attack_to_file()


if __name__ == '__main__':
    create_all_attack_phases()
