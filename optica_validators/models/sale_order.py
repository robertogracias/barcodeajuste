# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.

from odoo import models,api,fields
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta
import threading



class ref_partner(models.Model):
    _inherit='sale.order'
    
    @api.constrains('od_prisma','oi_prisma','x_od_prisma_dir','x_oi_prisma_dir')
    def check_prisma(self):
        for r in self:
            if r.od_prisma!=0:
                if not r.x_od_prisma_dir:
                    raise UserError('Debe especificarse la direccion del prisma de OD')
            if r.oi_prisma!=0:
                if not r.x_oi_prisma_dir:
                    raise UserError('Debe especificarse la direccion del prisma de OI')
            if r.x_od_prisma_dir:
                if not r.od_prisma!=0:
                    raise UserError('Debe especificarse un valor del prisma de OD')
            if r.x_oi_prisma_dir:
                if not r.oi_prisma!=0:
                    raise UserError('Debe especificarse un valor del prisma de OI')
    
    @api.constrains('od_adicion','oi_adicion','x_ap','x_dp')
    def check_adicion(self):
        for r in self:
            validar=False
            if r.od_adicion!=0:
                validar=True
            if r.oi_adicion!=0:
                validar=True
            if validar==True:
                cumple=False
                if r.x_ap:
                    cumple=True
                if r.x_ao:
                    cumple=True
                if not cumple:
                    raise UserError('Debe especificarse AP o DP')
    
    
    @api.constrains('x_od_cilindro','x_oi_cilindro','od_eje','oi_eje')
    def check_cilindro(self):
        for r in self:
            if r.x_od_cilindro:
                if not r.od_eje:
                    raise UserError('Debe especificarse EJE OD')
            if r.x_oi_cilindro:
                if not r.oi_eje:
                    raise UserError('Debe especificarse EJE OI')
            if r.od_eje:
                if not r.x_od_cilindro:
                    raise UserError('Debe especificarse CILINDRO OD')
            if r.oi_eje:
                if not r.x_oi_cilindro:
                    raise UserError('Debe especificarse CILINDOR OI')
            
                
                
