import { NODE_ENV } from '@SearchEngine/constants';
import { Router } from 'express';
// eslint-disable-next-line new-cap
const router = Router();

router.get('/', (_req, res) => {
  res.status(200).json({ message: `Server Running ${NODE_ENV}` });
});

router.get('/search', ()=>{console.log('search')});

export default router;
