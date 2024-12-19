import { Injectable, NotFoundException, Logger } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import * as bcrypt from 'bcrypt';
import { User, UserRole } from './entities/user.entity';
import { CreateUserDto } from './dto/create-user.dto';

@Injectable()
export class UserService {
  private readonly logger = new Logger(UserService.name);

  constructor(
    @InjectRepository(User)
    private userRepository: Repository<User>,
  ) {}

  async create(createUserDto: CreateUserDto): Promise<User> {
    const { email, password, role } = createUserDto;

    // Hash password
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);

    const user = this.userRepository.create({
      email,
      password: hashedPassword,
      role: role || UserRole.FREELANCE,
    });

    return this.userRepository.save(user);
  }

  async findByEmail(email: string): Promise<User | null> {
    return this.userRepository.findOne({ where: { email } });
  }

  async findById(id: string): Promise<User | null> {
    return this.userRepository.findOne({ where: { id } });
  }

  async saveRefreshToken(userId: string, refreshToken: string): Promise<void> {
    await this.userRepository.update(userId, { refreshToken });
  }

  async removeRefreshToken(userId: string): Promise<void> {
    await this.userRepository.update(userId, { refreshToken: null });
  }

  // Métodos para manejo de tokens push
  async obtenerTokensPush(usuarioId: string): Promise<string[]> {
    try {
      const usuario = await this.findById(usuarioId);
      if (!usuario) {
        this.logger.warn(`Usuario con ID ${usuarioId} no encontrado`);
        return [];
      }
      // Asumiendo que tienes un campo pushTokens en la entidad User
      return usuario.pushTokens || [];
    } catch (error) {
      this.logger.error(`Error obteniendo tokens push: ${error.message}`);
      return [];
    }
  }

  async agregarTokenPush(usuarioId: string, token: string): Promise<void> {
    try {
      const usuario = await this.findById(usuarioId);
      if (!usuario) {
        throw new NotFoundException(`Usuario con ID ${usuarioId} no encontrado`);
      }

      // Asegurarse de que no se agreguen tokens duplicados
      if (!usuario.pushTokens) {
        usuario.pushTokens = [];
      }
      
      if (!usuario.pushTokens.includes(token)) {
        usuario.pushTokens.push(token);
        await this.userRepository.save(usuario);
      }
    } catch (error) {
      this.logger.error(`Error agregando token push: ${error.message}`);
      throw error;
    }
  }

  async eliminarTokenPush(usuarioId: string, token: string): Promise<void> {
    try {
      const usuario = await this.findById(usuarioId);
      if (!usuario) {
        throw new NotFoundException(`Usuario con ID ${usuarioId} no encontrado`);
      }

      if (usuario.pushTokens) {
        usuario.pushTokens = usuario.pushTokens.filter(t => t !== token);
        await this.userRepository.save(usuario);
      }
    } catch (error) {
      this.logger.error(`Error eliminando token push: ${error.message}`);
      throw error;
    }
  }

  async eliminarTokensPush(tokensInvalidos: { token: string; error: any }[]): Promise<void> {
    try {
      for (const tokenInfo of tokensInvalidos) {
        const usuario = await this.userRepository.findOne({ 
          where: { pushTokens: tokenInfo.token } 
        });

        if (usuario) {
          usuario.pushTokens = usuario.pushTokens.filter(t => t !== tokenInfo.token);
          await this.userRepository.save(usuario);
        }
      }
    } catch (error) {
      this.logger.error(`Error eliminando tokens push inválidos: ${error.message}`);
      throw error;
    }
  }
}
