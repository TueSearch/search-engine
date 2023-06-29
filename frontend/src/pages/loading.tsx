import Box from '@mui/material/Box';
import useTheme from '@mui/material/styles/useTheme';
import React from 'react';
import { FallingLines, LineWave } from 'react-loader-spinner';

/**
 * Loading FootballLoading component that is displayed while the data is loading
 *
 * @return {React.ReactElement}
 */
export default function LoadingSuspense(): React.ReactElement {
  const theme = useTheme();

  return (
    <>
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          bgcolor: 'rgba(255,255,255,0.5)',
        }}
        data-tid="loading-box"
      >
        <FallingLines color={theme.palette.primary.main} width="100" visible={true} />
      </Box>
    </>
  );
}

/**
 * Loading FootballLoading component that is displayed while the data is loading
 *
 * @return {React.ReactElement}
 */
export function LoadingSuspenseSmall(): React.ReactElement {
  const theme = useTheme();
  return (
    <>
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          bgcolor: 'rgba(255,255,255,0.5)',
        }}
        data-tid="small-loading-box"
      >
        <LineWave
          height="100"
          width="100"
          color={theme.palette.primary.main}
          wrapperStyle={{}}
          wrapperClass=""
          visible={true}
          firstLineColor=""
          middleLineColor=""
          lastLineColor=""
        />
      </Box>
    </>
  );
}
