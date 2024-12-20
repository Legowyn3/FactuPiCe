import { PrometheusModule } from '@willsoto/nestjs-prometheus';
import { Counter, Histogram } from 'prom-client';

export const prometheusConfig = {
  imports: [
    PrometheusModule.register({
      defaultMetrics: {
        enabled: true,
        config: {
          prefix: 'factupicev2_',
        },
      },
    }),
  ],
};

// Métricas personalizadas para el módulo de Clientes
export const clienteMetrics = {
  createClienteCounter: new Counter({
    name: 'factupicev2_cliente_create_total',
    help: 'Total de clientes creados',
    labelNames: ['success']
  }),
  
  findClienteHistogram: new Histogram({
    name: 'factupicev2_cliente_find_duration_seconds',
    help: 'Tiempo de búsqueda de clientes',
    labelNames: ['method', 'success'],
    buckets: [0.1, 0.5, 1, 2, 5]
  }),

  updateClienteCounter: new Counter({
    name: 'factupicev2_cliente_update_total',
    help: 'Total de clientes actualizados',
    labelNames: ['success']
  }),

  deleteClienteCounter: new Counter({
    name: 'factupicev2_cliente_delete_total',
    help: 'Total de clientes eliminados',
    labelNames: ['success']
  })
};
