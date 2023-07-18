import { Box, Typography } from '@mui/material';
import { Stack } from '@mui/system';
import React from 'react';
import { Link } from 'react-router-dom';

export interface SearchResultsDocument {
  id: number;
  scores: number;
  title: string;
  description: string;
  url: string;
  is_english_prob: number;
  is_german_prob: number;
}

export interface SearchResults {
  page: number;
  pageSize: number;
  query: string;
  results: SearchResultsDocument[];
}

export const SingleDoc = ({ doc }: { doc: SearchResultsDocument }) => {
  return (
    <Stack direction={'column'} alignItems={'flex-start'} sx={{ p: 2 }}>
      <Box component={'div'}>
        <Typography variant="h6" data-tid="title">
          {doc.title}
        </Typography>
      </Box>
      <Box component={'div'}>
        <Typography variant="body1" data-tid="description">
          {doc.description}
        </Typography>
      </Box>
      <Box component={'div'}>
        <Link to={doc.url} target="_blank" rel="noopener noreferrer">
          <Typography variant="body2" data-tid="url">
            {doc.url}
          </Typography>
        </Link>
      </Box>
    </Stack>
  );
};
