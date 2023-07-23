import { Box, Typography } from '@mui/material';
import { Stack } from '@mui/system';
import React from 'react';
import { Link } from 'react-router-dom';

export interface SearchResultsDocument {
  id: number;
  scores: number;
  title: string;
  meta_author: string;
  meta_description: string;
  meta_keywords: string;
  url: string;
  body: string;
  relevant: boolean;
  is_english_prob: number;
  is_german_prob: number;
}

export interface SearchResults {
  page: number;
  pageSize: number;
  query: string;
  results: SearchResultsDocument[];
}

interface SingleDocProps {
  doc: SearchResultsDocument;
  show_eng_prob: boolean;
}



export const SingleDoc = ({doc, show_eng_prob}: SingleDocProps) => {
  const mayBeDocTitle = doc.title !== '' ? doc.title : doc.url.split('//')[1].split('/')[0];

  const slicedDocTitle = mayBeDocTitle.slice(0, 100);
  const slicedDocTitleEllipsis = mayBeDocTitle.length > 100 ? '...' : '';

  // calculate english probability
  const english_prob = doc.is_english_prob*10;

  const getColorFromProb = (prob: number) => {
    if (prob < 3) {
      return 'red';
    } else if (prob < 6) {
      return 'orange';
    } else {
      return 'green';
    }
  };

  // style for changing color to primary when hovering box
  const style = {
    '&:hover': {
      color: 'secondary.dark',
    },
  };


  return (
    <Stack direction={'column'} alignItems={'flex-start'} sx={{ p: 2 }}>
      <Link to={doc.url} target="_blank" rel="noopener noreferrer" className="noUnderline">
        <Box component={'div'} sx={style}>
          {show_eng_prob && <Typography variant="caption" data-tid="probs" fontSize={'bigger'} color={getColorFromProb(doc.is_english_prob)}>
            {english_prob}% English
          </Typography>}
          <Typography variant="h6" data-tid="title">
            {slicedDocTitle}
            {slicedDocTitleEllipsis}
          </Typography>
        </Box>
      </Link>
      <Box component={'div'}>
        <Link to={doc.url} target="_blank" rel="noopener noreferrer" className="noUnderline">
          <Typography variant="body2" data-tid="url">
            {doc.url}
          </Typography>
        </Link>
      </Box>
      <Box component={'div'}>
        <Link to={doc.url} target="_blank" rel="noopener noreferrer" className="noUnderline">
          <Stack direction={'row'} gap={1}>
            {doc.meta_author !== '' && (
              <Typography variant="caption" data-tid="author" fontSize={'bigger'}>
                {doc.meta_author}
              </Typography>
            )}
            {doc.meta_keywords !== '' && doc.meta_author !== ' ' && (
              <Typography variant="caption" data-tid="gap">
                {' | '}
              </Typography>
            )}
            <Typography variant="caption" data-tid="description">
              {doc.meta_keywords.slice(0, 50)}
              {doc.meta_keywords.length > 50 ? '...' : ''}
            </Typography>
          </Stack>
          <Typography variant="body1" data-tid="description" sx={{ overflow: 'hidden' }}>
            {doc.meta_description.slice(0, 175)}
            {doc.meta_description.length > 175 ? '...' : ''}
          </Typography>
        </Link>
      </Box>
    </Stack>
  );
};
