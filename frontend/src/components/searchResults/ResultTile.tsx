import { Typography } from '@mui/material';
import { Box } from '@mui/system';
import useTheme from '@mui/material/styles/useTheme';
import { SearchResultsDocument } from '@SearchTue/components/searchResults/singleDoc';
import { GraphElement, Graph } from '@SearchTue/components/LinkGraph/Graph';
import React from 'react';


export const ResultTile = ({ doc }: { doc: SearchResultsDocument }) => {

    const theme = useTheme();

    const mockGraph: Graph = {
        resultNode: 1,
        edges: [{
            id: 0,
            source: 1,
            target: 2,
            doc: doc
        }],
        nodes: [{
            id: 2,
        }]
    }

    const buildGraph = (doc: SearchResultsDocument) => {
        // TODO: build graph from doc
        // Additional data needed --> Either make a new request to the backend or add the data to the search results
    }

    return (
        <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', maxWidth: '20%' }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', border: '1px solid black', borderRadius: '10px', background: theme.palette.primary.main }}>
                <GraphElement graph={mockGraph} />
                <p style={{ color: 'white', padding: '0px', margin: '0', fontSize: '1.5em' }}>{doc.title}</p>
            </Box>
            <p style={{ textAlign: 'center' }}>This is going to be the abstract to the displayed result. <br />
                This is the URL: {doc.url} <br />
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ac commodo mauris. Proin mollis felis nisi, ut pulvinar tortor cursus et. Ut pellentesque ipsum quis nunc efficitur, eu suscipit lorem malesuada.</p>
        </Box>
    );
};
