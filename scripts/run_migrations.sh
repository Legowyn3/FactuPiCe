#!/bin/bash

# Activar el entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Ejecutar las migraciones
echo "Ejecutando migraciones..."
python scripts/migrations/01_add_clientes.py

# Verificar el resultado
if [ $? -eq 0 ]; then
    echo "✅ Migraciones completadas exitosamente"
else
    echo "❌ Error al ejecutar las migraciones"
    exit 1
fi
