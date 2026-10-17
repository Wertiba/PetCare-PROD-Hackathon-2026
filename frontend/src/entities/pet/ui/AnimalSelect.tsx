'use client';

import {
  Combobox,
  type ComboboxOption,
} from '@src/shared/ui';
import { useEffect, useState } from 'react';

import { useGetAnimalsQuery } from '../model';

const ANIMALS_PAGE_SIZE = 20;
const SEARCH_DEBOUNCE_MS = 300;

interface AnimalSelectProps {
  value: string;
  onChange: (animalId: string) => void;
  onBlur?: () => void;
  error?: string;
}

export function AnimalSelect({
  value,
  onChange,
  onBlur,
  error,
}: AnimalSelectProps) {
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

  const { data, isFetching } = useGetAnimalsQuery({
    page: 0,
    size: ANIMALS_PAGE_SIZE,
    q: debouncedSearch,
  });

  const options: ComboboxOption[] = (data?.items ?? []).map(
    (animal) => ({ value: animal.id, label: animal.name }),
  );

  return (
    <Combobox
      label="Вид"
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
