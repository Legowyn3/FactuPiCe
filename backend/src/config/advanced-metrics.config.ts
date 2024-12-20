import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Gauge, Registry } from 'prom-client';
import { Cliente } from '../modules/clientes/entities/cliente.entity';
import { Factura } from '../modules/facturas/entities/factura.entity';

@Injectable()
export class AdvancedMetricsService {
  private clienteTotalGauge: Gauge;
  private clienteWithFacturasGauge: Gauge;
  private clienteFacturaTotalGauge: Gauge;

  constructor(
    @InjectRepository(Cliente)
    private clientesRepository: Repository<Cliente>,
    @InjectRepository(Factura)
    private facturasRepository: Repository<Factura>,
    private registry: Registry
  ) {
    this.initMetrics();
  }

  private initMetrics() {
    this.clienteTotalGauge = new Gauge({
      name: 'factupicev2_cliente_total',
      help: 'Número total de clientes',
      registers: [this.registry]
    });

    this.clienteWithFacturasGauge = new Gauge({
      name: 'factupicev2_cliente_with_facturas',
      help: 'Número de clientes con facturas',
      registers: [this.registry]
    });

    this.clienteFacturaTotalGauge = new Gauge({
      name: 'factupicev2_cliente_factura_total',
      help: 'Número total de facturas por cliente',
      labelNames: ['cliente_id'],
      registers: [this.registry]
    });
  }

  async updateMetrics() {
    try {
      // Total de clientes
      const totalClientes = await this.clientesRepository.count();
      this.clienteTotalGauge.set(totalClientes);

      // Clientes con facturas
      const clientesWithFacturas = await this.clientesRepository
        .createQueryBuilder('cliente')
        .leftJoinAndSelect('cliente.facturas', 'facturas')
        .where('facturas.id IS NOT NULL')
        .getCount();
      
      this.clienteWithFacturasGauge.set(clientesWithFacturas);

      // Facturas por cliente
      const clientesWithFacturaDetails = await this.clientesRepository
        .createQueryBuilder('cliente')
        .leftJoinAndSelect('cliente.facturas', 'facturas')
        .getMany();

      clientesWithFacturaDetails.forEach(cliente => {
        this.clienteFacturaTotalGauge
          .labels({ cliente_id: cliente.id })
          .set(cliente.facturas?.length || 0);
      });
    } catch (error) {
      console.error('Error actualizando métricas:', error);
    }
  }

  // Método para actualizar métricas periódicamente
  async startMetricsCollection() {
    // Actualizar cada 5 minutos
    setInterval(async () => {
      await this.updateMetrics();
    }, 5 * 60 * 1000);

    // Primera actualización inmediata
    await this.updateMetrics();
  }
}
