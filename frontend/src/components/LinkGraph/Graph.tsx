import { SearchResultsDocument } from '@SearchTue/components/SearchResults/SingleDoc';
import React from 'react';
import { GraphCanvas } from 'reagraph';

export interface GraphDto {
  resultNode: string;
  edges: EdgeDto[];
  nodes: NodeDto[];
}

export interface EdgeDto {
  id: string;
  source: string;
  target: string;
  label: string;
  doc: SearchResultsDocument;
}

export interface NodeDto {
  id: string;
  label: string;
  size?: number;
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

// eslint-disable-next-line @typescript-eslint/no-unused-vars
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
      <GraphCanvas nodes={graph.nodes} edges={graph.edges} />
    </div>
  );
};
