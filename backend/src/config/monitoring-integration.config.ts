import { Injectable, OnModuleInit } from '@nestjs/common';
import { PrometheusModule } from '@willsoto/nestjs-prometheus';
import * as promClient from 'prom-client';
import { ConfigService } from '@nestjs/config';

@Injectable()
export class MonitoringIntegrationService implements OnModuleInit {
  private registry: promClient.Registry;

  constructor(private configService: ConfigService) {
    this.registry = new promClient.Registry();
  }

  onModuleInit() {
    // Configuración de métricas por defecto
    promClient.collectDefaultMetrics({
      register: this.registry,
      prefix: 'factupicev2_',
    });

    // Registrar métricas personalizadas
    this.registerCustomMetrics();
  }

  private registerCustomMetrics() {
    // Métricas de solicitudes
    const requestCounter = new promClient.Counter({
      name: 'factupicev2_requests_total',
      help: 'Total de solicitudes procesadas',
      labelNames: ['method', 'path', 'status'],
      registers: [this.registry],
    });

    const requestDuration = new promClient.Histogram({
      name: 'factupicev2_request_duration_seconds',
      help: 'Duración de las solicitudes HTTP',
      labelNames: ['method', 'path', 'status'],
      buckets: [0.1, 0.3, 0.5, 1, 3, 5, 10],
      registers: [this.registry],
    });

    const activeUsers = new promClient.Gauge({
      name: 'factupicev2_active_users',
      help: 'Número de usuarios activos',
      registers: [this.registry],
    });

    // Registrar métricas
    this.registry.registerMetric(requestCounter);
    this.registry.registerMetric(requestDuration);
    this.registry.registerMetric(activeUsers);
  }

  // Métodos de utilidad para actualizar métricas
  incrementRequestCounter(method: string, path: string, status: number) {
    const counter = this.registry.getSingleMetric('factupicev2_requests_total') as promClient.Counter;
    counter?.inc({ method, path, status });
  }

  observeRequestDuration(method: string, path: string, status: number, duration: number) {
    const histogram = this.registry.getSingleMetric('factupicev2_request_duration_seconds') as promClient.Histogram;
    histogram?.observe({ method, path, status }, duration);
  }

  setActiveUsers(count: number) {
    const gauge = this.registry.getSingleMetric('factupicev2_active_users') as promClient.Gauge;
    gauge?.set(count);
  }

  // Método para obtener el registro de métricas
  getMetricsRegistry(): promClient.Registry {
    return this.registry;
  }

  // Método para obtener métricas en formato Prometheus
  async getMetrics(): Promise<string> {
    return this.registry.metrics();
  }

  // Método para obtener estado de las métricas
  getMetricsStatus() {
    return {
      totalMetrics: this.registry.getMetricsAsArray().length,
      registeredMetrics: this.registry.getMetricsAsArray().map(metric => metric.name)
    };
  }

  // Método para reiniciar métricas
  resetMetrics() {
    this.registry.clear();
    this.onModuleInit();
  }

  // Método para registrar métricas personalizadas
  registerCustomMetric(metric: promClient.Metric) {
    this.registry.registerMetric(metric);
  }
}
