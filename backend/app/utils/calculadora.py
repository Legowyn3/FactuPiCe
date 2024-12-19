def calcular_totales(base_imponible: float, tipo_iva: float, tipo_retencion: float = 0):
    """
    Calcula los totales de una factura.
    
    Args:
        base_imponible (float): Base imponible de la factura
        tipo_iva (float): Porcentaje de IVA (ej: 21 para 21%)
        tipo_retencion (float, optional): Porcentaje de retención (ej: 15 para 15%)
    
    Returns:
        dict: Diccionario con los valores calculados
    """
    # Convertir porcentajes a decimales
    iva_decimal = tipo_iva / 100
    retencion_decimal = tipo_retencion / 100 if tipo_retencion else 0
    
    # Calcular IVA
    cuota_iva = base_imponible * iva_decimal
    
    # Calcular retención si aplica
    retencion = base_imponible * retencion_decimal if tipo_retencion else 0
    
    # Calcular total
    total_factura = base_imponible + cuota_iva - retencion
    
    return {
        "cuota_iva": round(cuota_iva, 2),
        "retencion": round(retencion, 2),
        "total_factura": round(total_factura, 2)
    }
