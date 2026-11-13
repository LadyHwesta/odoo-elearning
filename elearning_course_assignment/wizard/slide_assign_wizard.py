# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError

OFFICER = 'website_slides.group_website_slides_officer'


class SlideAssignWizard(models.TransientModel):
    _name = 'slide.assign.wizard'
    _description = 'Assign Courses to a Team'

    team_id = fields.Many2one('slide.team', required=True)
    team_member_ids = fields.Many2many(related='team_id.member_ids')
    channel_ids = fields.Many2many(
        'slide.channel', string="Courses", required=True,
        domain="[('is_published', '=', True)]")
    partner_ids = fields.Many2many(
        'res.partner', string="Assign To",
        compute='_compute_partner_ids', store=True, readonly=False,
        help="Everyone on the team by default.")
    date_due = fields.Date(string="Due")
    send_email = fields.Boolean(
        string="Email Them", default=True,
        help="Odoo's own enrolment email, with a link to the course.")

    @api.depends('team_id')
    def _compute_partner_ids(self):
        for wizard in self:
            wizard.partner_ids = wizard.team_id.member_ids

    def _check_can_assign(self):
        if self.env.user.has_group(OFFICER):
            return
        if self.env.user not in self.team_id.lead_ids:
            raise AccessError(_("Only a lead of %(team)s can assign its courses.",
                                team=self.team_id.name))
        outsiders = self.partner_ids - self.team_id.member_ids
        if outsiders:
            raise AccessError(_(
                "%(names)s isn't on %(team)s. Add them to the team first.",
                names=", ".join(outsiders.mapped('name')), team=self.team_id.name))
        unpublished = self.channel_ids.filtered(lambda c: not c.is_published)
        if unpublished:
            raise UserError(_("%(courses)s isn't published yet.",
                              courses=", ".join(unpublished.mapped('name'))))

    def action_assign(self):
        self.ensure_one()
        if not self.partner_ids:
            raise UserError(_("Choose who to assign the courses to."))
        self._check_can_assign()
        if self.send_email and not self.env.user.email:
            raise UserError(_("Your user has no email address to send from. Add one in "
                              "your preferences, or untick Email Them."))
        Assignment = self.env['slide.assignment'].sudo()
        changed = Assignment
        for channel in self.channel_ids.sudo():
            open_ones = Assignment.search([
                ('channel_id', '=', channel.id), ('partner_id', 'in', self.partner_ids.ids),
                ('state', '!=', 'done')])
            if self.date_due:
                open_ones.write({'date_due': self.date_due, 'reminder_sent': False})
            changed |= open_ones
            new_partners = self.partner_ids - open_ones.partner_id
            if not new_partners:
                continue
            self._enroll(channel, new_partners)
            members = self.env['slide.channel.partner'].sudo().search([
                ('channel_id', '=', channel.id), ('partner_id', 'in', new_partners.ids)])
            by_partner = {m.partner_id.id: m for m in members}
            changed |= Assignment.create([{
                'team_id': self.team_id.id,
                'channel_id': channel.id,
                'partner_id': partner.id,
                'assigned_by_id': self.env.user.id,
                'date_due': self.date_due,
                'channel_partner_id': by_partner[partner.id].id if partner.id in by_partner else False,
            } for partner in new_partners])
        changed.message_subscribe(partner_ids=self.team_id.lead_ids.partner_id.ids)
        changed._schedule_due_todo()
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _("Courses assigned"),
                'message': _("%(count)s assignment(s) for %(team)s.",
                             count=len(changed), team=self.team_id.name),
                'type': 'success',
                'next': {'type': 'ir.actions.act_window_close'},
            },
        }

    def _enroll(self, channel, partners):
        """Enroll through Odoo's own Add Attendees wizard, so they get its
        usual email. Run as superuser: a lead isn't the course's
        responsible, which core requires; _check_can_assign has already
        checked what a lead may do."""
        if not self.send_email:
            channel._action_add_members(partners)
            return
        template = self.env.ref('website_slides.mail_template_slide_channel_enroll',
                                raise_if_not_found=False)
        context = channel._action_channel_open_invite_wizard(template, enroll_mode=True)['context']
        invite = self.env['slide.channel.invite'].sudo().with_context(context).create({
            'channel_id': channel.id,
            'partner_ids': [(6, 0, partners.ids)],
        })
        invite.action_invite()
