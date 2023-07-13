import { GraphDto, GraphElement } from '@SearchTue/components/LinkGraph/Graph';
import { SearchResultsDocument } from '@SearchTue/components/searchResults/SingleDoc';
import useTheme from '@mui/material/styles/useTheme';
import { Box } from '@mui/system';
import React from 'react';

interface ResultTileProps {
  doc: SearchResultsDocument;
}

export const ResultTile = ({ doc }: ResultTileProps) => {
  const theme = useTheme();

  const mockGraph: GraphDto = {
    resultNode: '1',
    edges: [
      {
        id: '0',
        source: '1',
        target: '2',
        doc: doc,
      },
    ],
    nodes: [
      {
        id: '2',
      },
    ],
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const buildGraph = (doc: SearchResultsDocument) => {
    // TODO: build graph from doc
    // Additional data needed --> Either make a new request to the backend or add the data to the search results
  };

  return (
    <Box
      component={'div'}
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '30%',
        height: '100%',
      }}
    >
      <Box
        component={'div'}
        sx={{
          width: '100%',
          height: '100%',
          borderRadius: '10px',
          boxShadow: '0px 0px 64px 14px rgba(0,0,0,0.1)',
        }}
      >
        <GraphElement graph={mockGraph} />

        <Box
          component={'div'}
          sx={{
            width: '100%',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            borderBottomLeftRadius: '10px',
            borderBottomRightRadius: '10px',
            background: theme.palette.primary.main,
          }}
        >
          <p style={{ color: 'white', padding: '0px', margin: '0', fontSize: '1.5em' }}>{doc.title}</p>
        </Box>
      </Box>
      <p style={{ textAlign: 'center' }}>
        This is going to be the abstract to the displayed result.
        <br />
        This is the URL: {doc.url} <br />
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ac commodo mauris. Proin mollis felis nisi, ut pulvinar tortor cursus et. Ut pellentesque ipsum quis
        nunc efficitur, eu suscipit lorem malesuada.
      </p>
    </Box>
  );
};
