import { AppBar, Box, Container, Grid, Typography } from '@mui/material';
import useTheme from '@mui/material/styles/useTheme';
import useMediaQuery from '@mui/material/useMediaQuery/useMediaQuery';
import React, { FC, ReactElement } from 'react';
import { Link } from 'react-router-dom';

export const Footer: FC = (): ReactElement => {
  const theme = useTheme();
  const mobile = useMediaQuery(theme.breakpoints.down('sm'));
  return (
    <AppBar position="fixed" enableColorOnDark={true} sx={{ py: 1, bottom: 0, top: 'auto' }}>
      <Container maxWidth="lg">
        <Grid container direction="column" alignItems="center">
          <Grid item xs={12}>
            <Typography variant="subtitle2" component="div">
              <Box component={'div'} sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                <span>{`©${new Date().getFullYear()} `}</span>
                {mobile ? (
                  <Link to="https://github.com/TueSearch/search-engine" target="_blank" className="noUnderline" rel="noreferrer" data-tid="authorLink">
                    by D. Reimer, L. Nguyen, L. Listl, P. Alber
                  </Link>
                ) : (
                  <Link to="https://github.com/TueSearch/search-engine" target="_blank" className="noUnderline" rel="noreferrer" data-tid="authorLink">
                    by Daniel Reimer, Long Nguyen, Lukas Listl, Philipp Alber
                  </Link>
                )}
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
