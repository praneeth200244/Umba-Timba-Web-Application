from vendor.models import Vendor


def get_vendor_object(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor