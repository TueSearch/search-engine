import { SearchResults } from '@SearchTue/components/SearchResults/singleDoc';
import { ResultTile } from '@SearchTue/components/SearchResults/ResultTile';
import { Searchbar } from '@SearchTue/components/GraphSearch/SearchBar';
import { Box } from '@mui/material';
import axios from 'axios';
import React from 'react';


function SearchResultBox({ searchText, searchResults }: { searchText: string | null, searchResults: SearchResults | null }) {
  if (!searchText || searchText === '') {
    return null;
  }
  return <Box sx={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', width: '100%', gap: 3, margin: '10% auto 0 auto' }}>
    {searchResults !== null
      && searchResults?.results.length > 0
      && searchResults?.results.slice(0, 3).map((doc, index) => <ResultTile key={index} doc={doc} />)}
  </Box>
}

export default function GraphSearch(): React.ReactElement {
  const [searchText, setSearchText] = React.useState('');

  const [searchResults, setSearchResults] = React.useState<SearchResults | null>(null);

  React.useEffect(() => {
    // set search text
    const query = window.location.search.split('=')[1];
    setSearchText(query);
  }, []);

  const handleSearchSubmit = () => {
    if (!searchText || searchText === '') {
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
        <Searchbar
          searchText={searchText}
          onSearchTextChange={setSearchText}
          onSearchSubmit={handleSearchSubmit}
        />
        <SearchResultBox
          searchText={searchText}
          searchResults={searchResults}
        />
      </Box>
    </>
  );
}
