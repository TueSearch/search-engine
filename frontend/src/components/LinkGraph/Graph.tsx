import { Typography } from '@mui/material';
import { Box } from '@mui/system';
import { SearchResultsDocument } from '@SearchTue/components/SearchResults/singleDoc';
import React from 'react';

export interface GraphDto {
    resultNode: number;
    edges: Edge[];
    nodes: Node[];
}

export interface Edge {
    id: number;
    source: number;
    target: number;
    doc: SearchResultsDocument;
}

export interface Node {
    id: number;
    // outgoingEdges: Edge[];
}

export const GraphElement = ({ graph }: { graph: GraphDto }) => {
  return (
    <Box sx={{ p: 2, display: 'flex', flexDirection: 'column', width: '100%', borderBottom: '1px solid black', borderRadius: '10px', background: 'white'}}>
      <p>Root id: {graph.resultNode}</p>
      <p>This is where the graph will be displayed</p>
    </Box>
  );
};
