import { Injectable } from '@nestjs/common';
import { Factura } from '../../modules/facturas/entities/factura.entity';
import PDFDocument from 'pdfkit';
import { Buffer } from 'buffer';

interface PDFContent {
  text: string;
  x: number;
  y: number;
  options?: PDFKit.Mixins.TextOptions;
}

@Injectable()
export class PdfService {
  async generateInvoicePdf(factura: Factura): Promise<Buffer> {
    return new Promise((resolve) => {
      const doc = new PDFDocument();
      const chunks: Buffer[] = [];

      doc.on('data', (chunk: Buffer) => chunks.push(chunk));
      doc.on('end', () => resolve(Buffer.concat(chunks)));

      // Generar PDF
      this.buildInvoicePdf(doc, factura);

      doc.end();
    });
  }

  private buildInvoicePdf(doc: PDFKit.PDFDocument, factura: Factura): void {
    // Cabecera
    this.addHeader(doc, factura);
    
    // Datos del cliente
    this.addClientInfo(doc, factura);
    
    // Tabla de conceptos
    this.addConceptosTable(doc, factura);
    
    // Totales
    this.addTotales(doc, factura);
    
    // Pie de página
    this.addFooter(doc, factura);
  }

  private addHeader(doc: PDFKit.PDFDocument, factura: Factura): void {
    doc.fontSize(25)
       .text('Factura', 50, 50)
       .fontSize(12)
       .text(`Número: ${factura.numero}`, 50, 90)
       .text(`Fecha: ${factura.fecha.toLocaleDateString()}`, 50, 110);
  }

  private addClientInfo(doc: PDFKit.PDFDocument, factura: Factura): void {
    doc.fontSize(12)
       .text('Datos del Cliente:', 50, 150)
       .text(`Nombre: ${factura.cliente.nombre}`, 50, 170)
       .text(`NIF/CIF: ${factura.cliente.nif}`, 50, 190)
       .text(`Dirección: ${factura.cliente.direccion}`, 50, 210);
  }

  private addConceptosTable(doc: PDFKit.PDFDocument, factura: Factura): void {
    const tableTop = 250;
    const rowHeight = 30;

    // Cabecera de la tabla
    doc.fontSize(10)
       .text('Descripción', 50, tableTop)
       .text('Cantidad', 300, tableTop)
       .text('Precio', 380, tableTop)
       .text('Subtotal', 460, tableTop);

    // Línea separadora
    doc.moveTo(50, tableTop + 15)
       .lineTo(550, tableTop + 15)
       .stroke();

    // Contenido de la tabla
    let currentY = tableTop + 30;
    factura.conceptos.forEach(concepto => {
      doc.text(concepto.descripcion, 50, currentY)
         .text(concepto.cantidad.toString(), 300, currentY)
         .text(concepto.precioUnitario.toFixed(2) + ' €', 380, currentY)
         .text((concepto.cantidad * concepto.precioUnitario).toFixed(2) + ' €', 460, currentY);
      
      currentY += rowHeight;
    });
  }

  private addTotales(doc: PDFKit.PDFDocument, factura: Factura): void {
    const startY = 600;
    
    doc.fontSize(10)
       .text('Subtotal:', 380, startY)
       .text(`${factura.subtotal.toFixed(2)} €`, 460, startY)
       .text(`IVA (${factura.iva}%)`, 380, startY + 20)
       .text(`${(factura.subtotal * factura.iva / 100).toFixed(2)} €`, 460, startY + 20)
       .text(`Retención (${factura.retencion}%)`, 380, startY + 40)
       .text(`${(factura.subtotal * factura.retencion / 100).toFixed(2)} €`, 460, startY + 40)
       .fontSize(12)
       .text('Total:', 380, startY + 70)
       .text(`${factura.total.toFixed(2)} €`, 460, startY + 70);
  }

  private addFooter(doc: PDFKit.PDFDocument, factura: Factura): void {
    const pageHeight = doc.page.height;
    
    doc.fontSize(8)
       .text('Este documento es una factura electrónica.', 50, pageHeight - 50)
       .text(`Generada el ${new Date().toLocaleDateString()}`, 50, pageHeight - 35);
  }
} 