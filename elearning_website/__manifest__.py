# -*- coding: utf-8 -*-
{
    "name": "eLearning: Building Your Organization's Website",
    "version": "19.0.1.1.0",
    "category": "Website/eLearning",
    "summary": "eLearning course: a non-technical guide to Odoo's Website app",
    "description": """
eLearning: Building Your Organization's Website
==================================================

A short, self-contained eLearning course (Odoo's *eLearning* app) for a
non-technical person configuring their organization's public website -
opening the editor, building pages from blocks, menus and navigation,
publishing, and the handful of settings worth knowing early on. Install
this module and the course appears in eLearning already built - nothing
to author by hand.

Only depends on stock Odoo's ``website`` app - no custom module, no one
organization. Install it on any Odoo 19 Community instance.
""",
    "author": "Tiesa",
    "license": "LGPL-3",
    "website": "https://github.com/LadyHwesta/odoo-elearning",
    "depends": ["website_slides", "website"],
    "data": [
        "data/slide_channel_data.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "elearning_website/static/src/scss/course_content.scss",
        ],
    },
    "application": False,
}
