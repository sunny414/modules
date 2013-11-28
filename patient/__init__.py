from trytond.pool import Pool
from .patient import *


def register():
    Pool.register(
        User,
		PatientEmployer,
        Appointment,
        Party,
        PatientVaccination,
        module='patient', type_='model')

