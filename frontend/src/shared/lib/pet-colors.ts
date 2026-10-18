const PET_COLOR_SATURATION = 68;
const PET_COLOR_LIGHTNESS = 38;

export const createPetColorMap = (petIds: string[]) => {
  const uniqueIds = [...new Set(petIds)].sort();

  return new Map(
    uniqueIds.map((petId, index) => [
      petId,
      `hsl(${Math.round((index * 360) / uniqueIds.length)} ${PET_COLOR_SATURATION}% ${PET_COLOR_LIGHTNESS}%)`,
    ]),
  );
};
