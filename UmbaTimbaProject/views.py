from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor

def get_or_set_current_location(request):
    if 'lat' in request.session and 'lng' in request.session:
        latitude = request.session['lat']
        longitude = request.session['lng']
        return longitude, latitude
    elif 'lat' in request.GET and 'lng' in request.GET:
        latitude = request.GET.get('lat')
        longitude = request.GET.get('lng')
        request.session['lat'] = latitude
        request.session['lng'] = longitude
        return longitude,latitude
    else:
        return None,None

def home(request):
    longitude,latitude = get_or_set_current_location(request)
    if latitude and longitude:        
        pnt = GEOSGeometry('POINT(%s %s)' % (longitude, latitude))
        vendors = Vendor.objects.filter (    
            user_profile__location__distance_lte=(pnt, D(km=265))
        ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for vendor in vendors:
            vendor.kms = round(vendor.distance.km, 2)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors':vendors,
    }
    return render(request, 'home.html',context)