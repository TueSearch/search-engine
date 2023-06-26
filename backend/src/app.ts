import * as dotenv from 'dotenv';
dotenv.config();

import { BACKEND_PORT, NODE_ENV } from '@rhc/constants';
import routes from '@rhc/routes';
import compression from 'compression';
import express from 'express';
import helmet from 'helmet';

process.on('uncaughtException', (e) => {
  console.error('uncaughtException', e);
});

export const app = express();

// Middleware for parsing JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// activate helmet for security protection
app.use(helmet());

// activate compression for better performance
app.use(compression());

// init supabase

app.use('/', routes);

// catch 404 and forward to error handler
app.use((_req, res) => {
  return res.status(404).send('Wrong routing \n Error 404');
});

app
  .listen(BACKEND_PORT, () => {
    console.info(`The application (${NODE_ENV}) is listening on port ${BACKEND_PORT}!`);
  })
  .on('error', (e) => {
    console.error(e);
  });

export default app;
