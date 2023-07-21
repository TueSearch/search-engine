import { SearchResultsDocument } from '@SearchTue/components/SearchResults/SingleDoc';
import React, { useRef, useEffect } from 'react';
import { GraphCanvas, GraphCanvasRef, GraphNode, useSelection } from 'reagraph';

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
  handleNodeClick: (id: string) => void;
  graph: GraphDto;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const GraphElement = ({ graph, handleNodeClick }: GraphElementProps) => {
  const graphRef = useRef<GraphCanvasRef | null>(null);
  const { selections, actives, onNodeClick, onCanvasClick } = useSelection({
    ref: graphRef,
    nodes: graph.nodes,
    edges: graph.edges,
    pathSelectionType: 'all',
    focusOnSelect: false,
  });

  useEffect(() => {
    if (onNodeClick) {
      handleNodeClick(selections[0]);
    }
  }, [onNodeClick]);

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
      <GraphCanvas
        ref={graphRef}
        nodes={graph.nodes}
        edges={graph.edges}
        selections={selections}
        actives={actives}
        onCanvasClick={onCanvasClick}
        onNodeClick={onNodeClick}
      />
    </div>
  );
};
