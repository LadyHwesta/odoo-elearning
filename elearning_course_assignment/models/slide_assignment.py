# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.fields import Domain


class SlideAssignment(models.Model):
    """One course assigned to one learner by a team lead."""
    _name = 'slide.assignment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Course Assignment'
    _order = 'date_due, id desc'
    _rec_name = 'channel_id'

    team_id = fields.Many2one('slide.team', required=True, ondelete='cascade', index=True)
    channel_id = fields.Many2one('slide.channel', string="Course", required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string="Learner", required=True, index=True)
    assigned_by_id = fields.Many2one(
        'res.users', string="Assigned By", default=lambda self: self.env.user, readonly=True)
    date_assigned = fields.Date(default=fields.Date.context_today, readonly=True)
    date_due = fields.Date(string="Due", tracking=True)
    channel_partner_id = fields.Many2one('slide.channel.partner', readonly=True, ondelete='set null')
    completion = fields.Integer(
        string="% Done", related='channel_partner_id.completion', store=True)
    state = fields.Selection(
        [('assigned', "Not started"), ('in_progress', "In progress"), ('done', "Finished")],
        compute='_compute_state', store=True)
    is_overdue = fields.Boolean(compute='_compute_is_overdue', search='_search_is_overdue')
    reminder_sent = fields.Boolean(readonly=True, copy=False)

    @api.depends('completion')
    def _compute_state(self):
        for assignment in self:
            if assignment.completion >= 100:
                assignment.state = 'done'
            elif assignment.completion > 0:
                assignment.state = 'in_progress'
            else:
                assignment.state = 'assigned'

    @api.depends('date_due', 'state')
    def _compute_is_overdue(self):
        today = fields.Date.context_today(self)
        for assignment in self:
            assignment.is_overdue = bool(
                assignment.date_due and assignment.date_due < today and assignment.state != 'done')

    def _search_is_overdue(self, operator, value):
        if operator not in ('in', 'not in'):
            return NotImplemented
        domain = Domain([('state', '!=', 'done'),
                         ('date_due', '<', fields.Date.context_today(self))])
        return domain if (operator == 'in') == (True in value) else ~domain

    def _learner_user(self):
        """The learner's internal login, if they have one: to-dos only show
        up in the backend, so portal-only learners just get the emails."""
        self.ensure_one()
        return self.partner_id.user_ids.filtered(lambda u: not u.share)[:1]

    def _schedule_due_todo(self):
        todo = self.env.ref('mail.mail_activity_data_todo')
        for assignment in self.filtered(lambda a: a.date_due and a.state != 'done'):
            user = assignment._learner_user()
            if not user:
                continue
            assignment.activity_ids.filtered(
                lambda a: a.activity_type_id == todo and a.user_id == user).unlink()
            assignment.sudo().activity_schedule(
                'mail.mail_activity_data_todo', date_deadline=assignment.date_due,
                summary=_("Finish the course: %(course)s", course=assignment.channel_id.name),
                user_id=user.id)

    def _close(self):
        """The learner finished: close their to-do and tell the leads."""
        for assignment in self:
            assignment.sudo().activity_ids.action_feedback(feedback=_("Course finished."))
            assignment.sudo().message_post(
                body=_("%(learner)s finished %(course)s.",
                       learner=assignment.partner_id.name, course=assignment.channel_id.name),
                partner_ids=assignment.team_id.lead_ids.partner_id.ids,
                subtype_xmlid='mail.mt_note')

    def action_open_course(self):
        self.ensure_one()
        return {'type': 'ir.actions.act_url', 'url': f'/slides/{self.channel_id.id}', 'target': 'new'}

    @api.model
    def _cron_send_due_reminders(self):
        """On the due date, email every learner who hasn't finished yet. Once."""
        template = self.env.ref('elearning_course_assignment.mail_template_assignment_due')
        due = self.search([
            ('date_due', '<=', fields.Date.context_today(self)),
            ('state', '!=', 'done'), ('reminder_sent', '=', False),
            ('partner_id.email', '!=', False),
        ])
        for assignment in due:
            template.send_mail(assignment.id)
        due.write({'reminder_sent': True})
