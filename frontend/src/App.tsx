import React from 'react';
import { ReactQueryDevtools } from 'react-query/devtools';
import './App.css';

import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';

import { CssBaseline } from '@mui/material';
import Routing from '@SearchTue/routes';

import { ColorModeProvider } from '@SearchTue/hooks/useColorMode';
import { QueryClient, QueryClientProvider } from 'react-query';
/**
 *
 * App component
 *
 * @return {React.ReactElement} App component
 */
function App(): React.ReactElement {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        refetchOnWindowFocus: false,
        retry: false,
        cacheTime: 0,
      },
    },
  });

  return (
    <>
      <QueryClientProvider client={queryClient}>
        <ColorModeProvider>
          <CssBaseline />
          <Routing />
        </ColorModeProvider>
        <ReactQueryDevtools />
      </QueryClientProvider>
    </>
  );
}

export default App;
