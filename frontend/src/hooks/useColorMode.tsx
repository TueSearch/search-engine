import { createTheme, responsiveFontSizes, ThemeProvider } from '@mui/material';
import type {} from '@mui/x-date-pickers/themeAugmentation';
import React from 'react';

// Themes
import { mainThemeBright, mainThemeDark } from '@SearchTue/assets/styles/theme';

type themeMode = 'dark' | 'light';

interface ColorModeContextProps {
  toggleColorMode: () => void;
  mode: themeMode;
  theme: any;
}

// ColorModeContext
const colorModeContext = React.createContext<ColorModeContextProps>({
  toggleColorMode: () => {},
  mode: 'light',
  theme: {},
});

/**
 *
 * ColorModeProvider for colorMode change
 *
 * @param {React.PropsWithChildren<{}>} children
 * @return {React.ReactElement}
 */
export function ColorModeProvider({ children }: React.PropsWithChildren<{}>): React.ReactElement {
  const colorMode = useProvideColorMode();

  return (
    <colorModeContext.Provider value={colorMode}>
      <ThemeProvider theme={colorMode.theme}>{children}</ThemeProvider>
    </colorModeContext.Provider>
  );
}

export const useColorMode = () => {
  return React.useContext(colorModeContext);
};

/**
 * useProvideColorMode provides the colorModeContext as hook
 *
 * @return {ColorModeContextProps}
 */
function useProvideColorMode(): ColorModeContextProps {
  // theme state
  const [mode, setMode] = React.useState<themeMode>('light');

  const toggleColorMode = React.useCallback(() => {
    setMode((prevMode: themeMode) => {
      return prevMode === 'light' ? 'dark' : 'light';
    });
  }, []);

  let theme = React.useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'dark' ? mainThemeDark : mainThemeBright),
        },
      }),
    [mode]
  );

  // make theme responsive
  theme = responsiveFontSizes(theme);

  return {
    toggleColorMode,
    mode,
    theme,
  };
}
