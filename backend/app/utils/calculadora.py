from decimal import Decimal, ROUND_HALF_UP

def calcular_totales(
    base_imponible: Decimal,
    tipo_iva: Decimal,
    tipo_retencion: Decimal = Decimal('0')
) -> dict:
    """
    Calcula los totales de una factura usando Decimal para mayor precisión.
    """
    # Validaciones
    if base_imponible < 0:
        raise ValueError("La base imponible no puede ser negativa")
    if not 0 <= tipo_iva <= 100:
        raise ValueError("El tipo de IVA debe estar entre 0 y 100")
    if not 0 <= tipo_retencion <= 100:
        raise ValueError("El tipo de retención debe estar entre 0 y 100")

    # Convertir porcentajes a decimales
    iva_decimal = tipo_iva / Decimal('100')
    retencion_decimal = tipo_retencion / Decimal('100')
    
    # Calcular importes
    cuota_iva = (base_imponible * iva_decimal).quantize(
        Decimal('0.01'), 
        rounding=ROUND_HALF_UP
    )
    retencion = (base_imponible * retencion_decimal).quantize(
        Decimal('0.01'), 
        rounding=ROUND_HALF_UP
    )
    total_factura = (base_imponible + cuota_iva - retencion).quantize(
        Decimal('0.01'), 
        rounding=ROUND_HALF_UP
    )
    
    return {
        "cuota_iva": cuota_iva,
        "retencion": retencion,
        "total_factura": total_factura
    }
