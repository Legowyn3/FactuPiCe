import { CacheModuleOptions } from '@nestjs/cache-manager';
import { redisStore } from 'cache-manager-redis-yet';
import * as dotenv from 'dotenv';

dotenv.config();

export const cacheConfig: CacheModuleOptions = {
  isGlobal: true,
  store: redisStore,
  host: process.env.REDIS_HOST || 'localhost',
  port: parseInt(process.env.REDIS_PORT || '6379'),
  ttl: 60 * 5, // 5 minutos por defecto
  max: 100, // Máximo 100 elementos en caché
  
  // Configuraciones de Redis
  redisOptions: {
    password: process.env.REDIS_PASSWORD || '',
    tls: process.env.REDIS_TLS === 'true' ? {} : undefined,
  }
};

// Tipos de caché personalizados
export enum CacheKeys {
  CLIENTE_LIST = 'cliente_list',
  CLIENTE_DETAIL = 'cliente_detail',
}
