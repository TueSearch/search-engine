import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import React from 'react';
import { isRouteErrorResponse, useNavigate, useRouteError } from 'react-router-dom';

/**
 * Error Page Component
 *
 * @return {React.ReactElement}
 */
export default function ErrorPage(): React.ReactElement {
  const navigate = useNavigate();

  const error = useRouteError();
  console.error(error);

  const getErrorText = () => {
    if (isRouteErrorResponse(error)) {
      if (error.status === 404) {
        return 'Die Seite konnte nicht gefunden werden.';
      }

      if (error.status === 401) {
        return 'Du hast keine Berechtigung, diese Seite zu sehen.';
      }

      if (error.status === 503) {
        return 'Unser Server ist gerade nicht erreichbar.';
      }

      if (error.status === 418) {
        return '🫖';
      }
    } else {
      return 'Etwas ist schief gelaufen.';
    }
  };

  const getErrorStatus = () => {
    if (isRouteErrorResponse(error)) {
      return error.status;
    } else {
      return 'Unbekannt';
    }
  };

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
      <Typography variant="h3" color={'primary'}>
        Fehler
      </Typography>

      <Typography variant="h4">{getErrorText()}</Typography>
      <Typography variant="body1">Code: {getErrorStatus()}</Typography>

      <Button onClick={() => navigate('/?status=404')} data-tid="go-back-button">
        Zurück zur Startseite
      </Button>
    </Box>
  );
}
