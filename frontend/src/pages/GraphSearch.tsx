import { Searchbar } from '@SearchTue/components/GraphSearch/Searchbar';
import { ResultTile } from '@SearchTue/components/SearchResults/ResultTile';
import { SearchResults } from '@SearchTue/components/SearchResults/SingleDoc';
import Box from '@mui/material/Box';
import axios from 'axios';
import { config } from 'dotenv';
import React from 'react';

const SearchResultBox = ({ searchText, searchResults }: { searchText: string | null; searchResults: SearchResults | null }) => {
  if (!searchText || searchText === '') {
    return null;
  }
  return (
    <div style={{ width: '100%', display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', margin: '50px auto 0 auto' }}>
      {searchResults !== null && searchResults?.results.length > 0 && searchResults?.results.slice(0, 3).map((doc, index) => <ResultTile key={index} doc={doc} />)}
    </div>
  );
};

/**
 * GraphSearch Page
 *
 * @return {React.ReactElement} GraphSearch Page
 */
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
      .get(`${import.meta.env.VITE_API_URL}/api/search?q=${searchText}`)
      .then((response) => {
        console.log('Search query response:', response);
        setSearchResults(response.data);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <>
      <Box component="div" sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', margin: '20px 0' }}>
        <Searchbar searchText={searchText} onSearchTextChange={setSearchText} onSearchSubmit={handleSearchSubmit} />
        <SearchResultBox searchText={searchText} searchResults={searchResults} />
      </Box>
    </>
  );
}
