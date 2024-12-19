import { Injectable, Logger } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import * as nodemailer from 'nodemailer';
import * as handlebars from 'handlebars';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class EmailService {
  private readonly logger = new Logger(EmailService.name);
  private transporter: nodemailer.Transporter;

  constructor(
    private configService: ConfigService
  ) {
    this.inicializarTransporte();
  }

  private inicializarTransporte() {
    this.transporter = nodemailer.createTransport({
      host: this.configService.get('SMTP_HOST', 'smtp.gmail.com'),
      port: this.configService.get('SMTP_PORT', 587),
      secure: this.configService.get('SMTP_SECURE', false),
      auth: {
        user: this.configService.get('SMTP_USER'),
        pass: this.configService.get('SMTP_PASS')
      }
    });
  }

  private cargarPlantilla(nombrePlantilla: string, contexto: any): string {
    const rutaPlantilla = path.join(
      __dirname, 
      '..', 
      'templates', 
      `${nombrePlantilla}.hbs`
    );

    try {
      const contenidoPlantilla = fs.readFileSync(rutaPlantilla, 'utf8');
      const plantillaCompilada = handlebars.compile(contenidoPlantilla);
      return plantillaCompilada(contexto);
    } catch (error) {
      this.logger.error(`Error cargando plantilla ${nombrePlantilla}`, error);
      return '';
    }
  }

  async enviar(opciones: {
    to: string | string[];
    subject: string;
    template: string;
    context: Record<string, any>;
    attachments?: any[];
  }): Promise<void> {
    try {
      // Renderizar contenido HTML de la plantilla
      const htmlContent = this.cargarPlantilla(opciones.template, opciones.context);

      // Enviar email
      await this.transporter.sendMail({
        from: `"FactuPiCe" <${this.configService.get('SMTP_FROM', 'noreply@factupi.ce')}>`,
        to: opciones.to,
        subject: opciones.subject,
        html: htmlContent,
        attachments: opciones.attachments || []
      });

      this.logger.log(`Email enviado a ${opciones.to}`);
    } catch (error) {
      this.logger.error('Error enviando email', error);
      throw new Error(`Error al enviar email: ${error.message}`);
    }
  }

  // Método para enviar emails de prueba
  async enviarEmailPrueba(destinatario: string): Promise<void> {
    await this.enviar({
      to: destinatario,
      subject: 'Prueba de Email - FactuPiCe',
      template: 'prueba',
      context: {
        nombre: 'Usuario',
        fecha: new Date().toLocaleDateString()
      }
    });
  }
}
