# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import Command
from odoo.tests import Form
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon


class TestHrHolidaysCalendarPlanning(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        resource_calendar = cls.env["resource.calendar"]
        cls.calendar1 = resource_calendar.create(
            {"name": "Test calendar 1", "attendance_ids": []}
        )
        cls.calendar2 = resource_calendar.create(
            {"name": "Test calendar 2", "attendance_ids": []}
        )
        for day in range(5):  # From monday to friday
            cls.calendar1.attendance_ids = [
                Command.create(
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "08",
                        "hour_to": "12",
                    },
                ),
                Command.create(
                    {
                        "name": "Attendance",
                        "dayofweek": str(day),
                        "hour_from": "13",
                        "hour_to": "17",
                    },
                ),
            ]
            cls.calendar2.attendance_ids = [
                Command.create(
                    {
                        "name": "Attemdamce",
                        "dayofweek": str(day),
                        "hour_from": "07",
                        "hour_to": "14",
                    },
                ),
            ]
        cls.employee = cls.env["hr.employee"].create({"name": "Test Employee Leave"})

    @mute_logger("odoo.models.unlink")
    def test_onchange_update_visual_hours(self):
        self.employee.calendar_ids = [Command.clear()]
        self.employee.calendar_ids = [
            Command.create(
                {
                    "date_start": "2025-01-01",
                    "date_end": "2025-12-31",
                    "calendar_id": self.calendar1.id,
                },
            ),
            Command.create(
                {"date_start": "2026-01-01", "calendar_id": self.calendar2.id}
            ),
        ]
        leave_calendar_1 = Form(
            self.env["hr.leave"].with_context(
                default_employee_id=self.employee.id,
                default_request_date_from="2025-01-01",
                default_request_date_to="2025-01-01",
            )
        )
        self.assertEqual(leave_calendar_1.request_hour_from, 8.0)
        self.assertEqual(leave_calendar_1.request_hour_to, 17.0)
        leave_calendar_1.request_date_from = "2026-01-01"
        leave_calendar_1.request_date_to = "2026-01-01"
        self.assertEqual(leave_calendar_1.request_hour_from, 7.0)
        self.assertEqual(leave_calendar_1.request_hour_to, 14.0)
        leave_calendar_2 = Form(
            self.env["hr.leave"].with_context(
                default_employee_id=self.employee.id,
                default_request_date_from="2026-01-01",
                default_request_date_to="2026-01-01",
            )
        )
        self.assertEqual(leave_calendar_2.request_hour_from, 7.0)
        self.assertEqual(leave_calendar_2.request_hour_to, 14.0)
        leave_sunday_calendar_1 = Form(
            self.env["hr.leave"].with_context(
                default_employee_id=self.employee.id,
                default_request_date_from="2025-12-28",
                default_request_date_to="2025-12-28",
            )
        )
        self.assertEqual(leave_sunday_calendar_1.request_hour_from, 7.0)
        self.assertEqual(leave_sunday_calendar_1.request_hour_to, 14.0)
        leave_sunday_calendar_2 = Form(
            self.env["hr.leave"].with_context(
                default_employee_id=self.employee.id,
                default_request_date_from="2026-01-04",
                default_request_date_to="2026-01-04",
            )
        )
        self.assertEqual(leave_sunday_calendar_2.request_hour_from, 7.0)
        self.assertEqual(leave_sunday_calendar_2.request_hour_to, 14.0)
        leave_no_plan = Form(
            self.env["hr.leave"].with_context(
                default_employee_id=self.employee.id,
                default_request_date_from="2024-12-30",
                default_request_date_to="2024-12-30",
            )
        )
        self.assertEqual(leave_no_plan.request_hour_from, 7.0)
        self.assertEqual(leave_no_plan.request_hour_to, 14.0)
