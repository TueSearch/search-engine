import { SearchResults, SingleDoc } from '@SearchTue/components/searchResults/singleDoc';
import { Box, Typography } from '@mui/material';
import axios from 'axios';
import { set } from 'date-fns';
import React from 'react';

/**
 * Search page
 * @return {React.ReactElement} The Search page.
 */
export default function Search(): React.ReactElement {
  const [searchText, setSearchText] = React.useState('');

  const [searchResults, setSearchResults] = React.useState<SearchResults | null>(null);

  React.useEffect(() => {
    // set search text
    const query = window.location.search.split('=')[1];
    setSearchText(query);
  }, []);

  React.useEffect(() => {
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
  }, [searchText]);

  return (
    <>
      <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
        <Typography variant="h3" data-tid="title">
          Suchergebnisse
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {searchResults !== null && searchResults.results !== undefined && searchResults.results.map((doc) => <SingleDoc doc={doc} key={doc.id} />)}
        </Box>
      </Box>
    </>
  );
}
