import { searchQuery } from '@SearchTue/api/searchQuery';
import { SearchResults, SingleDoc } from '@SearchTue/components/SearchResults/SingleDoc';
import { LoadingSuspenseSmall } from '@SearchTue/pages/loading';
import SearchIcon from '@mui/icons-material/Search';
import { Box, Button, TextField, Typography } from '@mui/material';
import Alert from '@mui/material/Alert';
import AlertTitle from '@mui/material/AlertTitle';
import { Stack } from '@mui/system';
import React from 'react';
import { useQuery } from 'react-query';

/**
 * Search page
 * @return {React.ReactElement} The Search page.
 */
export default function Search(): React.ReactElement {
  const [searchText, setSearchText] = React.useState('');
  const [searchTextDebounced, setSearchTextDebounced] = React.useState(searchText);
  const { isLoading, isFetching, isRefetching, isError, data, error, refetch } = useQuery<SearchResults | null, Error>(
    ['search'],
    async () => await searchQuery(searchText)
  );

  const handleSearchTextChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTextDebounced(event.currentTarget.value);
  };

  const handleKeyDownChange = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter') {
      setSearchText(searchTextDebounced);
      handleSearchSubmit();
    }
  };

  React.useEffect(() => {
    const query = window.location.search.split('=')[1];
    const decodedQuery = decodeURIComponent(query);
    setSearchText(decodedQuery);
    setSearchTextDebounced(decodedQuery);
  }, []);

  const handleSearchSubmit = async () => {
    setSearchText(searchTextDebounced);
  };

  React.useEffect(() => {
    window.history.replaceState(null, '', `/search?q=${encodeURIComponent(searchTextDebounced)}`);
    refetch();
  }, [searchText]);

  return (
    <>
      <Box component={'div'} sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
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
              value={searchTextDebounced}
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

        <Stack direction={'column'} justifyContent={'center'} alignItems={'center'} gap={1}>
          {(isLoading || isFetching || isRefetching) && <LoadingSuspenseSmall />}
          {(isError || data === undefined || data === null) && (
            <Alert severity="error">
              <AlertTitle>Fehler </AlertTitle>
              Es ist ein Fehler aufgetreten. Bitte versuchen Sie es später nocheinmal
              <Typography variant="caption" data-tid="error">
                {error?.message}
              </Typography>
            </Alert>
          )}
          {data !== undefined && data !== null && data.results.length === 0 && <NothingFound />}
        </Stack>

        <Box component={'div'} sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
          {!isLoading &&
            !isFetching &&
            !isRefetching &&
            data !== undefined &&
            data !== null &&
            data.results.map((doc, index) => <SingleDoc doc={doc} key={`${doc.id}-${index}`} />)}
        </Box>
      </Box>
    </>
  );
}

const NothingFound = () => <Alert severity="info">Es wurden keine Ergebnisse gefunden</Alert>;
