from trytond.model import ModelView, ModelSQL, fields
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
import copy 
from trytond.wizard import Wizard, StateView, Button, StateTransition,StateAction
from trytond.report import Report
from trytond.pyson import Eval, Not, Bool, PYSONEncoder, Equal, Date, DateTime, And
import time
import datetime
from dateutil.relativedelta import relativedelta

__all__ = ['User','PatientEmployer','Appointment','Party','PatientVaccination']
__metaclass__ = PoolMeta


    
class PatientEmployer(ModelSQL, ModelView):
    "PatientEmployer"
    __name__='gnuhealth.patient'
   
    critical_info = fields.Text(
        'Allergies'
        ' information',
        help='Write any important information on the patient\'s disease,'
        ' surgeries, allergies, ...')
    
    employer=fields.Many2One('party.party', 'Employer', required=False,
                                   domain=[('is_employer','=',True)],
                                   
                                  help="person associated to this employer")
   
class User(ModelSQL, ModelView):
    __name__ = 'res.user'
    patient = fields.Many2One('gnuhealth.patient', 'Patient', 
                              required=False,  help='Patient Name')
    person_id=fields.Function(fields.Integer('Person ID'), 'get_patient_person_id')
    
    def get_patient_person_id(self, name):
        cursor = Transaction().cursor
        login_user_id = self.id
        
        cursor.execute('SELECT patient FROM res_user WHERE  \
            id = %s LIMIT 1', (login_user_id,))
        patient_id = cursor.fetchone()
        cursor = Transaction().cursor
        cursor.execute('SELECT name FROM gnuhealth_patient WHERE  \
            id = %s LIMIT 1', (patient_id[0],))
        person_id = cursor.fetchone()
        if (person_id):
        	return int(person_id[0])
    
    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        cls._context_fields.insert(0, 'patient')
        cls._context_fields.insert(0,'person_id')
        
        
class Appointment(ModelSQL, ModelView):
    'Patient Appointments'
    __name__ = 'gnuhealth.appointment'
    
    @classmethod
    def __setup__(cls):
        super(Appointment, cls).__setup__()
        cls._buttons.update({
                'confirmed': {
                    'invisible': And(Not(Equal(Eval('state'), '')),
                        Not(Equal(Eval('state'), 'user_cancelled'))),
                    },
                'cancel': {
                    'invisible': Not(Equal(Eval('state'), 'confirmed')),
                    },
                })

    @classmethod
    @ModelView.button
    def cancel(cls, registrations):
        registration_id = registrations[0]
        cls.write(registrations, {'state': 'user_cancelled'})

    @classmethod
    @ModelView.button
    def confirmed(cls, registrations):
        registration_id = registrations[0]
        cls.write(registrations, {'state': 'confirmed'})

    @classmethod
    def view_toolbar_get(cls):
        """
        Returns the model specific actions.
        A dictionary with keys:
            - print: a list of available reports
            - action: a list of available actions
            - relate: a list of available relations
        """
        Action = Pool().get('ir.action.keyword')
        key = (cls.__name__, repr(Transaction().context))
        result = cls._view_toolbar_get_cache.get(key)
        if result:
            return result
        prints = Action.get_keyword('form_print', (cls.__name__, -1))
        actions = Action.get_keyword('form_action', (cls.__name__, -1))
        relates = Action.get_keyword('form_relate', (cls.__name__, -1))
        result = {
            'print': prints,
            'action': actions,
            'relate': relates,
            }
        cls._view_toolbar_get_cache.set(key, result)
        return result

class Party(ModelSQL, ModelView):
    'Party'
    __name__='party.party'
    is_employer=fields.Boolean(
        'Employer',
        states={'invisible':Bool(Eval('is_persion'))},
        help='Check if the party is a employer')

class PatientVaccination(ModelSQL, ModelView):
    'Patient Vaccination information'
    __name__ = 'gnuhealth.vaccination'

    vaccine = fields.Many2One(
        'product.product', 'Immunization', required=True,
        domain=[('is_vaccine', '=', True)])

    vaccine_expiration_date = fields.Date('Expiration date')

    date = fields.DateTime('Date')
    
    next_dose_date = fields.DateTime('Due Date')
    
    

