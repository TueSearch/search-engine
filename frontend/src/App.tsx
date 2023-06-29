import React from 'react';
import './App.css';

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import { CssBaseline } from '@mui/material';
import Routing from '@SearchTue/routes';

import { ColorModeProvider } from '@SearchTue/hooks/useColorMode';
/**
 *
 * App component
 *
 * @return {React.ReactElement} App component
 */
function App(): React.ReactElement {
  return (
    <ColorModeProvider>
      <CssBaseline />
      <Routing />
    </ColorModeProvider>
  );
}

export default App;
