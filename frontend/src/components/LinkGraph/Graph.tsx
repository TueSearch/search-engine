import { Typography } from '@mui/material';
import { Box } from '@mui/system';
import { SearchResultsDocument } from '@SearchTue/components/searchResults/SingleDoc';
import { GraphCanvas } from 'reagraph';

export interface GraphDto {
  resultNode: string;
  edges: Edge[];
  nodes: Node[];
}

export interface Edge {
  id: string;
  source: string;
  target: string;
  doc: SearchResultsDocument;
}

export interface Node {
  id: string;
  // outgoingEdges: Edge[];
}

interface GraphElementProps {
  graph: GraphDto;
}

const nodes = [
  {
    id: '1',
    label: '1',
  },
  {
    id: '2',
    label: '2',
  },
];

const edges = [
  {
    source: '1',
    target: '2',
    id: '1-2',
    label: '1-2',
  },
  {
    source: '2',
    target: '1',
    id: '2-1',
    label: '2-1',
  },
];

export const GraphElement = ({ graph }: GraphElementProps) => {
  return (
    <div
      style={{
        display: 'block',
        position: 'relative',
        width: '100%',
        height: '60vh',
        overflow: 'hidden',
        borderTopLeftRadius: '10px',
        borderTopRightRadius: '10px',
      }}
    >
      <GraphCanvas nodes={nodes} edges={edges} />
    </div>
  );
};
