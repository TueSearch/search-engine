import { AppBar, Box, Container, Grid, Typography } from '@mui/material';
import React, { FC, ReactElement } from 'react';
import { Link } from 'react-router-dom';

export const Footer: FC = (): ReactElement => {
  return (
    <AppBar position="fixed" enableColorOnDark={true} sx={{ py: 1, bottom: 0, top: 'auto' }}>
      <Container maxWidth="lg">
        <Grid container direction="column" alignItems="center">
          <Grid item xs={12}>
            <Typography variant="subtitle2" component="div">
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <span>{`©${new Date().getFullYear()} `}</span>
                <Link to="https://philippalber.de" target="_blank" className="noUnderline" rel="noreferrer" data-tid="authorLink">
                  by Daniel Reimer, Long Nguyen, Lukas Listl, Philipp Alber
                </Link>
                <span> | </span>
                <Link to="/impressum" className="noUnderline" data-tid="impressumLink">
                  Impressum
                </Link>
              </Box>
            </Typography>
          </Grid>
        </Grid>
      </Container>
    </AppBar>
  );
};
