
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

import datetime
from openerp.osv import osv
from openerp.osv import fields
from openerp.tools.translate import _

class account_invoice(osv.osv):
    _inherit = 'account.invoice' 
    
    def _get_local_subtotal(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        for id in ids:
            result.setdefault(id, [])
        invoice_obj = self.pool.get('account.invoice')
        currency_obj = self.pool.get('res.currency')
        move_line_obj = self.pool.get('account.move.line')
        for id in ids:
            local_subtotal = 0
            total_debit = 0
            total_credit = 0
            result[id]=0
            invoice = invoice_obj.browse(cr,uid,id)
            context=dict(context)
            context.update({'date': invoice.date_invoice})
            #########Facture Client###########
            if invoice.type == 'out_invoice' :
                if invoice.state in ('draft','cancel','proforma'):
                    local_subtotal = currency_obj.compute(cr, uid, invoice.currency_id.id, invoice.company_id.currency_id.id,
                            invoice.amount_untaxed, context=context)
                    result[id]=local_subtotal
                if invoice.state in ('open','paid'):
                    move_line_ids = move_line_obj.search(cr,uid,[('move_id','=',invoice.move_id.id)])
                    for line in move_line_obj.browse(cr,uid,move_line_ids):
                        if line.account_id.type == 'receivable':  
                            total_debit += line.debit
                        if line.account_id.user_type.code == 'tax':  
                            total_credit += line.credit
                    result[id]=total_debit-total_credit
              #########Avoir Client###########
            if invoice.type == 'out_refund' :   
                if invoice.state in ('draft','cancel','proforma'):
                    local_subtotal = currency_obj.compute(cr, uid, invoice.currency_id.id, invoice.company_id.currency_id.id,
                            invoice.amount_untaxed, context=context)
                    result[id]=local_subtotal
                if invoice.state in ('open','paid'):
                    move_line_ids = move_line_obj.search(cr,uid,[('move_id','=',invoice.move_id.id)])
                    for line in move_line_obj.browse(cr,uid,move_line_ids):
                        if line.account_id.type == 'receivable':  
                            total_credit += line.credit
                        if line.account_id.user_type.code == 'tax':  
                            total_debit += line.debit
                    result[id]=total_credit-total_debit         
        
            #########Facture Fournisseur###########
            if invoice.type == 'in_invoice' :
                if invoice.state in ('draft','cancel','proforma'):
                    local_subtotal = currency_obj.compute(cr, uid, invoice.currency_id.id, invoice.company_id.currency_id.id,
                            invoice.amount_untaxed, context=context)
                    result[id]=local_subtotal
                if invoice.state in ('open','paid'):
                    move_line_ids = move_line_obj.search(cr,uid,[('move_id','=',invoice.move_id.id)])
                    for line in move_line_obj.browse(cr,uid,move_line_ids):
                        if line.account_id.type == 'payable':  
                            total_credit += line.credit
                        if line.account_id.user_type.code == 'tax':  
                            total_debit += line.debit
                    result[id]=total_credit-total_debit 
              #########Avoir Fournisseur###########
            if invoice.type == 'in_refund' :   
                if invoice.state in ('draft','cancel','proforma'):
                    local_subtotal = currency_obj.compute(cr, uid, invoice.currency_id.id, invoice.company_id.currency_id.id,
                            invoice.amount_untaxed, context=context)
                    result[id]=local_subtotal
                if invoice.state in ('open','paid'):
                    move_line_ids = move_line_obj.search(cr,uid,[('move_id','=',invoice.move_id.id)])
                    for line in move_line_obj.browse(cr,uid,move_line_ids):
                        if line.account_id.type == 'payable':  
                            total_debit += line.debit
                        if line.account_id.user_type.code == 'tax':  
                            total_credit += line.credit
                    result[id]=total_debit-total_credit    
                
                
        return result
    
    
    
    def _get_curency_rate(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        invoice_obj = self.pool.get('account.invoice')
        currency_obj = self.pool.get('res.currency')
        move_line_obj = self.pool.get('account.move.line')
        for id in ids:
            result[id]=1
            invoice = invoice_obj.browse(cr,uid,id)
            context=dict(context)
            context.update({'date': invoice.date_invoice})
            if invoice.currency_id.id != invoice.company_id.currency_id.id :
                if invoice.state in ('draft','cancel','proforma'):
                    result[id]=currency_obj.get_invoice_rate(cr,uid,invoice.currency_id.id, invoice.company_id.currency_id.id,
                                     context=context)
                else:
                    move_line_ids = move_line_obj.search(cr,uid,[('move_id','=',invoice.move_id.id)])
                    for line in move_line_obj.browse(cr,uid,move_line_ids):
                        if line.amount_currency != 0:
                            if line.credit != 0:
                                result[id] = abs(line.credit / line.amount_currency)
                                break
                            if line.debit != 0:
                                result[id] = abs(line.debit / line.amount_currency)
                                break
        return result
            
    def _get_curency_date(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        if not ids: return result
        invoice_obj = self.pool.get('account.invoice')
        currency_obj = self.pool.get('res.currency')
        currency_rate_obj = self.pool.get('res.currency.rate')
        move_obj = self.pool.get('account.move')
        for id in ids:
            result[id]=False
            invoice = invoice_obj.browse(cr,uid,id)
            context=dict(context)
            context.update({'date': invoice.date_invoice})
            if invoice.currency_id.id != invoice.company_id.currency_id.id :
                if invoice.state in ('draft','cancel','proforma'):
                    currency_rate_ids = currency_rate_obj.search(cr,uid,[('currency_id','=',invoice.currency_id.id)],order='name desc' ) 
                    if currency_rate_ids:
                        currency_rate= currency_rate_obj.browse(cr,uid,currency_rate_ids)
                        for obj in currency_rate:
                            if datetime.datetime.strptime(invoice.date_invoice, '%Y-%m-%d') > datetime.datetime.strptime(obj.name, '%Y-%m-%d %H:%M:%S'):
                                result[id]=obj.name
                                return result
                else:
                    move = move_obj.browse(cr,uid,invoice.move_id.id)
                    result[id]=move.date

        return result
    
    def test_currency_rate(self,cr, uid,inv_ids,context=None) :
        currency_rate_invisible = False
        for invoice in self.browse(cr, uid,inv_ids, context=context):
            currency_company_id = invoice.company_id.currency_id.id
            currency_id = invoice.currency_id.id
            if currency_company_id == currency_id :
                currency_rate_invisible = True
        return currency_rate_invisible

    def _get_currency_rate_invisible(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context=context):
            res[invoice.id] = self.test_currency_rate(cr, uid,[invoice.id])
        return res

    
    def _get_invoice_line2(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('account.invoice.line').browse(cr, uid, ids, context=context):
            result[line.invoice_id.id] = True
        return result.keys()
    
    def _get_invoice_tax2(self, cr, uid, ids, context=None):
        result = {}
        for tax in self.pool.get('account.invoice.tax').browse(cr, uid, ids, context=context):
            result[tax.invoice_id.id] = True
        return result.keys()
   
    _columns = {
                'local_subtotal': fields.function(_get_local_subtotal,type="float",  string='Sous total devise locale',
            # store={
            #     'account.invoice': (lambda self, cr, uid, ids, c={}: ids, ['amount_untaxed'], 30),
            #     'account.invoice.tax': (_get_invoice_tax2, None,30),
            #     'account.invoice.line': (_get_invoice_line2, ['price_unit','invoice_line_tax_id','quantity','discount','invoice_id'], 30),
            # }
            ),
            'currency_rate':fields.function(_get_curency_rate,type="float",string="Taux de change"),
            'company_id_currency':fields.related('company_id','currency_id',type='many2one',relation='res.currency',string="Devise de la société"),       
            'currency_date':fields.function(_get_curency_date,type="date",string="Date du taux de change"),  
            'currency_rate_invisible':fields.function(_get_currency_rate_invisible, type='boolean', string='Currency Rate visible?'),

                    }


account_invoice()

class res_currency(osv.osv):
 
    _inherit = "res.currency"
 
    def get_invoice_rate(self, cr, uid, from_currency_id, to_currency_id,
                round=True, currency_rate_type_from=False, currency_rate_type_to=False, context=None):
        if not context:
            context = {}
        if not from_currency_id:
            from_currency_id = to_currency_id
        if not to_currency_id:
            to_currency_id = from_currency_id
        xc = self.browse(cr, uid, [from_currency_id,to_currency_id], context=context)
        from_currency = (xc[0].id == from_currency_id and xc[0]) or xc[1]
        to_currency = (xc[0].id == to_currency_id and xc[0]) or xc[1]
        context.update({'currency_rate_type_from': currency_rate_type_from, 'currency_rate_type_to': currency_rate_type_to})
        rate = self._get_conversion_rate(cr, uid, from_currency, to_currency, context=context)
        return rate
        
res_currency()