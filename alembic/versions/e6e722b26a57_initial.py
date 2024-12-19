"""initial

Revision ID: e6e722b26a57
Revises: 
Create Date: 2024-12-19 22:09:11.694075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6e722b26a57'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('clientes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nif_cif', sa.String(), nullable=False),
    sa.Column('nombre', sa.String(), nullable=False),
    sa.Column('nombre_comercial', sa.String(), nullable=True),
    sa.Column('direccion', sa.String(), nullable=False),
    sa.Column('codigo_postal', sa.String(), nullable=False),
    sa.Column('ciudad', sa.String(), nullable=False),
    sa.Column('provincia', sa.String(), nullable=False),
    sa.Column('pais', sa.String(), nullable=False),
    sa.Column('telefono', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('activo', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_clientes_id'), 'clientes', ['id'], unique=False)
    op.create_index(op.f('ix_clientes_nif_cif'), 'clientes', ['nif_cif'], unique=True)
    op.create_table('usuarios',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('nombre', sa.String(), nullable=True),
    sa.Column('hashed_password', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_admin', sa.Boolean(), nullable=True),
    sa.Column('apellidos', sa.String(), nullable=True),
    sa.Column('telefono', sa.String(), nullable=True),
    sa.Column('mfa_secret', sa.String(length=32), nullable=True),
    sa.Column('mfa_enabled', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
    op.create_table('facturas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serie', sa.String(length=4), nullable=False),
    sa.Column('numero', sa.String(), nullable=False),
    sa.Column('fecha_expedicion', sa.DateTime(), nullable=False),
    sa.Column('fecha_operacion', sa.Date(), nullable=True),
    sa.Column('cliente_id', sa.Integer(), nullable=False),
    sa.Column('base_imponible', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('tipo_iva', sa.Float(), nullable=False),
    sa.Column('cuota_iva', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('tipo_retencion', sa.Float(), nullable=True),
    sa.Column('retencion', sa.Numeric(precision=10, scale=2), nullable=True),
    sa.Column('total_factura', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.Column('concepto', sa.String(), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('tipo', sa.Enum('ordinaria', 'rectificativa', 'simplificada', 'recapitulativa', name='tipofactura'), nullable=False),
    sa.Column('estado', sa.Enum('borrador', 'emitida', 'pagada', 'vencida', 'cancelada', name='estadofactura'), nullable=False),
    sa.Column('factura_original_id', sa.Integer(), nullable=True),
    sa.Column('motivo_rectificacion', sa.Text(), nullable=True),
    sa.Column('periodo_recapitulativo', sa.String(), nullable=True),
    sa.Column('fecha_vencimiento', sa.Date(), nullable=True),
    sa.Column('metodo_pago', sa.String(), nullable=True),
    sa.Column('cuenta_bancaria', sa.String(), nullable=True),
    sa.Column('archivo_adjunto', sa.Text(), nullable=True),
    sa.Column('notas', sa.Text(), nullable=True),
    sa.Column('firma_digital', sa.Text(), nullable=True),
    sa.Column('tbai_identifier', sa.String(), nullable=True),
    sa.Column('previous_invoice_hash', sa.String(), nullable=True),
    sa.Column('invoice_hash', sa.String(), nullable=True),
    sa.Column('qr_code', sa.Text(), nullable=True),
    sa.Column('xml_content', sa.Text(), nullable=True),
    sa.Column('signature', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('software_name', sa.String(), nullable=False),
    sa.Column('software_version', sa.String(), nullable=False),
    sa.Column('software_license', sa.String(), nullable=False),
    sa.Column('hash_fiscal', sa.String(length=64), nullable=True),
    sa.Column('is_deleted', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('verifactu_version', sa.String(), nullable=False),
    sa.Column('verifactu_timestamp', sa.DateTime(timezone=True), nullable=True),
    sa.Column('verifactu_validation_code', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
    sa.ForeignKeyConstraint(['factura_original_id'], ['facturas.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero'),
    sa.UniqueConstraint('tbai_identifier')
    )
    op.create_index(op.f('ix_facturas_id'), 'facturas', ['id'], unique=False)
    op.create_table('detalles_factura',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('factura_id', sa.Integer(), nullable=True),
    sa.Column('descripcion', sa.String(length=200), nullable=False),
    sa.Column('cantidad', sa.Float(), nullable=False),
    sa.Column('precio_unitario', sa.Float(), nullable=False),
    sa.Column('tipo_iva', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['factura_id'], ['facturas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('detalles_factura')
    op.drop_index(op.f('ix_facturas_id'), table_name='facturas')
    op.drop_table('facturas')
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_email'), table_name='usuarios')
    op.drop_table('usuarios')
    op.drop_index(op.f('ix_clientes_nif_cif'), table_name='clientes')
    op.drop_index(op.f('ix_clientes_id'), table_name='clientes')
    op.drop_table('clientes')
    # ### end Alembic commands ###