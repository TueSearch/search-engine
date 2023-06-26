import * as dotenv from 'dotenv';
dotenv.config();

const envOrError = (key: string): string => {
  const value = process.env[key];
  if (value === undefined) {
    throw new Error(`Missing environment variable: ${key}`);
  }
  return value;
};

export const BACKEND_PORT = envOrError('BACKEND_PORT');
export const BACKEND_URL = envOrError('BACKEND_URL');
export const NODE_ENV = envOrError('NODE_ENV');
