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
            'name': 'New',
            'patient_id': cls.patient.id,
            'doctor_id': cls.doctor.id,
        })

    def test_new_patent_notes_is_set_when_empty(self):
        new_patient = self.env['hospital.patient'].create({
            'name': 'Patient 1234',
            'gender': 'male',
            'age': 50,
        })
        self.assertEqual(new_patient.note, 'New Patient')

    def test_unlink_appointment(self):
        appointment_count = self.env['hospital.appointment'].search_count([('doctor_id', '=', self.doctor.id)])

        appointment = self.env['hospital.appointment'].with_context(tracking_disable=True)
        vals = {
            'name': 'New',
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
        }
        appointment.create(vals.copy())

        appointment_count_before = self.env['hospital.appointment'].search_count([('doctor_id', '=', self.doctor.id)])

        self.assertGreaterEqual(appointment_count, 1)
        self.appointment.unlink()

        appointment_count_after = self.env['hospital.appointment'].search_count([('doctor_id', '=', self.doctor.id)])
        self.assertGreater(appointment_count_before, appointment_count_after)

    def test_create_appointment(self):
        appointment = self.env['hospital.appointment'].with_context(tracking_disable=True)
        vals = {
            'name': 'New',
            'patient_id': self.patient.id,
            'doctor_id': self.doctor.id,
        }
        test_appointment = appointment.create(vals.copy())

        self.doctor._compute_appointment_count()
        self.patient._compute_appointment_count()

        self.assertGreaterEqual(self.patient.appointment_count, 1)
        self.assertGreaterEqual(self.doctor.appointment_count, 1)
        self.assertTrue(test_appointment.name, 'New')

    def test_new_patent_name_exists_on_create(self):
        new_patient = self.env['hospital.patient'].create({
            'name': 'Patient Duplicate',
            'gender': 'male',
            'age': 50,
        })

        with self.assertRaises(ValidationError):
            self.change_patient_name_same_id(new_patient)

    def change_patient_name_same_id(self, new_patient):
        new_patient.create({
            'name': 'Patient Duplicate',
            'gender': 'male',
            'age': 50,
        })

    def change_patient_age(self):
        self.patient.age = 0

    def change_patient_name(self):
        self.patient.name = 'Patient 1'

    def test_patient_exists_by_id(self):
        patients = self.patient.env['hospital.patient'].search(
            [('name', '=', self.patient.name), ('id', '!=', self.patient.id)])
        self.assertTrue(patients is not None)

    def test_doctor_exists_by_id(self):
        doctors = self.doctor.env['hospital.doctor'].search(
            [('doctor_name', '=', self.doctor.doctor_name), ('id', '!=', self.doctor.id)])
        self.assertTrue(doctors is not None)

    def test_appointment_exists_by_id(self):
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

    def test_onchange_null_patient_id_notes_gender_empty(self):
        self.appointment.patient_id = None
        self.appointment.onchange_patient_id()
        self.assertFalse(self.appointment.gender)
        self.assertFalse(self.appointment.note)

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
