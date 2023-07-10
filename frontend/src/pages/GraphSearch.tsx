import { SearchResults, SingleDoc } from '@SearchTue/components/searchResults/singleDoc';
import { ResultTile } from '@SearchTue/components/searchResults/ResultTile';
import { Box, Button, TextField } from '@mui/material';
import { Graph } from '@SearchTue/components/LinkGraph/Graph';
import SearchIcon from '@mui/icons-material/Search';
import axios from 'axios';
import React from 'react';

/**
 * Search page
 * @return {React.ReactElement} The Search page.
 */
export default function GraphSearch(): React.ReactElement {
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

  return (
    <>
      <Box sx={{ display: 'flex', flexDirection: 'column', width: '100%', alignItems: 'center', margin: '20px 0' }}>
        <Box sx={{ display: 'flex', flexDirection: 'row'}}>
          <TextField label="Suche" variant="outlined" sx={{ mr: -1, minWidth: '350px' }} />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSearchSubmit}
            sx={{ px: 3, borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
            startIcon={<SearchIcon />}
          ></Button>
        </Box>
      </Box>
      <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%', gap: 3, margin: '10% auto 0 auto' }}>
        {searchResults !== null && searchResults?.results.length > 0 && searchResults?.results.slice(0, 3).map((doc) => <ResultTile doc={doc} />)}
      </Box>
    </>
  );
}
