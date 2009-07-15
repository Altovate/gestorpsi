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

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.template import RequestContext
from django.core.paginator import Paginator
from django.utils import simplejson
from gestorpsi.organization.models import Organization
from gestorpsi.place.models import Place, Room, RoomType, PlaceType
from gestorpsi.address.models import Country, AddressType, State
from gestorpsi.address.views import address_save
from gestorpsi.phone.models import PhoneType
from gestorpsi.phone.views import phone_save
from gestorpsi.util.decorators import permission_required_with_403

@permission_required_with_403('place.place_list')
def room_index(request):
    user = request.user
    return render_to_response( "place/place_room_index.html",{
                                                            'RoomTypes': RoomType.objects.all(),
                                                            'Places': Place.objects.filter(organization=user.get_profile().org_active.id),
                                                            },
                                                          context_instance=RequestContext(request))

@permission_required_with_403('place.place_list')
def index(request):
    user = request.user
    return render_to_response( "place/place_index.html", {
                                                          'PlaceTypes': PlaceType.objects.all(),
                                                          'countries': Country.objects.all(),
                                                          'RoomTypes': RoomType.objects.all(),
                                                          'PhoneTypes': PhoneType.objects.all(),
                                                          'AddressTypes': AddressType.objects.all(),
                                                          'States': State.objects.all(),
                                                          'Places': Place.objects.filter(organization=user.get_profile().org_active.id),
                                                          },
                                                          context_instance=RequestContext(request))

@permission_required_with_403('place.place_list')
def list(request, page = 1):
    user = request.user
    object = Place.objects.filter(organization=user.get_profile().org_active.id)
    
    object_length = len(object)
    paginator = Paginator(object, settings.PAGE_RESULTS)
    object = paginator.page(page)

    array = {} #json
    i = 0

    array['util'] = {
        'has_perm_read': user.has_perm('place.place_read'),
        'paginator_has_previous': object.has_previous().real,
        'paginator_has_next': object.has_next().real,
        'paginator_previous_page_number': object.previous_page_number().real,
        'paginator_next_page_number': object.next_page_number().real,
        'paginator_actual_page': object.number,
        'paginator_num_pages': paginator.num_pages,
        'object_length': object_length,
    }

    
    array['paginator'] = {}
    for p in paginator.page_range:
        array['paginator'][p] = p
    
    for o in object.object_list:
        array[i] = {
            'id': o.id,
            'name': o.label,
            'phone': u'%s' % o.get_first_phone(),
        }
        i = i + 1

    return HttpResponse(simplejson.dumps(array), mimetype='application/json')

@permission_required_with_403('place.place_read')
def form(request, object_id=''):
    try:
        user = request.user
        phones = []
        addresses = []
        #rooms = []
        object= get_object_or_404(Place, pk=object_id)
        addresses= object.address.all()
        phones= object.phones.all()
        #rooms= object.room_set.all()
        organization= Organization.objects.get(pk= user.get_profile().org_active.id)

    except (Http404, ObjectDoesNotExist):
        object= Place()
        place_type= PlaceType()
    return render_to_response('place/place_form.html', {'object': object,
                                                        'PlaceTypes': PlaceType.objects.all(), 
                                                        'organization': organization,
                                                        'addresses': addresses,
                                                        'phones': phones,
                                                        'PhoneTypes': PhoneType.objects.all(),
                                                        'AddressTypes': AddressType.objects.all(),
                                                        'countries': Country.objects.all(),
                                                        'RoomTypes': RoomType.objects.all(),
                                                        #'rooms': rooms,
                                                        'States': State.objects.all(),
                                                        },
                                                        context_instance=RequestContext(request))

@permission_required_with_403('place.place_write')
def save(request, object_id=''):
    user = request.user
    try:
        object = get_object_or_404(Place, pk=object_id)
    except Http404:
        object = Place()

    try:
        object.visible= get_visible( request, request.POST['visible'] )
    except:
        object.visible = False
    object.label = request.POST['label']
    object.comments = request.POST.get('comments')
    object.place_type= PlaceType.objects.get( pk= request.POST[ 'place_type' ] )
    object.organization = user.get_profile().org_active    
    object.save() 

    #save_rooms( request, object, request.POST.getlist( 'room_id' ), request.POST.getlist('description'), request.POST.getlist('dimension'), request.POST.getlist('room_type'), request.POST.getlist('furniture') )
    phone_save(object, request.POST.getlist('phoneId'), request.POST.getlist('area'), request.POST.getlist('phoneNumber'), request.POST.getlist('ext'), request.POST.getlist('phoneType'))
    address_save(object, request.POST.getlist('addressId'), request.POST.getlist('addressPrefix'),
                 request.POST.getlist('addressLine1'), request.POST.getlist('addressLine2'),
                 request.POST.getlist('addressNumber'), request.POST.getlist('neighborhood'),
                 request.POST.getlist('zipCode'), request.POST.getlist('addressType'),
                 request.POST.getlist('city'), request.POST.getlist('foreignCountry'),
                 request.POST.getlist('foreignState'), request.POST.getlist('foreignCity'))

    return HttpResponse(object.id)

def room_save(request, object_id=''):
    user = request.user

    try:
        object = Room.objects.get(pk=object_id)
    except:
        object = Room()
        print request.POST.get('place_id')
        object.place = Place.objects.get(pk = request.POST.get('place_id'))

    object.description = request.POST.get( 'description' )
    object.dimension = request.POST.get('dimension')
    object.room_type = RoomType.objects.get(pk=request.POST.get('room_type'))
    object.furniture = request.POST.get('furniture')
    object.comments = request.POST.get('comments') 
    object.active = get_visible(request.POST.get('active'))

    if object.id:
        object.save(force_update=True)
    else:
        object.save()
    
    return HttpResponse(object.id)

def room_list(request, page = 1):
    user = request.user
    object = Room.objects.filter(place__organization = user.get_profile().org_active)
    
    object_length = len(object)
    paginator = Paginator(object, settings.PAGE_RESULTS)
    object = paginator.page(page)

    array = {} #json
    i = 0

    array['util'] = {
        'has_perm_read': user.has_perm('place.place_read'),
        'paginator_has_previous': object.has_previous().real,
        'paginator_has_next': object.has_next().real,
        'paginator_previous_page_number': object.previous_page_number().real,
        'paginator_next_page_number': object.next_page_number().real,
        'paginator_actual_page': object.number,
        'paginator_num_pages': paginator.num_pages,
        'object_length': object_length,
    }

    
    array['paginator'] = {}
    for p in paginator.page_range:
        array['paginator'][p] = p
    
    for o in object.object_list:
        array[i] = {
            'id': o.id,
            'name': o.description,
            'place': o.place.label,
        }
        i = i + 1

    return HttpResponse(simplejson.dumps(array), mimetype='application/json')

def room_form(request, object_id = ' '):
    user = request.user
    object = Room.objects.get(pk = object_id)

    return render_to_response('place/place_room_form.html', {
                                                        'object': object,
                                                        'RoomTypes': RoomType.objects.all(),
                                                        'Places': Place.objects.filter(organization=user.get_profile().org_active.id),
                                                        },
                                                        context_instance=RequestContext(request))


@permission_required_with_403('place.place_read')
def is_equal(request, a_room):
    try:
        room_loaded_from_db = Room.objects.get( pk= a_room.id )
    except:
        return -1
    
    if cmp(room_loaded_from_db, a_room) == 0:
        return 0
    else:
        return 1

def get_visible(value):
    if value == 'on':
        return True
    else:
        return False 
