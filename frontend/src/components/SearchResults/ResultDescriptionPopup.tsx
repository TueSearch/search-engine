import { SearchResultsDocument } from '@SearchTue/components/SearchResults/SingleDoc';
import { Divider, Tooltip } from '@mui/material';
import React from 'react';

interface ResultDescriptionPopup {
  xPos: number;
  yPos: number;
  doc: SearchResultsDocument;
}

// eslint-disable-next-line @typescript-eslint/no-unused-vars
export const ResultDescriptionPopup = ({ xPos, yPos, doc }: ResultDescriptionPopup) => (
  <div
    style={{
      position: 'absolute',
      top: yPos + 20,
      left: xPos - 250,
      width: '500px',
      background: 'white',
      padding: '10px',
      borderRadius: '10px',
      boxShadow: '0px 0px 64px 14px rgba(0,0,0,0.1)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '10px',
    }}
  >
    <Tooltip title={doc.url} placement="top-start">
      <div
        style={{
          fontSize: '1.3em',
          fontWeight: 'bold',
          cursor: 'pointer',
        }}
        onClick={() => window.open(doc.url, '_blank')}
      >
        {doc.title}
      </div>
    </Tooltip>
    <Divider flexItem />
    <div>{doc.meta_description}</div>
    <div></div>
  </div>
);
