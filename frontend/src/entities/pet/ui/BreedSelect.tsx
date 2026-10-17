'use client';

import {
  Combobox,
  type ComboboxOption,
} from '@src/shared/ui';
import { useEffect, useState } from 'react';

import { useGetBreedsQuery } from '../model';

const BREEDS_PAGE_SIZE = 20;
const SEARCH_DEBOUNCE_MS = 300;

interface BreedSelectProps {
  animalId: string;
  value: string;
  onChange: (breedId: string) => void;
  onBlur?: () => void;
  error?: string;
}

export function BreedSelect({
  animalId,
  value,
  onChange,
  onBlur,
  error,
}: BreedSelectProps) {
  const [search, setSearch] = useState('');
  const [debouncedSearch, setDebouncedSearch] =
    useState('');
  const [selected, setSelected] =
    useState<ComboboxOption | null>(null);

  useEffect(() => {
    const timer = setTimeout(
      () => setDebouncedSearch(search),
      SEARCH_DEBOUNCE_MS,
    );
    return () => clearTimeout(timer);
  }, [search]);

  const { data, isFetching } = useGetBreedsQuery({
    page: 0,
    size: BREEDS_PAGE_SIZE,
    q: debouncedSearch,
    animalId,
  });

  const options: ComboboxOption[] = (data?.items ?? []).map(
    (breed) => ({ value: breed.id, label: breed.name }),
  );

  return (
    <Combobox
      label="Порода"
      placeholder="Начните вводить название"
      options={options}
      selected={value ? selected : null}
      onSelect={(option) => {
        setSelected(option);
        onChange(option.value);
      }}
      onSearchChange={setSearch}
      onBlur={onBlur}
      isLoading={isFetching}
      error={error}
    />
  );
}
