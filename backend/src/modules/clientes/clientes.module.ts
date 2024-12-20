import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { PrometheusModule } from '@willsoto/nestjs-prometheus';
import { ClientesService } from './clientes.service';
import { ClientesController } from './clientes.controller';
import { Cliente } from './entities/cliente.entity';
import { AuthModule } from '../auth/auth.module';
import { clienteMetrics } from '../../config/prometheus.config';
import { AdvancedMetricsService } from '../../config/advanced-metrics.config';

@Module({
  imports: [
    // Importar módulo de autenticación para guards
    AuthModule,
    
    // Registrar entidad de cliente en TypeORM
    TypeOrmModule.forFeature([Cliente]),

    // Módulo de Prometheus para métricas
    PrometheusModule.register({
      metrics: [
        clienteMetrics.createClienteCounter,
        clienteMetrics.findClienteHistogram,
        clienteMetrics.updateClienteCounter,
        clienteMetrics.deleteClienteCounter
      ]
    })
  ],
  controllers: [ClientesController],
  providers: [
    ClientesService, 
    AdvancedMetricsService,
    // Registrar métricas como providers
    {
      provide: 'CREATE_CLIENTE_COUNTER',
      useValue: clienteMetrics.createClienteCounter
    },
    {
      provide: 'FIND_CLIENTE_HISTOGRAM',
      useValue: clienteMetrics.findClienteHistogram
    }
  ],
  exports: [
    ClientesService, 
    AdvancedMetricsService
  ]
})
export class ClientesModule {}
