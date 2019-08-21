# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models, fields, api, _
from odoo.exceptions import Warning, UserError

class StockInventory(models.Model):
    _name = "stock.inventory"
    _inherit = ['barcodes.barcode_events_mixin', 'stock.inventory']
    
    def _add_product(self, barcode):
        #step 1: state validation.
        if self and self.state != 'confirm':
            selections = self.fields_get()['state']['selection']
            value = next((v[1] for v in selections if v[0] == self.state), self.state)
            raise UserError(_("You can not scan item in %s state.") %(value))
        
        elif self:
            search_lines = False
            domain = []
            
            if self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_type == 'barcode':
                search_lines = self.line_ids.filtered(lambda l: l.product_id.barcode == barcode)
                domain = [("barcode","=",barcode)]
            
            elif self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_type == 'int_ref':
                search_lines = self.line_ids.filtered(lambda l: l.product_id.default_code == barcode)
                domain = [("default_code","=",barcode)]
            
            elif self.env.user.company_id.sudo().sh_inven_adjt_barcode_scanner_type == 'both':
                search_lines = self.line_ids.filtered(lambda l: l.product_id.barcode == barcode or l.product_id.default_code == barcode)
                domain = ["|",
                    ("default_code","=",barcode),
                    ("barcode","=",barcode)
                ]              
            
            if search_lines:
                for line in search_lines:
                    line.product_qty += 1
                    break
            else:
                search_product = self.env["product.product"].search(domain, limit = 1)
                if search_product:                    
                    inventory_line_val = {
                            'display_name': search_product.name,
                            'product_id': search_product.id,
                            'location_id':self.location_id.id,   
                            'product_qty': 1,
                            'inventory_id': self.id
                    }
                    if search_product.uom_id:
                        inventory_line_val.update({
                            'product_uom_id': search_product.uom_id.id,                            
                            })
                    self.env["stock.inventory.line"].new(inventory_line_val)                               
  
                else:
                    raise UserError(_("Scanned Internal Reference/Barcode not exist in any product!"))         
            
    def on_barcode_scanned(self, barcode):  
        self._add_product(barcode)                      

                    