from django.http import JsonResponse
from django.shortcuts import render
from django.contrib.gis.geoip2 import GeoIP2
from django.views.decorators.csrf import csrf_exempt
from geoip2.errors import AddressNotFoundError

# Initialize GeoIP2 instance
g = GeoIP2()


# Function to get client IP address
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Endpoint to get country code
@csrf_exempt
def get_country_code(request):
    ip_address = request.GET.get('ip_address')
    try:
        if ip_address:
            country_code = g.country_code(ip_address)
        else:
            country_code = g.country_code(get_client_ip(request))

        return JsonResponse({"country_code": country_code})
    except AddressNotFoundError:
        # If address is not found, return ZZ as the country code
        return JsonResponse({"country_code": "ZZ"})


# Endpoint to get country
@csrf_exempt
def get_country(request):
    ip_address = request.GET.get('ip_address')
    try:
        if ip_address:
            country = g.country(ip_address)
        else:
            country = g.country(get_client_ip(request))

        return JsonResponse({"country": country})
    except AddressNotFoundError:
        # If address is not found, return None for country code and country name
        return JsonResponse({"country": {"country_code": None, "country_name": None}})


# Endpoint to get city
@csrf_exempt
def get_city(request):
    ip_address = request.GET.get('ip_address')
    try:
        if ip_address:
            city = g.city(ip_address)
        else:
            city = g.city(get_client_ip(request))
        return JsonResponse({"city": city})
    except AddressNotFoundError:
        # If address is not found, return None for all city details
        return JsonResponse({"city": {"city": None, "continent_code": None, "continent_name": None,
                                      "country_code": None, "country_name": None, "dma_code": None,
                                      "is_in_european_union": None, "latitude": None, "longitude": None,
                                      "postal_code": None, "region": None, "time_zone": None}})
