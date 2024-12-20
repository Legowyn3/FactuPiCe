import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as nodemailer from 'nodemailer';
import { Factura } from '../../modules/facturas/entities/factura.entity';

@Injectable()
export class EmailService {
  private transporter: nodemailer.Transporter;

  constructor(private configService: ConfigService) {
    this.transporter = nodemailer.createTransport({
      host: this.configService.get('SMTP_HOST'),
      port: this.configService.get('SMTP_PORT'),
      secure: true,
      auth: {
        user: this.configService.get('SMTP_USER'),
        pass: this.configService.get('SMTP_PASS')
      }
    });
  }

  async sendInvoice(factura: Factura, pdfBuffer: Buffer) {
    await this.transporter.sendMail({
      from: this.configService.get('SMTP_FROM'),
      to: factura.cliente.email,
      subject: `Factura ${factura.numero}`,
      text: `Adjuntamos la factura ${factura.numero}`,
      attachments: [{
        filename: `factura-${factura.numero}.pdf`,
        content: pdfBuffer
      }]
    });
  }
} 