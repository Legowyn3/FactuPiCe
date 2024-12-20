import { 
  IsString, 
  IsEmail, 
  IsOptional, 
  Length, 
  Matches, 
  IsPhoneNumber 
} from 'class-validator';
import { ApiPropertyOptional } from '@nestjs/swagger';
import { CreateClienteDto } from './create-cliente.dto';

export class UpdateClienteDto {
  @ApiPropertyOptional({ 
    description: 'Nombre del cliente', 
    example: 'Juan Pérez García' 
  })
  @IsOptional()
  @IsString({ message: 'El nombre debe ser una cadena de texto' })
  @Length(2, 100, { message: 'El nombre debe tener entre 2 y 100 caracteres' })
  nombre?: string;

  @ApiPropertyOptional({ 
    description: 'NIF o CIF del cliente', 
    example: '12345678A' 
  })
  @IsOptional()
  @Matches(/^[0-9]{8}[A-Z]$/, { 
    message: 'El NIF/CIF debe tener 8 dígitos seguidos de una letra mayúscula' 
  })
  nif?: string;

  @ApiPropertyOptional({ 
    description: 'Correo electrónico del cliente', 
    example: 'juan.perez@ejemplo.com' 
  })
  @IsOptional()
  @IsEmail({}, { message: 'Debe ser un email válido' })
  @Length(5, 100, { message: 'El email debe tener entre 5 y 100 caracteres' })
  email?: string;

  @ApiPropertyOptional({ 
    description: 'Número de teléfono', 
    example: '+34666123456' 
  })
  @IsOptional()
  @IsPhoneNumber('ES', { message: 'Debe ser un número de teléfono español válido' })
  telefono?: string;

  @ApiPropertyOptional({ 
    description: 'Dirección completa', 
    example: 'Calle Mayor, 123, 28000 Madrid' 
  })
  @IsOptional()
  @IsString({ message: 'La dirección debe ser una cadena de texto' })
  @Length(10, 200, { message: 'La dirección debe tener entre 10 y 200 caracteres' })
  direccion?: string;

  @ApiPropertyOptional({ 
    description: 'Notas adicionales sobre el cliente', 
    example: 'Cliente habitual, prefiere facturación electrónica' 
  })
  @IsOptional()
  @IsString({ message: 'Las notas deben ser una cadena de texto' })
  @Length(0, 500, { message: 'Las notas no pueden exceder 500 caracteres' })
  notas?: string;
}
