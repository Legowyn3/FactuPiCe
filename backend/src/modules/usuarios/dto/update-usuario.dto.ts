import { OmitType, PartialType } from '@nestjs/mapped-types';
import { CreateUsuarioDto } from './create-usuario.dto';
import { IsString, MinLength, IsOptional, IsEmail } from 'class-validator';

export class UpdateUsuarioDto extends PartialType(CreateUsuarioDto) {
  @IsString()
  @MinLength(6)
  @IsOptional()
  password?: string = '';

  @IsEmail()
  @IsOptional()
  email?: string = '';

  constructor(partial: Partial<UpdateUsuarioDto> = {}) {
    super();
    Object.assign(this, partial);
  }
}