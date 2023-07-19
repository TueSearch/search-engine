import { GraphDto, NodeDto, EdgeDto, GraphElement } from '@SearchTue/components/LinkGraph/Graph';
import { SearchResultsDocument } from '@SearchTue/components/SearchResults/SingleDoc';
import useTheme from '@mui/material/styles/useTheme';
import { Box } from '@mui/system';
import axios from 'axios';
import React, { useEffect } from 'react';
import { GraphNode } from 'reagraph';

interface ResultTileProps {
  doc: SearchResultsDocument;
}

export const ResultTile = ({ doc }: ResultTileProps) => {
  const theme = useTheme();

  const [neighborDocs, setNeighborDocs] = React.useState<SearchResultsDocument[] | null>(null);

  const [graphDocumentMap, setGraphDocumentMap] = React.useState<Map<string, SearchResultsDocument>>(new Map());

  const [graph, setGraph] = React.useState<GraphDto>(
    { resultNode: doc.id, edges: [], nodes: [] }
  );

  useEffect(() => {
    getNearestNeighborLinks(doc.id, 3);
  }, [doc.id]);

  useEffect(() => {
    buildGraph();
  }, [neighborDocs]);

  const mockGraph: GraphDto = {
    resultNode: '1',
    edges: [
      {
        id: '0',
        source: '1',
        target: '2',
        label: '1-2',
        doc: doc,
      },
    ],
    nodes: [
      {
        id: '2',
        label: '2',
      },
    ],
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const buildGraph = () => {
    // TODO: build graph from neighbor docs
    console.log('Building graph from neighbor docs', neighborDocs);

    if (!neighborDocs) {
      return;
    }

    // iterate over neighbor docs and build graph
    let nodes: NodeDto[] = neighborDocs.map((neighbor,index) => {
      
      let label = neighbor.title;
      try {
        const url = new URL(neighbor.url);
        label = url.hostname;
      } catch (error) {
        console.error(`Invalid URL: ${neighbor.url}`);
      }
      
      let id = neighbor.id.toString();
      if (graphDocumentMap.has(id) || id === doc.id.toString()) {
        id = id + index.toString();
      }
      graphDocumentMap.set(id, neighbor);

      return {
        id: id,
        label: label,
      }
    });

    console.log('Nodes: ', nodes);

    let edges: EdgeDto[] = Array.from(graphDocumentMap).map(([id, neighborDoc], index) => {
      return {
        id: index.toString(),
        source: id,
        target: doc.id.toString(),
        label: id + '-' + doc.id,
        doc: neighborDoc
      };
    });

    console.log('Edges: ', edges);

    // add result node
    graphDocumentMap.set(doc.id.toString(), doc);
    nodes.push({
      id: doc.id.toString(),
      label: 'Result',
      size: 15
    });

    console.log('Graph: ', nodes, edges)
    setGraph({
      resultNode: doc.id,
      nodes: nodes,
      edges: edges
    });

  };

  const getNearestNeighborLinks = (doc_id: string, num: number) => {
    console.log('Getting nearest neighbor links', doc_id, num)
    if (!doc_id || doc_id === '') {
      return;
    }
    axios
      .get(`${import.meta.env.VITE_API_URL}/nearest/${doc_id}?num=${num}`)
      .then((response) => {
        setNeighborDocs(response.data.results);

      })
      .catch((error) => {
        console.log(error);
      });
  };

  const handleNodeClick = (id: string) => {
    console.log('Node clicked in parent component', id);
    console.log("Map:", graphDocumentMap)
    if (graphDocumentMap.has(id)) {
      const doc = graphDocumentMap.get(id);
      console.log('Doc: ', doc);
    }
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
        <GraphElement graph={graph} handleNodeClick={handleNodeClick} />

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
