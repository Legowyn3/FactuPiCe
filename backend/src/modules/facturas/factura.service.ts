import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Factura } from './entities/factura.entity';
import { CreateFacturaDto, UpdateFacturaDto } from './dto';
import { FacturaMapper } from './mappers/factura.mapper';
import { PdfService } from '../common/services/pdf.service';
import { EmailService } from '../common/services/email.service';

@Injectable()
export class FacturaService {
  constructor(
    @InjectRepository(Factura)
    private facturaRepository: Repository<Factura>,
    private pdfService: PdfService,
    private emailService: EmailService,
    private facturaMapper: FacturaMapper
  ) {}

  async create(dto: CreateFacturaDto) {
    const factura = this.facturaMapper.toEntity(dto);
    const saved = await this.facturaRepository.save(factura);
    
    // Generar PDF
    const pdf = await this.pdfService.generateInvoicePdf(saved);
    
    // Enviar email si se requiere
    if (dto.sendEmail) {
      await this.emailService.sendInvoice(saved, pdf);
    }

    return this.facturaMapper.toDto(saved);
  }

  // ... otros métodos
} 