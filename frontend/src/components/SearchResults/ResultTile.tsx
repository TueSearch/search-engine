import { GraphDto, NodeDto, EdgeDto, GraphElement } from '@SearchTue/components/LinkGraph/Graph';
import { SearchResultsDocument } from '@SearchTue/components/SearchResults/SingleDoc';
import { ResultDescriptionPopup } from '@SearchTue/components/SearchResults/ResultDescriptionPopup';
import useTheme from '@mui/material/styles/useTheme';
import { Box } from '@mui/system';
import axios from 'axios';
import React, { useEffect } from 'react';

interface ResultTileProps {
  doc: SearchResultsDocument;
}

export const ResultTile = ({ doc }: ResultTileProps) => {
  const theme = useTheme();

  const [neighborDocs, setNeighborDocs] = React.useState<SearchResultsDocument[] | null>(null);
  const [selectedDoc, setSelectedDoc] = React.useState<SearchResultsDocument>(doc);

  const [graphDocumentMap] = React.useState<Map<string, SearchResultsDocument>>(new Map());

  const [graph, setGraph] = React.useState<GraphDto>({ resultNode: doc.id.toString(), edges: [], nodes: [] });

  const [mousePos, setMousePos] = React.useState<{ x: number; y: number }>({ x: 0, y: 0 });

  const [xPos, setXPos] = React.useState<number>(0);
  const [yPos, setYPos] = React.useState<number>(0);
  const [popupVisible, setPopupVisible] = React.useState<boolean>(false);

  useEffect(() => {
    getNearestNeighborLinks(doc.id.toString(), 5);
  }, [doc.id]);

  useEffect(() => {
    buildGraph();
  }, [neighborDocs]);

  useEffect(() => {
    const handleMouseMove = (event: MouseEvent) => {
      setMousePos({ x: event.clientX, y: event.clientY });
    };

    document.addEventListener('mousemove', handleMouseMove);

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  useEffect(() => {
    const handleDocumentClick = () => {
      if (popupVisible) {
        setPopupVisible(false);
      }
    };

    document.addEventListener('click', handleDocumentClick);

    return () => {
      document.removeEventListener('click', handleDocumentClick);
    };
  }, [popupVisible]);

  const handleNodeClick = (id: string) => {
    console.log('Node clicked in parent component', id);
    console.log('Map:', graphDocumentMap);
    if (graphDocumentMap.has(id)) {
      const doc = graphDocumentMap.get(id);
      if (!doc) {
        return;
      }
      setSelectedDoc(doc);
      // Set xPos to mouse x position
      setXPos(mousePos.x);
      // Set yPos to mouse y position
      setYPos(mousePos.y);

      // timeout to prevent popup from closing immediately
      setTimeout(() => {
        setPopupVisible(true);
      }, 100);
      console.log('Doc: ', doc);
    }
  };

  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const buildGraph = () => {
    // TODO: build graph from neighbor docs
    console.log('Building graph from neighbor docs', neighborDocs);

    if (!neighborDocs) {
      return;
    }

    // iterate over neighbor docs and build graph
    const nodes: NodeDto[] = neighborDocs.map((neighbor, index) => {
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
      };
    });

    console.log('Nodes: ', nodes);

    const edges: EdgeDto[] = Array.from(graphDocumentMap).map(([id, neighborDoc], index) => {
      return {
        id: index.toString(),
        source: id,
        target: doc.id.toString(),
        label: id + '-' + doc.id,
        doc: neighborDoc,
      };
    });

    console.log('Edges: ', edges);

    // add result node
    graphDocumentMap.set(doc.id.toString(), doc);
    nodes.push({
      id: doc.id.toString(),
      label: '',
      
      size: 15,
    });

    console.log('Graph: ', nodes, edges);
    setGraph({
      resultNode: doc.id.toString(),
      nodes: nodes,
      edges: edges,
    });
  };

  const getNearestNeighborLinks = (docId: string, num: number) => {
    console.log('Getting nearest neighbor links', docId, num);
    if (!docId || docId === '') {
      return;
    }
    axios
      .post(`${import.meta.env.VITE_API_URL}/semantic-api/search_documents_by_documents`,
        {
          doc_id: docId,
          num_docs: num,
          is_english_prob: 9
        })
      .then((response) => {
        console.log('Nearest neighbor response:', response)
        setNeighborDocs(response.data.similar_docs);
      })
      .catch((error) => {
        console.log(error);
      });
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
            justifyContent: 'center',
            borderBottomLeftRadius: '10px',
            borderBottomRightRadius: '10px',
            background: theme.palette.primary.main, 
            height: '100px'
          }}
        >
          <div style={{ color: 'white', padding: '10px', fontSize: '1.5em', cursor: 'pointer', textAlign: 'center' }} onClick={() => window.open(doc.url, '_blank')}>
            {doc.title.length > 100 ? doc.title.slice(0, 100) + '...' : doc.title}
          </div>
        </Box>
      </Box>
      <p style={{ textAlign: 'center', height: '200px' }}>
        {doc.meta_description.length > 500 ? doc.meta_description.slice(0, 500) + '...' : doc.meta_description}
      </p>
      {popupVisible && <ResultDescriptionPopup xPos={xPos} yPos={yPos} doc={selectedDoc} />}
    </Box>
  );
};
