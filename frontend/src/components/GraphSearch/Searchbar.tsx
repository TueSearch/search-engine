import SearchIcon from '@mui/icons-material/Search';
import InputAdornment from '@mui/material/InputAdornment';
import { Box, IconButton, TextField } from '@mui/material';
import React from 'react';

interface SearchbarProps {
  searchText: string;
  onSearchTextChange: (searchText: string) => void;
  onSearchSubmit: () => void;
}

export const Searchbar = ({ searchText, onSearchTextChange, onSearchSubmit }: SearchbarProps) => {

  const handleSearchSubmit = () => {
    onSearchSubmit();
  };

  return (
    <TextField
      style={{ minWidth: '40%' }}
      label="Suche"
      variant="outlined"
      value={searchText}
      onChange={(e) => onSearchTextChange(e.target.value)}
      sx={{ mr: -1, minWidth: '350px' }}
      InputProps={{
        endAdornment: (
          <InputAdornment position="end">
            <IconButton onClick={handleSearchSubmit}>
              <SearchIcon />
            </IconButton>
          </InputAdornment>
        ),
        onKeyDown: (e) => {
          if (e.key === 'Enter') {
            handleSearchSubmit();
          }
        },
      }}
    />
  );
};
