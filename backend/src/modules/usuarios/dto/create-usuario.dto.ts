import { IsString, IsEmail, MinLength, IsOptional } from 'class-validator';

export class CreateUsuarioDto {
  @IsString()
  nombre: string = '';

  @IsEmail()
  email: string = '';

  @IsString()
  @MinLength(6)
  password: string = '';

  @IsString()
  @IsOptional()
  nif?: string;

  @IsString()
  @IsOptional()
  direccion?: string;

  @IsString()
  @IsOptional()
  telefono?: string;

  constructor(partial: Partial<CreateUsuarioDto> = {}) {
    Object.assign(this, partial);
  }
} 