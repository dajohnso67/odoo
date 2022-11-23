# -*- coding: utf-8 -*-
from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHospitalAppointment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.patient = cls.env['hospital.patient'].create({
            'name': 'Patient 1',
            'note': 'Test patient note',
            'gender': 'female',
        })

        cls.doctor = cls.env['hospital.doctor'].create({
            'doctor_name': 'Doctor 1',
            'gender': 'male',
            'active': True,
        })

        cls.appointment = cls.env['hospital.appointment'].create({
            'name': 'Appt 1',
            'patient_id': cls.patient.id,
            'doctor_id': cls.doctor.id,
        })

    def test_copy_doctor(self):
        ret = self.doctor.copy()
        self.assertEqual(ret.doctor_name, _("%s (Copy)", self.doctor.doctor_name))
        self.assertNotEqual(self.doctor.id, ret.id)

    def test_appointment_unlink_validation_error(self):
        self.appointment.state = 'done'
        self.assertRaises(ValidationError, self.appointment.unlink)

    def test_onchange_patient_id(self):
        self.appointment.onchange_patient_id()
        self.assertEqual(self.appointment.gender, self.patient.gender)
        self.assertEqual(self.appointment.note, self.patient.note)
        self.assertEqual(self.appointment.gender, 'female')
        self.assertEqual(self.appointment.note, 'Test patient note')

    def test_action_confirm_appointment(self):
        self.appointment.action_confirm()
        self.assertEqual(self.appointment.state, 'confirm')

        self.appointment.action_done()
        self.assertEqual(self.appointment.state, 'done')

        self.appointment.action_draft()
        self.assertEqual(self.appointment.state, 'draft')

        self.appointment.action_cancel()
        self.assertEqual(self.appointment.state, 'cancel')

    def test_action_confirm_patient(self):
        self.patient.action_confirm()
        self.assertEqual(self.patient.state, 'confirm')

        self.patient.action_done()
        self.assertEqual(self.patient.state, 'done')

        self.patient.action_draft()
        self.assertEqual(self.patient.state, 'draft')

        self.patient.action_cancel()
        self.assertEqual(self.patient.state, 'cancel')
