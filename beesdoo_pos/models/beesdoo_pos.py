# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class BeesPOS(models.Model):
    _inherit = 'pos.config'

    bill_value = fields.One2many('bill_value', 'pos')
    
class BillValue(models.Model):
    _name = 'bill_value'
    _order = 'name asc'

    name = fields.Float(string='Name')
    pos = fields.Many2one('pos.config')

class BeesAccountBankStatement(models.Model):
    _inherit = 'account.bank.statement.cashbox'

    def _get_default_line(self):
        if not self.env.context.get('active_id'):
            return []

        pos_session_rec = self.env['pos.session'].browse(self.env.context['active_id'])
        return [(0, 0, {'coin_value' : bill_value_rec.name}) for bill_value_rec in pos_session_rec.config_id.bill_value]

    cashbox_lines_ids = fields.One2many(default=_get_default_line)

class BeescoopPosOrder(models.Model):

    _inherit = 'pos.order'

    @api.model
    def send_order(self, receipt_name):
        order = self.search([('pos_reference', '=', receipt_name)])
        if not order:
            return _('Error: no order found')
        if not order.partner_id.email:
            return _('Cannot send the ticket, no email address found on the client')
        mail_template = self.env.ref("beesdoo_pos.email_send_ticket")
        mail_template.send_mail(order.id)
        return _("Ticket sent")

class BeescoopPosPartner(models.Model):
    _inherit = 'res.partner'

    def _get_eater(self):
        eater1, eater2 = False, False
        if self.child_eater_ids:
            eater1 = self.child_eater_ids[0].name
        if len(self.child_eater_ids) > 1:
            eater2 = self.child_eater_ids[1].name
        return eater1, eater2

    @api.multi
    def get_balance_and_eater(self):
        self.ensure_one()
        self = self.sudo()
        account_id = self.property_account_receivable_id.id
        move_lines = self.env['account.move.line'].search([('account_id', '=', account_id), ('partner_id', '=', self.id)])
        credit = sum([m.credit for m in move_lines])
        debit = sum([m.debit for m in move_lines])
        eater1, eater2 = self._get_eater()
        return str(round(credit - debit, 2)), eater1, eater2

    last_name = fields.Char('Last Name', required=True, default="/")
