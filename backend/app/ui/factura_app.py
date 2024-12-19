import streamlit as st
import sys
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='/home/piqueras/Documentos/Proyecto/streamlit_debug.log')

# Añadir el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database.database import SessionLocal, engine
from models.cliente import Cliente
from models.factura import Factura
from services.factura_service import FacturaService
from services.cliente_service import ClienteService
from schemas.factura import FacturaCreate, FacturaUpdate
from schemas.cliente import ClienteCreate

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def main():
    try:
        logging.info("Iniciando aplicación Streamlit")
        st.title("Gestión de Facturas")

        # Inicializar servicios
        db = next(get_db())
        factura_service = FacturaService(db)
        cliente_service = ClienteService(db)

        # Menú de navegación
        menu = st.sidebar.selectbox("Menú", 
            [
                "Crear Cliente", 
                "Crear Factura", 
                "Listar Facturas", 
                "Actualizar Factura", 
                "Firmar Factura", 
                "Enviar Factura por Email"
            ])

        if menu == "Crear Cliente":
            st.header("Crear Nuevo Cliente")
            nombre = st.text_input("Nombre")
            apellidos = st.text_input("Apellidos")
            nif_cif = st.text_input("NIF/CIF")
            email = st.text_input("Email")
            direccion = st.text_input("Dirección")

            if st.button("Crear Cliente"):
                cliente_data = ClienteCreate(
                    nombre=nombre,
                    apellidos=apellidos,
                    nif_cif=nif_cif,
                    email=email,
                    direccion=direccion
                )
                nuevo_cliente = cliente_service.crear_cliente(cliente_data)
                st.success(f"Cliente {nuevo_cliente.nombre} creado con ID: {nuevo_cliente.id}")

        elif menu == "Crear Factura":
            st.header("Crear Nueva Factura")
            
            # Obtener lista de clientes
            clientes = cliente_service.obtener_clientes()
            cliente_nombres = [f"{c.nombre} {c.apellidos} ({c.nif_cif})" for c in clientes]
            
            cliente_seleccionado = st.selectbox("Seleccionar Cliente", cliente_nombres)
            cliente_nif = cliente_seleccionado.split('(')[1].strip(')')
            cliente = cliente_service.obtener_cliente_por_nif(cliente_nif)

            base_imponible = st.number_input("Base Imponible", min_value=0.0, step=0.01)
            tipo_iva = st.selectbox("Tipo de IVA", [0.21, 0.10, 0.04])
            es_rectificativa = st.checkbox("Es Factura Rectificativa")

            if st.button("Crear Factura"):
                factura_data = FacturaCreate(
                    cliente_id=cliente.id,
                    base_imponible=base_imponible if not es_rectificativa else -base_imponible,
                    tipo_iva=tipo_iva,
                    es_rectificativa=es_rectificativa
                )
                nueva_factura = factura_service.crear_factura(factura_data)
                st.success(f"Factura creada con ID: {nueva_factura.id}")

        elif menu == "Listar Facturas":
            st.header("Listado de Facturas")
            facturas = factura_service.obtener_facturas()
            
            for factura in facturas:
                st.write(f"ID: {factura.id}")
                st.write(f"Cliente: {factura.cliente.nombre} {factura.cliente.apellidos}")
                st.write(f"Base Imponible: {factura.base_imponible}")
                st.write(f"Cuota IVA: {factura.cuota_iva}")
                st.write(f"Total: {factura.total_factura}")
                st.write(f"Estado: {factura.estado}")
                st.write("---")

        elif menu == "Actualizar Factura":
            st.header("Actualizar Factura")
            
            # Obtener lista de facturas
            facturas = factura_service.obtener_facturas()
            factura_ids = [f.id for f in facturas]
            
            factura_id = st.selectbox("Seleccionar Factura", factura_ids)
            
            base_imponible = st.number_input("Nueva Base Imponible", min_value=-10000.0, step=0.01)
            tipo_iva = st.selectbox("Nuevo Tipo de IVA", [0.21, 0.10, 0.04])

            if st.button("Actualizar Factura"):
                factura_data = FacturaUpdate(
                    base_imponible=base_imponible,
                    tipo_iva=tipo_iva
                )
                factura_actualizada = factura_service.actualizar_factura(factura_id, factura_data)
                st.success(f"Factura {factura_id} actualizada. Nuevo total: {factura_actualizada.total_factura}")

        elif menu == "Firmar Factura":
            st.header("Firmar Factura")
            
            # Obtener lista de facturas
            facturas = factura_service.obtener_facturas()
            factura_ids = [f.id for f in facturas]
            
            factura_id = st.selectbox("Seleccionar Factura", factura_ids)

            if st.button("Firmar Factura"):
                try:
                    factura_firmada = factura_service.firmar_factura(factura_id)
                    st.success(f"Factura {factura_id} firmada digitalmente")
                except Exception as e:
                    st.error(f"Error al firmar la factura: {e}")

        elif menu == "Enviar Factura por Email":
            st.header("Enviar Factura por Email")
            
            # Obtener lista de facturas
            facturas = factura_service.obtener_facturas()
            factura_ids = [f.id for f in facturas]
            
            factura_id = st.selectbox("Seleccionar Factura", factura_ids)

            if st.button("Enviar Factura"):
                try:
                    enviada = factura_service.enviar_factura_por_email(factura_id)
                    if enviada:
                        st.success(f"Factura {factura_id} enviada por email")
                    else:
                        st.warning(f"No se pudo enviar la factura {factura_id}")
                except Exception as e:
                    st.error(f"Error al enviar la factura: {e}")

    except Exception as e:
        logging.error(f"Error en la aplicación Streamlit: {e}", exc_info=True)
        st.error(f"Ha ocurrido un error: {e}")

if __name__ == "__main__":
    main()
