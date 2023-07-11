import { Typography } from '@mui/material';
import { Box } from '@mui/system';
import useTheme from '@mui/material/styles/useTheme';
import { SearchResultsDocument } from '@SearchTue/components/SearchResults/singleDoc';
import { GraphElement, GraphDto, Edge, Node } from '@SearchTue/components/LinkGraph/Graph';

interface ResultTileProps {
    doc: SearchResultsDocument;
}

export const ResultTile = ({ doc }: ResultTileProps) => {

    const theme = useTheme();

    const mockGraph: GraphDto = {
        resultNode: '1',
        edges: [{
            id: '0',
            source: '1',
            target: '2',
            doc: doc
        }],
        nodes: [{
            id: '2',
        }]
    }

    const buildGraph = (doc: SearchResultsDocument) => {
        // TODO: build graph from doc
        // Additional data needed --> Either make a new request to the backend or add the data to the search results
    }

    return (

        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            width: '30%',
            height: '100%',
        }}>
            <div style={{
                width: '100%',
                height: '100%',
                borderRadius: '10px',
                boxShadow: '0px 0px 64px 14px rgba(0,0,0,0.1)'
            }}>

                <GraphElement graph={mockGraph} />

                <div style={{
                    width: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    borderBottomLeftRadius: '10px',
                    borderBottomRightRadius: '10px',
                    background: theme.palette.primary.main,
                }}>
                    <p style={{ color: 'white', padding: '0px', margin: '0', fontSize: '1.5em' }}>{doc.title}</p>
                </div>

            </div>
            <p style={{ textAlign: 'center' }}>This is going to be the abstract to the displayed result.<br />
                This is the URL: {doc.url} <br />
                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut ac commodo mauris. Proin mollis felis nisi, ut pulvinar tortor cursus et. Ut pellentesque ipsum quis nunc efficitur, eu suscipit lorem malesuada.</p>
        </div>
    );
};
