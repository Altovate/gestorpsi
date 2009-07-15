# -*- coding: utf-8 -*-
"""
Copyright (C) 2008 GestorPsi

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""

import reversion
from django.db import models
from django.contrib.contenttypes import generic
from gestorpsi.phone.models import Phone
from gestorpsi.address.models import City, Address, Country
from gestorpsi.document.models import Document
from gestorpsi.internet.models import Email, Site, InstantMessenger
from gestorpsi.organization.models import Organization
from gestorpsi.util.uuid_field import UuidField
from gestorpsi.util.first_capitalized import first_capitalized
   
Gender = ( ('0','No Information'),('1','Female'), ('2','Male'))

class MaritalStatus(models.Model):
    description = models.CharField(max_length=20)
    def __unicode__(self):
        return u"%s" % self.description
    class Meta:
        ordering = ['description']

class Person(models.Model):
    id = UuidField(primary_key=True)
    name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=20, null=True, blank=True)
    photo = models.CharField(max_length=100)
    birthDate = models.DateField(null=True)
    birthPlace = models.ForeignKey(City, null=True)
    gender = models.CharField(max_length=1, choices=Gender) 
    maritalStatus = models.ForeignKey(MaritalStatus, null=True)
    phones = generic.GenericRelation(Phone, null=True)
    address = generic.GenericRelation(Address, null=True)
    document = generic.GenericRelation(Document, null=True)
    emails  = generic.GenericRelation(Email, null=True)
    sites = generic.GenericRelation(Site, null=True)
    instantMessengers =generic.GenericRelation(InstantMessenger, null=True)
    comments = models.TextField(blank=True, null=True)
    organization = models.ForeignKey(Organization, null=True)

    # the fields below were added in order to deal with foreign ones
    birthForeignCity = models.CharField(max_length=100, null=True)
    birthForeignState = models.CharField(max_length=100, null=True)
    birthForeignCountry = models.IntegerField(max_length=4, null=True)
        
    def __unicode__(self):
        return u"%s" % self.name

    """ function used only in reports.py waiting a fix in Geraldo SubReport"""
    def get_documents(self):
        if self.document.all().count() > 1:
            text = "%s " % self.document.all()[0]
            text += " | %s" % self.document.all()[1]
        elif self.document.all().count() == 1:
            text = "%s" % self.document.all()[0]
        else:
            text = ""
        return text

    """ function used only in reports.py waiting a fix in Geraldo SubReport"""
    def get_phones(self):
        if self.phones.all().count() > 1:
            text = "%s " % self.phones.all()[0]
            text += " | %s" % self.phones.all()[1]
        elif self.phones.all().count() == 1:
            text = "%s" % self.phones.all()[0]
        else:
            text = ""
        return text

    """ function used only in reports.py waiting a fix in Geraldo SubReport"""
    def get_internet(self):
        text = ""
        if self.emails.all().count():
            text = "e-mail: %s" % self.emails.all()[0]
        if self.sites.all().count():
            if len(text):
                text += " | Web Page: %s" % self.sites.all()[0]
            else:
                text += "Web Page: %s" % self.sites.all()[0]
        if self.instantMessengers.all().count():
            if len(text):
                text += " | IM: %s" % self.instantMessengers.all()[0]
            else:
                text += "IM: %s" % self.instantMessengers.all()[0]
        return text

    """ function used only in reports.py waiting a fix in Geraldo SubReport"""
    def get_address(self):
        text = ""
        if self.address.all().count():
            addr = self.address.all()[0]
            text = "%s %s, %s" % (addr.addressPrefix, addr.addressLine1, addr.addressNumber)
            if len(addr.addressLine2): text += " - %s" % addr.addressLine2
            if len(addr.neighborhood): text += " - %s" % addr.neighborhood
            text += "<br />%s - %s - %s" % (first_capitalized(addr.city.name), addr.city.state.shortName, addr.city.state.country.name)
            if len(addr.zipCode): text += " - CEP: %s" % addr.zipCode
        return text

    def get_photo(self):
        from gestorpsi.settings import MEDIA_ROOT #, PROJECT_ROOT_PATH
        if len(self.photo):
            return "%simg/organization/%s/.thumb-whitebg/%s" % (MEDIA_ROOT, self.organization.id, self.photo)
        else:
            return "%simg/%s" % (MEDIA_ROOT, 'male_generic_photo.png')

    def get_birthdate(self):
        if self.birthDate == None:
            return ""
        else:
            return self.birthDate.strftime('%d/%m/%Y')

    def get_first_phone(self):
        if self.phones.count:
            return self.phones.all()[0]
        else:
            return ""

    def get_birth_place(self):
        if self.birthPlace == None:
            return u"%s - %s" % (self.birthForeignCity, self.birthForeignState)
        else:
            return u"%s - %s" % (first_capitalized(self.birthPlace.name), self.birthPlace.state.shortName)

    def get_birth_country(self):
        if self.birthPlace == None:
            return u"%s" % Country.objects.get(pk=self.birthForeignCountry)
        else:
            return self.birthPlace.state.country

    def get_first_phone(self):
        if ( len( self.phones.all() ) != 0 ):
            return self.phones.all()[0]
        else:
            return ''
    
    def get_first_email(self):
        if ( len( self.emails.all() ) != 0 ):
            return self.emails.all()[0]
        else:
            return ''
        
    def get_first_site(self):
        if ( len( self.sites.all() ) != 0 ):
            return self.sites.all()[0]
        else:
            return ''        

    def revision(self):
        return reversion.models.Version.objects.get_for_object(self).order_by('-revision__date_created').latest('revision__date_created').revision

    class Meta:
        ordering = ['name']

reversion.register(Person, follow=['phones','address', 'emails', 'sites', 'instantMessengers'])
