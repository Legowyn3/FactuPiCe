import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { CreateClienteDto } from '../src/modules/clientes/dto/create-cliente.dto';

describe('ClientesController Performance Tests', () => {
  let app: INestApplication;
  let authToken: string;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    // Autenticación
    const loginResponse = await request(app.getHttpServer())
      .post('/auth/login')
      .send({
        username: 'admin',
        password: 'admin123'
      });
    
    authToken = loginResponse.body.access_token;
  });

  afterAll(async () => {
    await app.close();
  });

  describe('Rendimiento de Creación de Clientes', () => {
    const baseCliente: CreateClienteDto = {
      nombre: 'Cliente de Prueba',
      nif: '12345678A',
      email: 'cliente.prueba@example.com',
      telefono: '+34666123456',
      direccion: 'Calle de Prueba, 123'
    };

    it('Crear 100 clientes en serie', async () => {
      const startTime = Date.now();
      
      for (let i = 0; i < 100; i++) {
        const cliente = { 
          ...baseCliente, 
          nif: `1234567${i}A`,
          email: `cliente.prueba${i}@example.com`
        };

        await request(app.getHttpServer())
          .post('/api/v1/clientes')
          .set('Authorization', `Bearer ${authToken}`)
          .send(cliente)
          .expect(201);
      }

      const totalTime = Date.now() - startTime;
      console.log(`Tiempo total para crear 100 clientes: ${totalTime}ms`);
      expect(totalTime).toBeLessThan(10000); // Menos de 10 segundos
    }, 20000);

    it('Crear 100 clientes en paralelo', async () => {
      const startTime = Date.now();
      
      const promises = Array.from({ length: 100 }, (_, i) => {
        const cliente = { 
          ...baseCliente, 
          nif: `9876543${i}A`,
          email: `cliente.paralelo${i}@example.com`
        };

        return request(app.getHttpServer())
          .post('/api/v1/clientes')
          .set('Authorization', `Bearer ${authToken}`)
          .send(cliente)
          .expect(201);
      });

      await Promise.all(promises);

      const totalTime = Date.now() - startTime;
      console.log(`Tiempo total para crear 100 clientes en paralelo: ${totalTime}ms`);
      expect(totalTime).toBeLessThan(5000); // Menos de 5 segundos
    }, 10000);
  });

  describe('Pruebas de Carga y Estrés', () => {
    it('Búsqueda de clientes con paginación bajo carga', async () => {
      const concurrentRequests = 50;
      const startTime = Date.now();

      const promises = Array.from({ length: concurrentRequests }, () => 
        request(app.getHttpServer())
          .get('/api/v1/clientes')
          .set('Authorization', `Bearer ${authToken}`)
          .query({ page: 1, limit: 10 })
          .expect(200)
      );

      const responses = await Promise.all(promises);

      const totalTime = Date.now() - startTime;
      console.log(`Tiempo total para ${concurrentRequests} búsquedas: ${totalTime}ms`);

      // Verificar que todas las respuestas tengan la estructura esperada
      responses.forEach(response => {
        expect(response.body).toHaveProperty('data');
        expect(response.body).toHaveProperty('total');
        expect(response.body).toHaveProperty('page');
        expect(response.body).toHaveProperty('totalPages');
      });

      // Tiempo promedio por solicitud no debe superar 200ms
      const averageResponseTime = totalTime / concurrentRequests;
      expect(averageResponseTime).toBeLessThan(200);
    }, 15000);
  });

  describe('Pruebas de Consistencia', () => {
    it('Verificar integridad de datos después de múltiples operaciones', async () => {
      // Crear un cliente
      const createResponse = await request(app.getHttpServer())
        .post('/api/v1/clientes')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          nombre: 'Cliente de Prueba Consistencia',
          nif: '11111111A',
          email: 'cliente.consistencia@example.com',
          telefono: '+34666111222',
          direccion: 'Calle Consistencia, 1'
        })
        .expect(201);

      const clienteId = createResponse.body.id;

      // Actualizar cliente
      const updateResponse = await request(app.getHttpServer())
        .patch(`/api/v1/clientes/${clienteId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ telefono: '+34777333444' })
        .expect(200);

      expect(updateResponse.body.telefono).toBe('+34777333444');

      // Obtener cliente y verificar
      const getResponse = await request(app.getHttpServer())
        .get(`/api/v1/clientes/${clienteId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(getResponse.body.telefono).toBe('+34777333444');
    });
  });
});
