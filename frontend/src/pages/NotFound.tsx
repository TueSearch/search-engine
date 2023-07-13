import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import React from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * NotFound Page Component
 *
 * @return {React.ReactElement}
 */
export default function NotFound(): React.ReactElement {
  const navigate = useNavigate();

  return (
    <Box
      component={'div'}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 10,
      }}
    >
      <Typography variant="h1">404</Typography>
      <Typography variant="h4">Seite nicht gefunden</Typography>

      <Button onClick={() => navigate('/?status=404')} data-tid="go-back-button">
        Zurück zur Startseite
      </Button>
    </Box>
  );
}
