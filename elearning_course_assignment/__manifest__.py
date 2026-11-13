# -*- coding: utf-8 -*-
{
    "name": "eLearning: Assign Courses to a Team",
    "version": "19.0.1.0.0",
    "category": "Website/eLearning",
    "summary": "Team leads assign courses to their team, with due dates, reminders and progress",
    "description": """
eLearning: Assign Courses to a Team
====================================

A manager or committee chair assigns eLearning courses to the people on
their team, without being an eLearning administrator.

* **Learning Teams** (eLearning > Assignments > Teams): a team has one or
  more leads and its members (any contacts: staff, volunteers, committee
  members). Making someone a lead gives them the *Team Lead* access level.
* **Assign Courses** from a team: pick published courses, the members
  (all by default), a due date, and whether to email them. They are
  enrolled straight away, with Odoo's own enrolment email.
* **Reminders**: a learner with an Odoo login gets a to-do due on that
  date; everyone still unfinished on the due date is emailed a reminder.
  Finishing the course closes the to-do.
* **Progress**: leads see each assignment, its % done, and which are
  finished or overdue.

A Team Lead can assign any published course, but only to members of
teams they lead, and can't edit courses. eLearning Officers and
Administrators can do everything a lead can, for every team.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/odoo-elearning",
    "depends": ["website_slides", "mail"],
    "data": [
        "security/elearning_course_assignment_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "data/ir_cron_data.xml",
        "wizard/slide_assign_wizard_views.xml",
        "views/slide_team_views.xml",
        "views/slide_assignment_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
}
