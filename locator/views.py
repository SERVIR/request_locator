from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.gis.geoip2 import GeoIP2
from django.views.decorators.csrf import csrf_exempt
from geoip2.errors import AddressNotFoundError

# Create your views here.

g = GeoIP2()


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def get_country_code(request):
    ip_address = request.GET.get('ip_address')
    if ip_address:
        country_code = g.country_code(ip_address)
    else:
        country_code = g.country_code(get_client_ip(request))
    try:
        return JsonResponse({"country_code": country_code})
    except AddressNotFoundError:
        return JsonResponse({"country_code": "ZZ"})
    
    
@csrf_exempt
def get_country(request):
    ip_address = request.GET.get('ip_address')
    if ip_address:
        country = g.country(ip_address)
    else:
        country = g.country(get_client_ip(request))
    try:
        return JsonResponse({"country": country})
    except AddressNotFoundError:
        return JsonResponse({"country": "Not Found"})
