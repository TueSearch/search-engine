import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import { Footer } from '@SearchTue/components/Footer';
import Header from '@SearchTue/components/Header';
import React from 'react';
import { Outlet } from 'react-router-dom';

export const Layout = () => {
  return (
    <>
      <Header />
      <Grid container spacing={0.5}>
        <Grid item xs={0} sm={1} />
        <Grid item xs={12} sm={10}>
          <Box sx={{ pb: '50px', px: 2 }}>
            <Outlet />
          </Box>
        </Grid>
        <Grid item xs={0} sm={1} />
      </Grid>
      <Footer />
    </>
  );
};
