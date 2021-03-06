# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError

class TemporaryExemption(models.TransientModel):
    _name = 'beesdoo.shift.temporary_exemption'
    _inherit = 'beesdoo.shift.action_mixin'

    temporary_exempt_reason_id = fields.Many2one('cooperative.exempt.reason', 'Exempt Reason', required=True)
    temporary_exempt_start_date = fields.Date(default=fields.Date.today, required=True)
    temporary_exempt_end_date = fields.Date(required=True)

    @api.multi
    def exempt(self):
        self = self._check() #maybe a different group
        status_id = self.env['cooperative.status'].search([('cooperator_id', '=', self.cooperator_id.id)])
        if status_id.temporary_exempt_end_date >= status_id.today:
            raise ValidationError(_("You cannot encode new temporary exemptuon since the previous one are not over yet"))
        status_id.sudo().write({
            'temporary_exempt_start_date': self.temporary_exempt_start_date,
            'temporary_exempt_end_date': self.temporary_exempt_end_date,
            'temporary_exempt_reason_id': self.temporary_exempt_reason_id.id,
        })
        self.env['beesdoo.shift.shift'].sudo().unsubscribe_from_today([self.cooperator_id.id], today=self.temporary_exempt_start_date, end_date=self.temporary_exempt_end_date)
