import { SearchResults, SingleDoc } from '@SearchTue/components/searchResults/singleDoc';
import SearchIcon from '@mui/icons-material/Search';
import { Box, Button, TextField, Typography } from '@mui/material';
import { Stack } from '@mui/system';
import axios from 'axios';
import React from 'react';

/**
 * Search page
 * @return {React.ReactElement} The Search page.
 */
export default function Search(): React.ReactElement {
  const [searchText, setSearchText] = React.useState('');

  const handleSearchTextChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // debounce the search
    const value = event.target.value;
    const timeout = setTimeout(() => {
      setSearchText(value);
    }, 500);
    return () => clearTimeout(timeout);
  };

  const handleKeyDownChange = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      handleSearchSubmit();
    }
  };

  const [searchResults, setSearchResults] = React.useState<SearchResults | null>(null);

  React.useEffect(() => {
    // set search text
    const query = window.location.search.split('=')[1];
    setSearchText(query);
  }, []);

  const handleSearchSubmit = () => {
    if (searchText === '') {
      return;
    }
    axios
      .get(`${import.meta.env.VITE_API_URL}/search?q=${searchText}`)
      .then((response) => {
        console.log(response.data);
        setSearchResults(response.data);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  React.useEffect(() => {
    handleSearchSubmit();
  }, [searchText]);

  return (
    <>
      <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Stack direction={{ xs: 'column', md: 'row' }} gap={3}>
          <Typography variant="h3" data-tid="title">
            Suchergebnisse
          </Typography>
          <Stack sx={{ display: 'flex', flexDirection: 'row' }}>
            <TextField
              label="Suche"
              className="MainSearchBar"
              variant="outlined"
              sx={{ minWidth: { xs: '250px', md: '350px' } }}
              onChange={handleSearchTextChange}
              onKeyDown={handleKeyDownChange}
              value={searchText}
            />
            <Button
              variant="contained"
              color="primary"
              onClick={handleSearchSubmit}
              sx={{ px: 3, borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
              startIcon={<SearchIcon />}
            >
              Suche
            </Button>
          </Stack>
        </Stack>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {searchResults !== null && searchResults.results !== undefined && searchResults.results.map((doc, index) => <SingleDoc doc={doc} key={`${doc.id}-${index}`} />)}
        </Box>
      </Box>
    </>
  );
}
