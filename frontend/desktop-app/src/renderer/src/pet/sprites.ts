import axolotlAwake from '../../../images/axolotl-awake.svg';
import axolotlSleeping from '../../../images/axolotl-sleeping.svg';
import catAwake from '../../../images/cat-awake.svg';
import catSleeping from '../../../images/cat-sleeping.svg';
import dogAwake from '../../../images/dog-awake.svg';
import dogSleeping from '../../../images/dog-sleeping.svg';
import {
  SPRITE_ANIMALS,
  type SpriteAnimal,
} from '../../../shared/config';

interface Sprite {
  sleeping: string;
  awake: string;
}

const sprites: Record<SpriteAnimal, Sprite> = {
  Кошка: { sleeping: catSleeping, awake: catAwake },
  Собака: { sleeping: dogSleeping, awake: dogAwake },
  Аксолотль: {
    sleeping: axolotlSleeping,
    awake: axolotlAwake,
  },
};

const isSpriteAnimal = (
  name: string,
): name is SpriteAnimal => name in sprites;

/** Unknown species (or none yet) sleep as the first sprite, never invisible. */
export const spriteFor = (animalName: string | null) =>
  sprites[
    animalName && isSpriteAnimal(animalName)
      ? animalName
      : SPRITE_ANIMALS[0]
  ];
