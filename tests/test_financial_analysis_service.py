import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.services.financial_analysis_service import FinancialAnalysisService
from app.models.factura import Factura
from app.models.cliente import Cliente
from app.core.database import SessionLocal

@pytest.fixture
def db_session():
    """Crear una sesión de base de datos para pruebas"""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def financial_analysis_service(db_session):
    """Crear instancia del servicio de análisis financiero"""
    return FinancialAnalysisService(db_session)

@pytest.mark.asyncio
async def test_total_revenue(financial_analysis_service, db_session):
    """Prueba el cálculo de ingresos totales"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Test Cliente")
    db_session.add(cliente)
    db_session.flush()

    facturas = [
        Factura(
            cliente_id=cliente.id, 
            total_factura=100.0, 
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente_id=cliente.id, 
            total_factura=200.0, 
            fecha_expedicion=datetime.now() - timedelta(days=15)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Ejecutar método
    start_date = datetime.now() - timedelta(days=45)
    end_date = datetime.now()
    total_revenue = await financial_analysis_service._total_revenue(start_date, end_date)

    # Verificar resultados
    assert total_revenue['total'] == 300.0
    assert total_revenue['average_invoice_value'] == 150.0
    assert total_revenue['total_invoices'] == 2

@pytest.mark.asyncio
async def test_revenue_by_invoice_type(financial_analysis_service, db_session):
    """Prueba el análisis de ingresos por tipo de factura"""
    # Preparar datos de prueba
    cliente = Cliente(nombre="Test Cliente")
    db_session.add(cliente)
    db_session.flush()

    facturas = [
        Factura(
            cliente_id=cliente.id, 
            total_factura=100.0, 
            tipo='NORMAL',
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente_id=cliente.id, 
            total_factura=200.0, 
            tipo='RECTIFICATIVA',
            fecha_expedicion=datetime.now() - timedelta(days=15)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Ejecutar método
    start_date = datetime.now() - timedelta(days=45)
    end_date = datetime.now()
    revenue_by_type = await financial_analysis_service._revenue_by_invoice_type(start_date, end_date)

    # Verificar resultados
    assert 'NORMAL' in revenue_by_type
    assert 'RECTIFICATIVA' in revenue_by_type
    assert revenue_by_type['NORMAL'] == 100.0
    assert revenue_by_type['RECTIFICATIVA'] == 200.0

@pytest.mark.asyncio
async def test_top_clients_by_revenue(financial_analysis_service, db_session):
    """Prueba obtención de clientes top por ingresos"""
    # Preparar datos de prueba
    clientes = [
        Cliente(nombre="Cliente 1"),
        Cliente(nombre="Cliente 2")
    ]
    db_session.add_all(clientes)
    db_session.flush()

    facturas = [
        Factura(
            cliente_id=clientes[0].id, 
            total_factura=500.0, 
            fecha_expedicion=datetime.now() - timedelta(days=30)
        ),
        Factura(
            cliente_id=clientes[0].id, 
            total_factura=300.0, 
            fecha_expedicion=datetime.now() - timedelta(days=15)
        ),
        Factura(
            cliente_id=clientes[1].id, 
            total_factura=200.0, 
            fecha_expedicion=datetime.now() - timedelta(days=10)
        )
    ]
    db_session.add_all(facturas)
    db_session.commit()

    # Ejecutar método
    start_date = datetime.now() - timedelta(days=45)
    end_date = datetime.now()
    top_clients = await financial_analysis_service._top_clients_by_revenue(start_date, end_date)

    # Verificar resultados
    assert len(top_clients) == 2
    assert top_clients[0]['name'] == 'Cliente 1'
    assert top_clients[0]['total_revenue'] == 800.0
    assert top_clients[0]['total_invoices'] == 2

@pytest.mark.asyncio
async def test_predict_future_revenue(financial_analysis_service, db_session):
    """Prueba predicción de ingresos futuros"""
    # Preparar datos históricos
    cliente = Cliente(nombre="Test Cliente")
    db_session.add(cliente)
    db_session.flush()

    # Crear facturas para los últimos 12 meses
    for i in range(12):
        factura = Factura(
            cliente_id=cliente.id, 
            total_factura=1000.0 + (i * 50),  # Variación ligera
            fecha_expedicion=datetime.now() - timedelta(days=30 * (12 - i))
        )
        db_session.add(factura)
    db_session.commit()

    # Ejecutar predicción
    prediction = await financial_analysis_service.predict_future_revenue()

    # Verificar resultados
    assert 'predictions' in prediction
    assert len(prediction['predictions']) == 3
    assert 'predicted_revenue' in prediction['predictions'][0]
    assert prediction['average_historical_revenue'] is not None

def test_generate_financial_report(financial_analysis_service):
    """Prueba generación de informe financiero"""
    # Ejecutar generación de informe
    report = financial_analysis_service.generate_financial_report()

    # Verificar estructura del informe
    assert 'dashboard' in report
    assert 'future_revenue_prediction' in report
    assert 'total_revenue' in report['dashboard']
    assert 'predictions' in report['future_revenue_prediction']

@pytest.mark.asyncio
async def test_advanced_revenue_prediction(financial_analysis_service, db_session):
    """Prueba predicción avanzada de ingresos"""
    # Preparar datos históricos
    cliente = Cliente(nombre="Test Cliente")
    db_session.add(cliente)
    db_session.flush()

    # Crear facturas para los últimos 12 meses con patrón de crecimiento
    for i in range(12):
        factura = Factura(
            cliente_id=cliente.id, 
            total_factura=1000.0 + (i * 100),  # Crecimiento gradual
            fecha_expedicion=datetime.now() - timedelta(days=30 * (12 - i))
        )
        db_session.add(factura)
    db_session.commit()

    # Probar diferentes modelos de predicción
    models = ['exponential_smoothing', 'arima', 'moving_average']
    
    for model_type in models:
        prediction = await financial_analysis_service.advanced_revenue_prediction(
            historical_months=12, 
            prediction_months=3, 
            model_type=model_type
        )

        # Verificaciones comunes
        assert 'predictions' in prediction
        assert len(prediction['predictions']) == 3
        assert 'predicted_revenue' in prediction['predictions'][0]
        assert 'confidence_interval' in prediction['predictions'][0]
        assert prediction['model_type'] == model_type

@pytest.mark.asyncio
async def test_risk_analysis(financial_analysis_service, db_session):
    """Prueba análisis de riesgo financiero"""
    # Preparar datos de prueba con múltiples clientes
    clientes = [
        Cliente(nombre=f"Cliente {i}") for i in range(5)
    ]
    db_session.add_all(clientes)
    db_session.flush()

    # Crear facturas con distribución variada
    facturas = []
    for i, cliente in enumerate(clientes):
        for j in range(3):  # 3 facturas por cliente
            factura = Factura(
                cliente_id=cliente.id, 
                total_factura=1000.0 * (i + 1),  # Variación entre clientes
                tipo='NORMAL' if j % 2 == 0 else 'RECTIFICATIVA',
                fecha_expedicion=datetime.now() - timedelta(days=30 * j)
            )
            facturas.append(factura)
    
    db_session.add_all(facturas)
    db_session.commit()

    # Ejecutar análisis de riesgo
    risk_analysis = await financial_analysis_service.risk_analysis()

    # Verificaciones
    assert 'client_concentration' in risk_analysis
    assert 'metrics' in risk_analysis['client_concentration']
    assert 'herfindahl_index' in risk_analysis['client_concentration']
    
    assert 'revenue_volatility' in risk_analysis
    assert 'standard_deviation' in risk_analysis['revenue_volatility']
    assert 'coefficient_of_variation' in risk_analysis['revenue_volatility']
    
    assert 'risk_score' in risk_analysis
    assert 'total_risk_score' in risk_analysis['risk_score']
    assert 'risk_level' in risk_analysis['risk_score']
    assert 'components' in risk_analysis['risk_score']

def test_risk_score_calculation(financial_analysis_service):
    """Prueba cálculo de puntuación de riesgo"""
    # Datos de ejemplo para prueba
    concentration_metrics = [
        {'name': 'Cliente 1', 'revenue_share': 60.0, 'invoice_count': 10},
        {'name': 'Cliente 2', 'revenue_share': 20.0, 'invoice_count': 5}
    ]
    revenue_volatility = {
        'coefficient_of_variation': 0.5
    }
    revenue_by_invoice_type = {
        'NORMAL': 5000,
        'RECTIFICATIVA': 2000
    }

    # Método privado de cálculo de riesgo
    risk_score = financial_analysis_service._calculate_risk_score(
        concentration_metrics, 
        revenue_volatility, 
        revenue_by_invoice_type
    )

    # Verificaciones
    assert 'total_risk_score' in risk_score
    assert 'risk_level' in risk_score
    assert 'components' in risk_score
    assert 0 <= risk_score['total_risk_score'] <= 100

    # Verificar niveles de riesgo
    assert risk_score['risk_level'] in ['BAJO', 'MEDIO', 'ALTO']
