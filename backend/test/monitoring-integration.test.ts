import { Test, TestingModule } from '@nestjs/testing';
import { MonitoringIntegrationService } from '../src/config/monitoring-integration.config';
import { PrometheusModule } from '@willsoto/nestjs-prometheus';
import { Registry } from 'prom-client';

describe('MonitoringIntegrationService', () => {
  let monitoringService: MonitoringIntegrationService;
  let registry: Registry;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [PrometheusModule.register()],
      providers: [MonitoringIntegrationService]
    }).compile();

    monitoringService = module.get<MonitoringIntegrationService>(MonitoringIntegrationService);
    registry = new Registry();
  });

  it('debe inicializar métricas por defecto', () => {
    const metricsStatus = monitoringService.getMetricsStatus();
    
    expect(metricsStatus.totalMetrics).toBeGreaterThan(0);
    expect(metricsStatus.registeredMetrics).toBeDefined();
  });

  it('debe exportar métricas en formato Prometheus', async () => {
    const metrics = await monitoringService.getMetrics();
    
    expect(metrics).toBeTruthy();
    expect(metrics).toContain('factupicev2_');
  });

  it('debe reiniciar métricas correctamente', () => {
    const initialMetricsCount = monitoringService.getMetricsStatus().totalMetrics;
    
    monitoringService.resetMetrics();
    const resetMetricsCount = monitoringService.getMetricsStatus().totalMetrics;
    
    expect(resetMetricsCount).toBeGreaterThan(0);
    expect(resetMetricsCount).toBe(initialMetricsCount);
  });

  it('debe incluir métricas personalizadas', () => {
    const metricsStatus = monitoringService.getMetricsStatus();
    
    const customMetrics = [
      'factupicev2_cliente_create_total',
      'factupicev2_cliente_find_duration_seconds',
      'factupicev2_cliente_update_total',
      'factupicev2_cliente_delete_total'
    ];

    customMetrics.forEach(metricName => {
      const metricExists = metricsStatus.registeredMetrics.some(
        metric => metric.includes(metricName)
      );
      expect(metricExists).toBeTruthy();
    });
  });

  it('debe manejar concurrencia de métricas', async () => {
    const concurrentRequests = 10;
    const promises = Array.from({ length: concurrentRequests }, () => 
      monitoringService.getMetrics()
    );

    const results = await Promise.all(promises);
    
    results.forEach(metrics => {
      expect(metrics).toBeTruthy();
      expect(metrics).toContain('factupicev2_');
    });
  });

  it('debe proporcionar información detallada de estado', () => {
    const metricsStatus = monitoringService.getMetricsStatus();
    
    expect(metricsStatus).toHaveProperty('totalMetrics');
    expect(metricsStatus).toHaveProperty('registeredMetrics');
    expect(Array.isArray(metricsStatus.registeredMetrics)).toBeTruthy();
  });
});
