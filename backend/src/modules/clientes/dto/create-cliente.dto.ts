import { 
  IsString, 
  IsEmail, 
  IsOptional, 
  IsNotEmpty, 
  Length 
} from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';
import { IsValidNifCif } from '../../../common/validators/nif-cif.validator';

export class CreateClienteDto {
  @ApiProperty({ 
    description: 'Nombre del cliente', 
    example: 'Juan Pérez García' 
  })
  @IsNotEmpty({ message: 'El nombre no puede estar vacío' })
  @IsString({ message: 'El nombre debe ser una cadena de texto' })
  @Length(2, 100, { message: 'El nombre debe tener entre 2 y 100 caracteres' })
  nombre: string;

  @ApiProperty({ 
    description: 'NIF, CIF o NIE del cliente', 
    example: '12345678A' 
  })
  @IsNotEmpty({ message: 'El NIF/CIF/NIE no puede estar vacío' })
  @IsValidNifCif({ message: 'El NIF/CIF/NIE no es válido' })
  nif: string;

  @ApiProperty({ 
    description: 'Correo electrónico del cliente', 
    example: 'juan.perez@ejemplo.com' 
  })
  @IsEmail({}, { message: 'Debe ser un email válido' })
  @Length(5, 100, { message: 'El email debe tener entre 5 y 100 caracteres' })
  email: string;

  @ApiProperty({ 
    description: 'Número de teléfono', 
    example: '+34666123456' 
  })
  @IsString({ message: 'El teléfono debe ser una cadena de texto' })
  @Length(9, 15, { message: 'El teléfono debe tener entre 9 y 15 caracteres' })
  telefono: string;

  @ApiProperty({ 
    description: 'Dirección completa', 
    example: 'Calle Mayor, 123, 28000 Madrid' 
  })
  @IsNotEmpty({ message: 'La dirección no puede estar vacía' })
  @IsString({ message: 'La dirección debe ser una cadena de texto' })
  @Length(10, 200, { message: 'La dirección debe tener entre 10 y 200 caracteres' })
  direccion: string;

  @ApiProperty({ 
    description: 'Notas adicionales sobre el cliente', 
    example: 'Cliente habitual, prefiere facturación electrónica',
    required: false 
  })
  @IsOptional()
  @IsString({ message: 'Las notas deben ser una cadena de texto' })
  @Length(0, 500, { message: 'Las notas no pueden exceder 500 caracteres' })
  notas?: string;
}
