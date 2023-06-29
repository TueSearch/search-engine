import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { Grid, IconButton } from '@mui/material';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

export const Impressum = (): React.ReactElement => {
  const navigate = useNavigate();
  return (
    <>
      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 3 }}>
        <Grid container spacing={1} alignItems="center">
          <Grid item xs={2}>
            <IconButton color={'primary'} onClick={() => navigate('..', { relative: 'path' })}>
              <ArrowBackIcon />
            </IconButton>
          </Grid>
          <Grid item xs={8} textAlign={'center'}>
            <Typography variant="h4">Impressum</Typography>
          </Grid>
          <Grid item xs={2} />
        </Grid>
        <Typography variant="h5">Angaben gemäß § 5 TMG</Typography>
        <Box>
          <Typography variant="body1">TueSearch</Typography>
          <Typography variant="body1">Sand 14</Typography>
          <Typography variant="body1">72074 Tübingen</Typography>
        </Box>

        <Box>
          <Typography variant="h5">Github Project</Typography>
          <Typography variant="body1">
            <Link to="https://github.com/TueSearch/search-engine">SearchTue</Link>
          </Typography>
        </Box>
      </Box>
    </>
  );
};
