# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,api,fields
from odoo.exceptions import UserError

class mrp_process(models.Model):
    _name='mrp.proceso'
    _description='Procesamiento de ordenes'
    name=fields.Char("Nombre o Referencia")
    ultima=fields.Char("Ultima orden leida")
    ordenes=fields.One2many(comodel_name='mrp.proceso.line',inverse_name='proceso_id', string='Ordenes')
    tipo=fields.Selection([
        ('Ingreso','Ingreso'),
        ('Salida','Salida')], string='Tipo de operacion',required=True)
    
    
    @api.one
    def sh_on_barcode_scanned(self, barcode):
        proceso_id=self.id
        proceso=self.env['mrp.proceso'].search([('id', '=', proceso_id)],limit=1)
        if proceso:
            orden = self.env['mrp.production'].search([('origin', '=', barcode)],limit=1)
            if orden:
                if proceso.tipo=='Ingreso':
                    if orden.state=='confirmed':
                        if not orden.recibido_lab:
                            orden.recibido_lab=True
                            orden.action_toggle_is_locked()
                            self.env['mrp.proceso.line'].create({'name':barcode,'proceso_id':proceso.id,'production_id':orden.id})
                        else:
                            raise UserError('La orden ya fue recibida')
                    else:
                        raise UserError('La orden no esta en estado confirmada')
                if proceso.tipo=='Salida':
                    if orden.state=='progress':
                        orden.button_mark_done()
                        self.env['mrp.proceso.line'].create({'name':barcode,'proceso_id':proceso.id,'production_id':orden.id})
                    else:
                        raise UserError('La orden no esta en progreso')
            else:
                raise UserError('La orden no esta registrada')
        
    
class mrp_process_lie(models.Model):
    _name='mrp.proceso.line'
    _description='Linea de procesamiento de ordenes'
    name=fields.Char("Orden")
    proceso_id=fields.Many2one(comodel_name='mrp.proceso', string='Proceso')
    production_id=fields.Many2one(comodel_name='mrp.production', string='Orden de Produccion')
    sale_order=fields.Many2one(comodel_name='sale.order',related='production_id.x_sale_order_id', string='Orden de Venta')
    partner_id=fields.Many2one(comodel_name='res.partner',related='production_id.x_cliente', string='Cliente')
    paciente=fields.Char(string='Paciente',related='production_id.x_paciente')

class mrp_process_production(models.Model):
    _inherit='mrp.production'
    recibido_lab=fields.Boolean('Recibido en laboratorio')


class StockInventory(models.Model):
    _inherit='stock.inventory'
    last_product_id=fields.Many2one(comodel_name='product.product', string='ULTIMO PRODUCTO ESCANEADO')
    last_cantidad=fields.Integer("ULTIMA CANTIDAD LEIDA")

    @api.one
    def sh_on_barcode_scanned(self, barcode):

        inventory_id =self.id
        stock_inventory = self.env['stock.inventory'].search([('id', '=', inventory_id)],limit=1)

        if stock_inventory:
            product_id = self.env['product.product'].search([('barcode', '=', barcode)],limit=1)
            if not product_id:
                multi=self.env['product.multi.barcode'].search([('name', '=', barcode)],limit=1)
                if multi:
                    if multi.product_id:
                        product_id=self.env['product.product'].search([('id', '=', multi.product_id.id)],limit=1)

            if product_id:

                location_id = stock_inventory.location_id
                company = self.env.user.company_id
                warehouse = self.env['stock.warehouse'].search([('company_id', '=', company.id)], limit=1)

#                if warehouse:
#                    location_id = warehouse.lot_stock_id.id
#                else:
#                    raise UserError(_('You must define a warehouse for the company: %s.') % (company.name,))

                if not stock_inventory.line_ids:
                    inventory_line_val = {
                            'display_name': product_id.name,
                            'product_id': product_id.id,
                            'location_id':location_id,
                            'product_qty': 1,
                            'product_uom_id': product_id.product_tmpl_id.uom_id.id,
                            'inventory_id': stock_inventory.id
                    }
                    self.last_product_id=product_id.id
                    self.last_cantidad=1
                    stock_inventory.update({'line_ids': [(0, 0, inventory_line_val)]})

                else:
                    stock_picking_line = stock_inventory.line_ids.search([('product_id', '=', product_id.id),('inventory_id','=',inventory_id)], limit=1)
                    cantidad=1
                    if stock_picking_line:
                        stock_picking_line.product_qty += 1
                        cantidad=stock_picking_line.product_qty
                        self.last_product_id=product_id.id
                        self.last_cantidad=cantidad
                    else :
                        inventory_line_val = {
                            'display_name': product_id.name,
                            'product_id': product_id.id,
                            'location_id':location_id,
                            'product_qty': 1,
                            'product_uom_id': product_id.product_tmpl_id.uom_id.id,
                            'inventory_id': stock_inventory.id
                        }
                        self.last_product_id=product_id.id
                        self.last_cantidad=cantidad
                        stock_inventory.update({'line_ids': [(0, 0, inventory_line_val)]})
            else :
                raise UserError('Product does not exist')
