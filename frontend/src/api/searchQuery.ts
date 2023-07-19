import { SearchResults } from '@SearchTue/components/SearchResults/SingleDoc';
import axios from 'axios';

export const searchQuery = async (query: string): Promise<SearchResults | null> => {
  if (query === '') {
    return null;
  }

  const result = await axios.get(`${import.meta.env.VITE_API_URL}/search?q=${query}`);
  console.log(result.data);

  if (result.data === null) {
    return null;
  }

  return result.data;
};
