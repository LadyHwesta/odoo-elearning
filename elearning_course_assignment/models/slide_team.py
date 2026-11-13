# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

LEAD_GROUP = 'elearning_course_assignment.group_learning_team_lead'


class SlideTeam(models.Model):
    """A group of people whose training one or more leads look after:
    a department, a committee, a volunteer crew."""
    _name = 'slide.team'
    _inherit = ['mail.thread']
    _description = 'Learning Team'
    _order = 'name'

    name = fields.Char(required=True, tracking=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    description = fields.Text()
    lead_ids = fields.Many2many(
        'res.users', 'slide_team_lead_rel', 'team_id', 'user_id', string="Leads",
        domain="[('share', '=', False)]", tracking=True,
        help="Who assigns courses to this team: a manager or committee chair. "
             "Leads get the eLearning 'Team Lead' access level automatically.")
    member_ids = fields.Many2many(
        'res.partner', 'slide_team_member_rel', 'team_id', 'partner_id', string="Members",
        help="Anyone with a contact: staff, volunteers, committee members. "
             "They need a login (internal or portal) to take a course.")
    member_count = fields.Integer(compute='_compute_counts')
    assignment_ids = fields.One2many('slide.assignment', 'team_id')
    assignment_count = fields.Integer(compute='_compute_counts')

    @api.depends('member_ids', 'assignment_ids')
    def _compute_counts(self):
        for team in self:
            team.member_count = len(team.member_ids)
            team.assignment_count = len(team.assignment_ids)

    @api.model_create_multi
    def create(self, vals_list):
        teams = super().create(vals_list)
        teams._grant_lead_access()
        return teams

    def write(self, vals):
        result = super().write(vals)
        if 'lead_ids' in vals:
            self._grant_lead_access()
        return result

    def _grant_lead_access(self):
        group = self.env.ref(LEAD_GROUP)
        users = self.lead_ids.filtered(lambda u: group not in u.all_group_ids)
        if users:
            users.sudo().write({'group_ids': [(4, group.id)]})

    def action_assign_courses(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _("Assign Courses to %(team)s", team=self.name),
            'res_model': 'slide.assign.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_team_id': self.id},
        }

    def action_view_assignments(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id(
            'elearning_course_assignment.action_slide_assignment')
        action['domain'] = [('team_id', '=', self.id)]
        action['context'] = {'default_team_id': self.id}
        return action
