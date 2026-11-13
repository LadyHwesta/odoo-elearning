# -*- coding: utf-8 -*-
from odoo import models


class SlideChannelPartner(models.Model):
    _inherit = 'slide.channel.partner'

    def _post_completion_update_hook(self, completed=True):
        result = super()._post_completion_update_hook(completed=completed)
        if completed:
            assignments = self.env['slide.assignment'].sudo().search([
                ('channel_partner_id', 'in', self.ids)])
            assignments._close()
        return result
