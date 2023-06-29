import SearchTueLogoIcon from '@SearchTue/assets/images/logo_icon.svg';
import { useColorMode } from '@SearchTue/hooks/useColorMode';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Stack from '@mui/material/Stack';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import useTheme from '@mui/material/styles/useTheme';
import React from 'react';
import { DarkModeToggle } from 'react-dark-mode-toggle-2';
import { Link } from 'react-router-dom';

/**
 * Header component.
 * @return {React.ReactElement} The Header.
 * */
export default function Header(): React.ReactElement {
  const { toggleColorMode } = useColorMode();
  const theme = useTheme();

  return (
    <Box sx={{ flexGrow: 1 }}>
      <AppBar position="static" enableColorOnDark={true}>
        <Toolbar
          sx={{
            display: 'flex',
            justifyContent: 'flex-start',
            alignItems: 'center',
            gap: 2,
          }}
        >
          <Link to="/" className="noUnderline">
            <Stack direction="row" spacing={1}>
              <img src={SearchTueLogoIcon} alt="RHC Logo" className="logo" height="auto" width={'40px'} color="white" data-tid="logo" />
              <Typography variant="h6" component="div" sx={{ display: { xs: 'none', sm: 'block' } }}>
                TueSearch
              </Typography>
            </Stack>
          </Link>
          <Typography variant="body2" component="div">
            {import.meta.env.VITE_APP_VERSION}
          </Typography>

          <Box
            sx={{
              marginLeft: 'auto!important',
            }}
          />

          <DarkModeToggle onChange={toggleColorMode} isDarkMode={theme.palette.mode === 'dark'} size={50} className="darkModeToggle" />
        </Toolbar>
      </AppBar>
    </Box>
  );
}
