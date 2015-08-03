
# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _
import datetime

class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _get_local_subtotal(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            result.setdefault(id, [])
        sale_order_obj = self.pool.get('sale.order')
        currency_obj = self.pool.get('res.currency')
        company_id=self.pool.get('res.company').browse(cr,uid,1)
        for id in ids:
            local_subtotal = 0
            result[id]=0
            sale_order = sale_order_obj.browse(cr,uid,id)
            if sale_order.sale_order_currency_id.id :
                context=dict(context)
                context.update({'date': sale_order.date_order})
                local_subtotal = currency_obj.compute(cr, uid, sale_order.currency_id.id, company_id.currency_id.id,
                                sale_order.amount_untaxed, context=context)
                result[id]= local_subtotal
        return result


    def _get_curency_rate(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        order_obj = self.pool.get('sale.order')
        currency_obj = self.pool.get('res.currency')
        company_id=self.pool.get('res.company').browse(cr,uid,1)
        for id in ids:
            result[id]=1
            order = order_obj.browse(cr,uid,id)
            context=dict(context)
            context.update({'date': order.date_order})
            if order.currency_id.id != company_id.currency_id.id :
               result[id]=currency_obj.get_invoice_rate(cr,uid,order.currency_id.id, order.company_id.currency_id.id,
                                     context=context)

        return result

    def _get_curency_date(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        order_obj = self.pool.get('sale.order')
        currency_obj = self.pool.get('res.currency')
        currency_rate_obj = self.pool.get('res.currency.rate')
        company_id=self.pool.get('res.company').browse(cr,uid,1)
        for id in ids:
            result[id]=False
            order = order_obj.browse(cr,uid,id)
            if order.currency_id.id != company_id.currency_id.id :
                currency_rate_ids = currency_rate_obj.search(cr,uid,[('currency_id','=',order.currency_id.id)],order='name desc' )
                if currency_rate_ids:
                    currency_rate= currency_rate_obj.browse(cr,uid,currency_rate_ids)
                    for obj in currency_rate:
                        if datetime.datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S') > datetime.datetime.strptime(obj.name, '%Y-%m-%d %H:%M:%S'):
                            result[id]=obj.name
                            return result

        return result

    def test_currency_rate(self,cr, uid,inv_ids,context=None) :
        currency_rate_invisible = False
        for order in self.browse(cr, uid,inv_ids, context=context):
            currency_company_id = order.company_id.currency_id.id
            currency_id = order.currency_id.id
            if currency_company_id == currency_id :
                currency_rate_invisible = True
        return currency_rate_invisible

    def _get_currency_rate_invisible(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = self.test_currency_rate(cr, uid,[order.id])
        return res

    def onchange_pricelist_id(self, cr, uid, ids, pricelist_id, order_lines, context=None):
        context = context or {}
        if not pricelist_id:
            return {}
        currency_id=self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
        value = {
            'currency_id': currency_id,
            'sale_order_currency_id': currency_id
        }
        if not order_lines:
            return {'value': value}
        warning = {
            'title': _('Pricelist Warning!'),
            'message' : _('If you change the pricelist of this order (and eventually the currency), prices of existing order lines will not be updated.')
        }
        return {'warning': warning, 'value': value}

    _columns = {
            'company_id_currency':fields.related('company_id','currency_id',type='many2one',relation='res.currency',string="Devise de la société"),
            'sale_order_currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Devise(groupement)"),
            'local_subtotal':fields.function(_get_local_subtotal,type="float",string="Total H.T (devise locale)"),
            'currency_rate':fields.function(_get_curency_rate,type="float",string="Taux de change"),
            'currency_date':fields.function(_get_curency_date,type="date",string="Date du taux de change"),
            'currency_rate_invisible':fields.function(_get_currency_rate_invisible, type='boolean', string='Currency Rate visible?'),
                    }

sale_order()


class purchase_order(osv.osv):
    _inherit = 'purchase.order'

    def _get_local_subtotal(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            result.setdefault(id, [])
        order_obj = self.pool.get('purchase.order')
        currency_obj = self.pool.get('res.currency')
        company_id=self.pool.get('res.company').browse(cr,uid,1)
        for id in ids:
            local_subtotal = 0
            result[id]=0
            order = order_obj.browse(cr,uid,id)
            if order.order_currency_id.id :
                context=dict(context)
                context.update({'date': order.date_order})
                local_subtotal = currency_obj.compute(cr, uid, order.currency_id.id, company_id.currency_id.id,
                                order.amount_untaxed, context=context)
                result[id]= local_subtotal
        return result


    def _get_curency_rate(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        order_obj = self.pool.get('purchase.order')
        currency_obj = self.pool.get('res.currency')
        company_id=self.pool.get('res.company').browse(cr,uid,1)
        for id in ids:
            result[id]=1
            order = order_obj.browse(cr,uid,id)
            context=dict(context)
            context.update({'date': order.date_order})
            if order.currency_id.id != company_id.currency_id.id :
               result[id]=currency_obj.get_invoice_rate(cr,uid,order.currency_id.id, company_id.currency_id.id,
                                     context=context)

        return result

    def _get_curency_date(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        order_obj = self.pool.get('purchase.order')
        currency_obj = self.pool.get('res.currency')
        currency_rate_obj = self.pool.get('res.currency.rate')
        company_id=self.pool.get('res.company').browse(cr,uid,1)
        for id in ids:
            result[id]=False
            order = order_obj.browse(cr,uid,id)
            if order.currency_id.id != company_id.currency_id.id :
                currency_rate_ids = currency_rate_obj.search(cr,uid,[('currency_id','=',order.currency_id.id)],order='name desc' )
                if currency_rate_ids:
                    currency_rate= currency_rate_obj.browse(cr,uid,currency_rate_ids)
                    for obj in currency_rate:
                        if datetime.datetime.strptime(order.date_order, '%Y-%m-%d %H:%M:%S') > datetime.datetime.strptime(obj.name, '%Y-%m-%d %H:%M:%S'):
                            result[id]=obj.name
                            return result

        return result

    def test_currency_rate(self,cr, uid,inv_ids,context=None) :
        currency_rate_invisible = False
        for order in self.browse(cr, uid,inv_ids, context=context):
            currency_company_id = order.company_id.currency_id.id
            currency_id = order.currency_id.id
            if currency_company_id == currency_id :
                currency_rate_invisible = True
        return currency_rate_invisible

    def _get_currency_rate_invisible(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = self.test_currency_rate(cr, uid,[order.id])
        return res

    def onchange_pricelist(self, cr, uid, ids, pricelist_id, context=None):
        if not pricelist_id:
            return {}
        currency_id=self.pool.get('product.pricelist').browse(cr, uid, pricelist_id, context=context).currency_id.id
        return {'value': {'currency_id': currency_id, 'order_currency_id':currency_id}}


    _columns = {
            'company_id_currency':fields.related('company_id','currency_id',type='many2one',relation='res.currency',string="Devise de la société"),
            'order_currency_id': fields.related('pricelist_id', 'currency_id', type="many2one", relation="res.currency", string="Devise(groupement)",store=True),
			'local_subtotal':fields.function(_get_local_subtotal,type="float",string="Total H.T (devise locale)"),
			'currency_rate':fields.function(_get_curency_rate,type="float",string="Taux de change"),
            'currency_date':fields.function(_get_curency_date,type="date",string="Date du taux de change"),
            'currency_rate_invisible':fields.function(_get_currency_rate_invisible, type='boolean', string='Currency Rate visible?'),
                    }

purchase_order()