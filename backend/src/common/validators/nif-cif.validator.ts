import { 
  registerDecorator, 
  ValidationOptions, 
  ValidatorConstraint, 
  ValidatorConstraintInterface 
} from 'class-validator';

@ValidatorConstraint({ name: 'isValidNifCif', async: false })
export class IsValidNifCifConstraint implements ValidatorConstraintInterface {
  validate(value: string): boolean {
    if (!value) return false;

    const nifRegex = /^[0-9]{8}[A-Z]$/;
    const cifRegex = /^[A-HJPQSUV][0-9]{7}[A-J]$/;
    const nieRegex = /^[XYZ][0-9]{7}[A-Z]$/;

    if (nifRegex.test(value)) {
      return this.validateNIF(value);
    }

    if (cifRegex.test(value)) {
      return this.validateCIF(value);
    }

    if (nieRegex.test(value)) {
      return this.validateNIE(value);
    }

    return false;
  }

  private validateNIF(nif: string): boolean {
    const numbers = nif.substring(0, 8);
    const letter = nif[8];
    const validLetters = 'TRWAGMYFPDXBNJZSQVHLCKE';
    const expectedLetter = validLetters[parseInt(numbers) % 23];
    return letter === expectedLetter;
  }

  private validateCIF(cif: string): boolean {
    const controlDigit = cif[8];
    const firstChar = cif[0];
    const digits = cif.substring(1, 8).split('').map(Number);

    let sum = 0;
    for (let i = 0; i < digits.length; i++) {
      const digit = digits[i];
      sum += i % 2 === 0 
        ? digit * 2 > 9 
          ? digit * 2 - 9 
          : digit * 2 
        : digit;
    }

    const controlNumber = (10 - (sum % 10)) % 10;
    const validControlChars = 'JABCDEFGHI';

    return firstChar.match(/[PQSNW]/) 
      ? controlDigit === String(controlNumber) 
      : controlDigit === validControlChars[controlNumber];
  }

  private validateNIE(nie: string): boolean {
    const prefixMap = { 'X': '0', 'Y': '1', 'Z': '2' };
    const mappedNie = prefixMap[nie[0]] + nie.substring(1, 8);
    const validLetters = 'TRWAGMYFPDXBNJZSQVHLCKE';
    const expectedLetter = validLetters[parseInt(mappedNie) % 23];
    return nie[8] === expectedLetter;
  }

  defaultMessage(): string {
    return 'El NIF/CIF/NIE no es válido';
  }
}

export function IsValidNifCif(validationOptions?: ValidationOptions) {
  return function (object: object, propertyName: string) {
    registerDecorator({
      target: object.constructor,
      propertyName: propertyName,
      options: validationOptions,
      constraints: [],
      validator: IsValidNifCifConstraint,
    });
  };
}
