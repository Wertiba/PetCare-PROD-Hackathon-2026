'use client';

import { useId, useState } from 'react';

export interface ComboboxOption {
  value: string;
  label: string;
}

interface ComboboxProps {
  label: string;
  options: ComboboxOption[];
  selected: ComboboxOption | null;
  onSelect: (option: ComboboxOption) => void;
  onSearchChange: (query: string) => void;
  onBlur?: () => void;
  isLoading?: boolean;
  placeholder?: string;
  error?: string;
}

export function Combobox({
  label,
  options,
  selected,
  onSelect,
  onSearchChange,
  onBlur,
  isLoading = false,
  placeholder,
  error,
}: ComboboxProps) {
  const id = useId();
  const listId = `${id}-list`;
  const errorId = `${id}-error`;
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);

  const close = () => {
    setIsOpen(false);
    setQuery('');
    onSearchChange('');
  };

  const select = (option: ComboboxOption) => {
    onSelect(option);
    close();
  };

  const optionId = (index: number) =>
    `${id}-option-${index}`;

  return (
    <div className="relative flex flex-col gap-2">
      <label
        htmlFor={id}
        className="text-sm font-semibold tracking-[0.01em] text-[var(--forest)]"
      >
        {label}
      </label>
      <input
        id={id}
        type="text"
        role="combobox"
        autoComplete="off"
        aria-expanded={isOpen}
        aria-controls={listId}
        aria-autocomplete="list"
        aria-activedescendant={
          isOpen && options.length > 0
            ? optionId(activeIndex)
            : undefined
        }
        aria-invalid={error ? true : undefined}
        aria-describedby={error ? errorId : undefined}
        placeholder={placeholder}
        value={isOpen ? query : (selected?.label ?? '')}
        onFocus={() => setIsOpen(true)}
        onChange={(event) => {
          setIsOpen(true);
          setActiveIndex(0);
          setQuery(event.target.value);
          onSearchChange(event.target.value);
        }}
        onBlur={() => {
          close();
          onBlur?.();
        }}
        onKeyDown={(event) => {
          if (event.key === 'ArrowDown') {
            event.preventDefault();
            setIsOpen(true);
            setActiveIndex((index) =>
              Math.min(index + 1, options.length - 1),
            );
          } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            setActiveIndex((index) =>
              Math.max(index - 1, 0),
            );
          } else if (event.key === 'Enter' && isOpen) {
            event.preventDefault();
            const option = options[activeIndex];
            if (option) select(option);
          } else if (event.key === 'Escape') {
            close();
          }
        }}
        className="w-full rounded-sm border border-[var(--ink)] bg-[var(--white)] px-4 py-3 text-base text-[var(--ink)] placeholder:text-[var(--ink)]/45 focus:bg-[var(--cream)] focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-[var(--forest)]"
      />
      {isOpen ? (
        <ul
          id={listId}
          role="listbox"
          aria-label={label}
          className="absolute top-full z-10 mt-1 max-h-60 w-full overflow-auto rounded-sm border border-[var(--ink)] bg-[var(--white)] shadow-[4px_4px_0_var(--ink)]"
        >
          {options.length === 0 ? (
            <li className="px-4 py-3 text-sm text-[var(--ink)]/60">
              {isLoading
                ? 'Загрузка…'
                : 'Ничего не найдено'}
            </li>
          ) : (
            options.map((option, index) => (
              <li
                key={option.value}
                id={optionId(index)}
                role="option"
                aria-selected={
                  option.value === selected?.value
                }
                // mousedown, not click: click fires after the input's blur has already closed the list
                onMouseDown={(event) => {
                  event.preventDefault();
                  select(option);
                }}
                onMouseEnter={() => setActiveIndex(index)}
                className={`cursor-pointer px-4 py-3 text-base text-[var(--ink)] ${
                  index === activeIndex
                    ? 'bg-[var(--lime)]'
                    : ''
                } ${
                  option.value === selected?.value
                    ? 'font-bold'
                    : ''
                }`}
              >
                {option.label}
              </li>
            ))
          )}
        </ul>
      ) : null}
      {error ? (
        <span
          id={errorId}
          role="alert"
          className="text-sm text-red-700"
        >
          {error}
        </span>
      ) : null}
    </div>
  );
}
