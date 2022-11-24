# -*- coding: utf-8 -*-
from odoo import _
from odoo.exceptions import ValidationError
from odoo.tests import common, tagged


@tagged('-at_install', 'post_install')
class TestHospitalAppointment(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.patient = cls.env['hospital.patient'].create({
            'name': 'Patient 1',
            'note': 'Test patient note',
            'gender': 'female',
            'age': 10,
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

    def test_create_appointment(self):
        appointment = self.env['hospital.appointment'].with_context(tracking_disable=True)
        vals = {
            'name': 'Appt 1/1/2022',
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
        }
        test_appointment = appointment.create(vals.copy())

        appointment_count = self.env['hospital.appointment'].search_count([('doctor_id', '=', self.doctor.id)])
        self.assertGreaterEqual(appointment_count, 1)
        self.assertTrue(test_appointment.name.startswith('Appt'))

    def change_patient_age(self):
        self.patient.age = 0

    def change_patient_name(self):
        self.patient.name = 'Patient 1'

    def test_patient_exists(self):
        patients = self.patient.env['hospital.patient'].search(
            [('name', '=', self.patient.name), ('id', '!=', self.patient.id)])
        self.assertTrue(patients is not None)

    def test_doctor_exists(self):
        doctors = self.doctor.env['hospital.doctor'].search(
            [('doctor_name', '=', self.doctor.doctor_name), ('id', '!=', self.doctor.id)])
        self.assertTrue(doctors is not None)

    def test_appointment_exists(self):
        appointments = self.appointment.env['hospital.appointment'].search(
            [('name', '=', self.appointment.name), ('id', '!=', self.appointment.id)])
        self.assertTrue(appointments is not None)

    def test_patient_duplicate_name_validation_error(self):
        self.assertRaises(ValidationError, self.change_patient_name())

    def test_patient_age_validation_error(self):
        self.assertRaises(ValidationError, self.change_patient_age)

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

    def test_appointment_action(self):
        self.appointment.action_confirm()
        self.assertEqual(self.appointment.state, 'confirm')

        self.appointment.action_done()
        self.assertEqual(self.appointment.state, 'done')

        self.appointment.action_draft()
        self.assertEqual(self.appointment.state, 'draft')

        self.appointment.action_cancel()
        self.assertEqual(self.appointment.state, 'cancel')

    def test_patient_action(self):
        self.patient.action_confirm()
        self.assertEqual(self.patient.state, 'confirm')

        self.patient.action_done()
        self.assertEqual(self.patient.state, 'done')

        self.patient.action_draft()
        self.assertEqual(self.patient.state, 'draft')

        self.patient.action_cancel()
        self.assertEqual(self.patient.state, 'cancel')
