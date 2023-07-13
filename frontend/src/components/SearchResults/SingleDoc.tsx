import { Box, Typography } from '@mui/material';
import React from 'react';
import { Link } from 'react-router-dom';

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
    <Box component="div" sx={{ p: 2, display: 'flex', flexDirection: 'column', gap: 1 }}>
      <Typography variant="h6" data-tid="title">
        {doc.title}
      </Typography>
      <Link to={doc.url} target="_blank" rel="noopener noreferrer">
        <Typography variant="body1" data-tid="url">
          {doc.url}
        </Typography>
      </Link>
    </Box>
  );
};
