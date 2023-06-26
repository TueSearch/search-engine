import { noValueCategory } from '@rhc/types/supabaseTypes';
import short from 'short-uuid';

const translator = short();

export const getShortedID = (id: string): string => {
  // catch noValue id
  if (id === noValueCategory.id) {
    return noValueCategory.id;
  }
  // parse id into bas62 string
  const base62 = translator.fromUUID(id);
  return base62 as string;
};

export const getFullID = (shortId: string): string => {
  // catch noValue id
  if (shortId === noValueCategory.id) {
    return noValueCategory.id;
  }
  // parse base62 string into id
  const id = translator.toUUID(shortId);
  return id as string;
};
