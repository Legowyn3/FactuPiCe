import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication, ValidationPipe } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';
import { CreateClienteDto } from '../src/modules/clientes/dto/create-cliente.dto';
import { UpdateClienteDto } from '../src/modules/clientes/dto/update-cliente.dto';

describe('ClientesController (e2e)', () => {
  let app: INestApplication;
  let createdClienteId: string;
  let authToken: string;

  const mockCliente: CreateClienteDto = {
    nombre: 'Cliente de Prueba',
    nif: '12345678A',
    email: 'cliente.prueba@example.com',
    telefono: '+34666123456',
    direccion: 'Calle de Prueba, 123',
    notas: 'Cliente de prueba para tests'
  };

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.useGlobalPipes(new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: true,
      transform: true,
    }));
    await app.init();

    // Autenticación para pruebas
    const loginResponse = await request(app.getHttpServer())
      .post('/auth/login')
      .send({
        username: 'admin', // Ajusta con credenciales de prueba
        password: 'admin123'
      });
    
    authToken = loginResponse.body.access_token;
  });

  afterAll(async () => {
    await app.close();
  });

  describe('Crear Cliente', () => {
    it('(POST) /clientes - crear cliente con datos válidos', async () => {
      const response = await request(app.getHttpServer())
        .post('/api/v1/clientes')
        .set('Authorization', `Bearer ${authToken}`)
        .send(mockCliente)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.nombre).toBe(mockCliente.nombre);
      createdClienteId = response.body.id;
    });

    it('(POST) /clientes - fallar al crear cliente con datos inválidos', async () => {
      const invalidCliente = { ...mockCliente, email: 'invalid-email' };
      await request(app.getHttpServer())
        .post('/api/v1/clientes')
        .set('Authorization', `Bearer ${authToken}`)
        .send(invalidCliente)
        .expect(400);
    });

    it('(POST) /clientes - fallar al crear cliente con NIF duplicado', async () => {
      await request(app.getHttpServer())
        .post('/api/v1/clientes')
        .set('Authorization', `Bearer ${authToken}`)
        .send(mockCliente)
        .expect(400);
    });
  });

  describe('Obtener Clientes', () => {
    it('(GET) /clientes - listar clientes con paginación', async () => {
      const response = await request(app.getHttpServer())
        .get('/api/v1/clientes')
        .set('Authorization', `Bearer ${authToken}`)
        .query({ page: 1, limit: 10 })
        .expect(200);

      expect(response.body).toHaveProperty('data');
      expect(response.body).toHaveProperty('total');
      expect(response.body).toHaveProperty('page');
      expect(response.body).toHaveProperty('totalPages');
    });

    it('(GET) /clientes/:id - obtener cliente por ID', async () => {
      const response = await request(app.getHttpServer())
        .get(`/api/v1/clientes/${createdClienteId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      expect(response.body).toHaveProperty('id', createdClienteId);
      expect(response.body.nombre).toBe(mockCliente.nombre);
    });
  });

  describe('Actualizar Cliente', () => {
    it('(PATCH) /clientes/:id - actualizar cliente', async () => {
      const updateData: UpdateClienteDto = { 
        nombre: 'Cliente Actualizado',
        telefono: '+34777654321'
      };

      const response = await request(app.getHttpServer())
        .patch(`/api/v1/clientes/${createdClienteId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send(updateData)
        .expect(200);

      expect(response.body.nombre).toBe(updateData.nombre);
      expect(response.body.telefono).toBe(updateData.telefono);
    });

    it('(PATCH) /clientes/:id - fallar al actualizar con NIF duplicado', async () => {
      // Crear otro cliente primero
      const otroCliente = await request(app.getHttpServer())
        .post('/api/v1/clientes')
        .set('Authorization', `Bearer ${authToken}`)
        .send({
          nombre: 'Otro Cliente',
          nif: '87654321B',
          email: 'otro.cliente@example.com',
          telefono: '+34666789012',
          direccion: 'Otra Calle, 456'
        });

      // Intentar actualizar NIF a uno existente
      await request(app.getHttpServer())
        .patch(`/api/v1/clientes/${createdClienteId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .send({ nif: '87654321B' })
        .expect(400);
    });
  });

  describe('Eliminar Cliente', () => {
    it('(DELETE) /clientes/:id - eliminar cliente', async () => {
      await request(app.getHttpServer())
        .delete(`/api/v1/clientes/${createdClienteId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(200);

      // Intentar obtener el cliente eliminado debe fallar
      await request(app.getHttpServer())
        .get(`/api/v1/clientes/${createdClienteId}`)
        .set('Authorization', `Bearer ${authToken}`)
        .expect(404);
    });
  });
});
