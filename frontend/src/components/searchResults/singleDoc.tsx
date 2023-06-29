import { Typography } from '@mui/material';
import { Box } from '@mui/system';
import React from 'react';

export interface SearchResultsDocument {
  id: number;
  title: string;
  url: string;
}

export interface SearchResults {
  page: number;
  pageSize: number;
  query: string;
  results: SearchResultsDocument[];
}

export const SingleDoc = ({ doc }: { doc: SearchResultsDocument }) => {
  return (
    <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
      <Typography variant="h6" data-tid="title">
        {doc.title}
      </Typography>
      <Typography variant="body1" data-tid="url">
        {doc.url}
      </Typography>
    </Box>
  );
};
