from django.db.models import Subquery, OuterRef, Sum
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from registration.models import Product, ProductCategory, ProductSlot, Registration, OrderItem

class ProductStatuses:
    MAX_PURCHASED = 'max_purchased'
    UNAVAILABLE = 'unavailable'
    CONFLICT = 'conflict'
    AVAILABLE = 'available'

def get_status_for_product(product):
    if (product.quantity_purchased >= product.max_quantity_per_reg):
        return 'max_purchased'
    if (product.available_quantity <= 0):
        return 'unavailable'
    if (len(product.slot_conflicts) and product.quantity_claimed + product.quantity_purchased <= 0):
        return 'conflict'
    return 'available'

def build_product(product, user, slot_id):
    slots = list(map(str, product.slots.values_list('pk', flat=True)))
    return {
        'id': product.pk,
        'has_parts': slot_id and product.slots.count() > 1,
        'part': list(product.slots.order_by('rank').values_list('pk', flat=True)).index(slot_id) + 1 if slot_id and product.slots.count() > 1 else None,
        'total_parts': product.slots.count() if slot_id and product.slots.count() > 1 else None,
        'title': product.title,
        'subtitle': product.subtitle,
        'description': product.description,
        'price': '${:,.2f}'.format(product.price * 0.01),
        'max_quantity': min(product.max_quantity_per_reg - product.quantity_purchased, product.available_quantity + product.quantity_claimed),
        'quantity_range': range(0, min(product.max_quantity_per_reg - product.quantity_purchased, product.available_quantity + product.quantity_claimed) + 1),
        'max_quantity_per_reg': product.max_quantity_per_reg,
        'quantity_claimed': product.quantity_claimed,
        'quantity_purchased': product.quantity_purchased,
        'status': get_status_for_product(product),
        'slots': ','.join(slots),
        'slotClasses': ' '.join(map(lambda id: 'slot-' + id, slots)),
        'conflictClasses': ' '.join(map(lambda id: 'conflict-' + str(id), product.slot_conflicts)),
        'is_comped': product.is_compable and Registration.for_user(user).is_comped
    }

def get_context_for_product_selection(section, user, event):
    return {
        'section': [v[1] for v in ProductCategory.SECTION_CHOICES if v[0] == section][0],
        'categories': [{
            'name': category.name,
            'slots': [{
                'name': slot.display_name,
                'is_exclusionary': slot.is_exclusionary,
                'products': [build_product(product, user, slot.pk) for product in Product.objects.get_product_info_for_user(user, event).filter(category=category, slots=slot).iterator()]
            } for slot in ProductSlot.objects.filter(event=event, product__in=category.product_set.all()).distinct().order_by('rank').iterator()]
        } if category.is_slot_based else {
            'name': category.name,
            'products': [build_product(product, user, None) for product in Product.objects.get_product_info_for_user(user, event).filter(category=category).iterator()]
        } for category in ProductCategory.objects.filter(section=section, product__isnull=False, event=event).distinct().order_by('rank').iterator()]
    }

def get_quantity_purchased_for_item(items, user, event):
    purchased_order_items = OrderItem.objects.filter(order__registration__event=event, order__registration__user=user, order__session__isnull=True, product=OuterRef('product__pk')).order_by().values('product').annotate(sum=Sum('quantity')).values('sum')
    return items.annotate(quantity_purchased=Coalesce(Subquery(purchased_order_items), 0))

def add_quantity_range_to_item(item):
    item.quantity_range = range(0, min(item.product.max_quantity_per_reg - item.quantity_purchased, item.product.available_quantity + item.quantity) + 1)
    return item

def add_remove_item_view(request, order, action):
    try:
        product_id = request.POST['product']
        success = action(product_id, int(request.POST['quantity']))
        
        data = {
            'success': success,
            'newTotalInCents': order.original_price,
            'apAvailable': order.can_offer_accessible_price,
        }
    except Exception as e:
        data = {
            'error': 'error: {0}'.format(e)
        }
    return JsonResponse(data)