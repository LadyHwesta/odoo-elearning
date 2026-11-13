# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged("post_install", "-at_install")
class TestCourseAssignment(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, mail_create_nolog=True))
        cls.chair = new_test_user(cls.env, login="chair", name="Committee Chair",
                                  email="chair@example.com", groups="base.group_user")
        cls.staff = new_test_user(cls.env, login="staff", name="Staff Member",
                                  email="staff@example.com", groups="base.group_user")
        cls.volunteer = cls.env["res.partner"].create(
            {"name": "Volunteer", "email": "vol@example.com"})
        cls.outsider = cls.env["res.partner"].create(
            {"name": "Outsider", "email": "out@example.com"})
        cls.course = cls.env["slide.channel"].create({
            "name": "Event Safety", "is_published": True,
            "visibility": "members", "enroll": "invite",
        })
        cls.lesson = cls.env["slide.slide"].create({
            "name": "Fire exits", "channel_id": cls.course.id,
            "slide_category": "article", "is_published": True,
        })
        cls.team = cls.env["slide.team"].create({
            "name": "Events Committee", "lead_ids": [(6, 0, cls.chair.ids)],
            "member_ids": [(6, 0, (cls.staff.partner_id | cls.volunteer).ids)],
        })
        cls.due = fields.Date.today() + timedelta(days=14)

    def _assign(self, user=None, **vals):
        wizard = self.env["slide.assign.wizard"].with_user(user or self.chair).create(dict({
            "team_id": self.team.id, "channel_ids": [(6, 0, self.course.ids)],
            "date_due": self.due, "send_email": False,
        }, **vals))
        wizard.action_assign()
        return self.env["slide.assignment"].search([("team_id", "=", self.team.id)])

    def test_becoming_a_lead_grants_access(self):
        self.assertTrue(self.chair.has_group(
            "elearning_course_assignment.group_learning_team_lead"))
        self.assertFalse(self.chair.has_group("website_slides.group_website_slides_officer"))

    def test_lead_sees_members_only_courses(self):
        self.assertIn(self.course, self.env["slide.channel"].with_user(self.chair).search([]))

    def test_lead_enrolls_the_whole_team(self):
        assignments = self._assign()
        self.assertEqual(assignments.partner_id, self.staff.partner_id | self.volunteer)
        enrolled = self.course.channel_partner_ids.filtered(
            lambda m: m.member_status != "invited").partner_id
        self.assertLessEqual(self.staff.partner_id | self.volunteer, enrolled)
        self.assertTrue(all(assignments.mapped("channel_partner_id")))
        self.assertEqual(set(assignments.mapped("state")), {"assigned"})

    def test_lead_cannot_assign_outside_the_team(self):
        with self.assertRaises(AccessError):
            self._assign(partner_ids=[(6, 0, self.outsider.ids)])

    def test_someone_else_cannot_assign_for_the_team(self):
        with self.assertRaises(AccessError):
            self._assign(user=self.staff)

    def test_staff_with_a_login_get_a_todo(self):
        assignments = self._assign()
        staff = assignments.filtered(lambda a: a.partner_id == self.staff.partner_id)
        volunteer = assignments - staff
        self.assertEqual(staff.activity_ids.user_id, self.staff)
        self.assertEqual(staff.activity_ids.date_deadline, self.due)
        self.assertFalse(volunteer.activity_ids)

    def test_assigning_again_moves_the_due_date(self):
        self._assign()
        later = self.due + timedelta(days=7)
        assignments = self._assign(date_due=later)
        self.assertEqual(len(assignments), 2)
        self.assertEqual(set(assignments.mapped("date_due")), {later})

    def test_finishing_closes_the_todo(self):
        assignments = self._assign()
        staff = assignments.filtered(lambda a: a.partner_id == self.staff.partner_id)
        self.lesson.with_user(self.staff).sudo()._action_mark_completed()
        self.assertEqual(staff.state, "done")
        self.assertEqual(staff.completion, 100)
        self.assertFalse(staff.activity_ids)

    def test_overdue_filter(self):
        assignments = self._assign(date_due=fields.Date.today() - timedelta(days=1))
        overdue = self.env["slide.assignment"].search(
            [("is_overdue", "=", True), ("id", "in", assignments.ids)])
        self.assertEqual(overdue, assignments)

    def test_due_reminder_is_sent_once(self):
        assignments = self._assign(date_due=fields.Date.today())
        self.env["slide.assignment"]._cron_send_due_reminders()
        self.assertTrue(all(assignments.mapped("reminder_sent")))
        reminders = [("model", "=", "slide.assignment"), ("res_id", "in", assignments.ids),
                     ("subject", "like", "Reminder:")]
        self.assertEqual(self.env["mail.mail"].search_count(reminders), 2)
        self.env["slide.assignment"]._cron_send_due_reminders()
        self.assertEqual(self.env["mail.mail"].search_count(reminders), 2)

    def test_lead_sees_progress_learner_sees_own(self):
        self._assign()
        self.assertEqual(
            len(self.env["slide.assignment"].with_user(self.chair).search([])), 2)
        own = self.env["slide.assignment"].with_user(self.staff).search([])
        self.assertEqual(own.partner_id, self.staff.partner_id)

    def test_email_them_uses_odoos_enrolment_email(self):
        assignments = self._assign(send_email=True)
        self.assertEqual(len(assignments), 2)
        sent_to = self.env["mail.mail"].search(
            [("subject", "like", self.course.name), ("model", "=", False)]).recipient_ids
        self.assertLessEqual(self.staff.partner_id | self.volunteer, sent_to)
