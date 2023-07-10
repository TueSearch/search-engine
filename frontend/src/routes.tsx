import { Layout } from '@SearchTue/components/Layout';
import ErrorPage from '@SearchTue/pages/ErrorPage';
import Home from '@SearchTue/pages/Home';
import { Impressum } from '@SearchTue/pages/Impressum';
import GraphSearch from '@SearchTue/pages/GraphSearch';
import Search from '@SearchTue/pages/Search';
import LoadingSuspense from '@SearchTue/pages/loading';
import React, { Suspense } from 'react';
import { Navigate, RouterProvider } from 'react-router';
import { createBrowserRouter } from 'react-router-dom';
import NotFound from './pages/NotFound';

/**
 * Creating a router for the application.
 * @return {React.ReactElement} The router for the application.
 */
export default function Routing(): React.ReactElement {
  const router = createBrowserRouter([
    {
      path: '/',
      element: <Layout />,
      errorElement: <ErrorPage />,
      children: [
        {
          path: '/',
          element: <Home />,
        },
        {
          path: '/graph-search',
          element: <GraphSearch />
        },
        {
          path: '/search',
          element: <Search />,
        },
        {
          path: '/logs',
          element: <Navigate to={'/events/all'} />,
        },

        {
          path: '/impressum',
          element: <Impressum />,
        },

        {
          path: '/404',
          element: <NotFound />,
        },
        {
          path: '/error',
          element: <ErrorPage />,
        },
        {
          path: '/*',
          element: <NotFound />,
        },
      ],
    },
  ]);

  return (
    <>
      <Suspense fallback={<LoadingSuspense />}>
        <RouterProvider router={router} />
      </Suspense>
    </>
  );
}
