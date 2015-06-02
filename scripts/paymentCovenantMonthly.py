#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    script to create payment monthly
    create a new payment for each covenant
'''

import sys
import locale
from os import environ

reload(sys)
sys.setdefaultencoding("utf-8")
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

environ['DJANGO_SETTINGS_MODULE'] = 'gestorpsi.settings'
sys.path.append('..')

#sys.path.append("/home/redepsi/lib/python2.7")
#sys.path.append("/home/redepsi/webapps/gestorpsi_app/git.gestorpsi.com.br")
#sys.path.append("/home/redepsi/webapps/gestorpsi_app/git.gestorpsi.com.br/gestorpsi")
#sys.path.append("/home/redepsi/webapps/gestorpsi_app/git.gestorpsi.com.br/gestorpsi/gestorpsi")

from datetime import datetime

from django.db.models.loading import get_models
loaded_models = get_models()

from gestorpsi.financial.models import Payment
from gestorpsi.referral.models import Referral

'''
    Covenant.charge = 12 : Monthly
'''

# main code
for r in Referral.objects.filter(covenant__isnull=False, covenant__charge=12, referraldischarge__isnull=True): 

    '''
        filter for all referall that don't have discharge
    '''
    
    # create a payment for each covenant of referral
    for c in r.covenant.all():

        # new
        payment = Payment()
        payment.created = datetime
        payment.name = c.name
        payment.price = c.price
        payment.off = 0
        payment.total = c.price
        payment.covenant_charge = c.charge

        # clear all
        payment.covenant_payment_way_options = ''
        for pw in c.payment_way.all():
            x = "(%s,'%s')," % ( pw.id , pw.name ) # need be a dict
            payment.covenant_payment_way_options += x

        # add referral
        payment.referral = r

        # save
        payment.save()
