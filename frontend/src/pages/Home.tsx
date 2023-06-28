import SearchTueLogo from '@SearchTue/assets/images/logo.svg';
import SearchIcon from '@mui/icons-material/Search';
import { Box, Button, TextField } from '@mui/material';
import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Search page
 * @return {React.ReactElement} The Search page.
 */
export default function Home(): React.ReactElement {
  const navigate = useNavigate();
  const [searchText, setSearchText] = React.useState('');

  const handleSearchTextChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    // debounce the search
    const value = event.target.value;
    const timeout = setTimeout(() => {
      setSearchText(value);
    }, 500);
    return () => clearTimeout(timeout);
  };

  const handleSearchSubmit = () => {
    navigate(`/search?q=${searchText}`);
  };

  return (
    <>
      <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 3, justifyContent: 'center', alignItems: 'center', height: '500px' }}>
        <img src={SearchTueLogo} alt="RHC Logo" className="logo" height="auto" width={'300px'} color="white" data-tid="logo" />
        <Box sx={{ display: 'flex', flexDirection: 'row' }}>
          <TextField label="Suche" variant="outlined" sx={{ mr: -1, minWidth: '350px' }} onChange={handleSearchTextChange} />
          <Button
            variant="contained"
            color="primary"
            onClick={handleSearchSubmit}
            sx={{ px: 3, borderTopLeftRadius: 0, borderBottomLeftRadius: 0 }}
            startIcon={<SearchIcon />}
          >
            Suche
          </Button>
        </Box>
      </Box>
    </>
  );
}
