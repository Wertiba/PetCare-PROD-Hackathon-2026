'use client';

import { useCreatePetMutation } from '@src/features/pet/create-pet';

const PetsList = () => {
  const { mutate } = useCreatePetMutation();

  return (
    <div>
      <h2>PetsList</h2>
      <button
        onClick={() =>
          mutate({
            name: 'pet1name',
            breedId: '3fa85f64-5717-4562-b3fc-2c963f66afa6',
            birthDate: Number(new Date()),
          })
        }
      >
        Create pet
      </button>
    </div>
  );
};

export default PetsList;
