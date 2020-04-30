from registration.models import Product, ProductCategory, ProductSlot

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
    if (product.exclusionary_slot_exists_in_order and product.quantity_claimed + product.quantity_purchased <= 0):
        return 'conflict'
    return 'available'

def build_product(product, slot_id):
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
        'max_quantity': product.max_quantity_per_reg - product.quantity_purchased,
        'quantity_claimed': product.quantity_claimed,
        'status': get_status_for_product(product),
        'slots': ','.join(slots),
        'slotClasses': ' '.join(map(lambda id: 'slot-' + id, slots)),
        'conflictClasses': ' '.join(map(lambda id: 'conflict-' + str(id), product.slot_conflicts))
    }

def get_context_for_product_selection(section, user):
    return {
        'section': [v[1] for v in ProductCategory.SECTION_CHOICES if v[0] == section][0],
        'categories': [{
            'name': category.name,
            'slots': [{
                'name': slot.name,
                'is_exclusionary': slot.is_exclusionary,
                'products': [build_product(product, slot.pk) for product in Product.objects.get_product_info_for_user(user).filter(category=category, slots=slot).iterator()]
            } for slot in ProductSlot.objects.filter(product__in=category.product_set.all()).distinct().order_by('rank').iterator()]
        } if category.is_slot_based else {
            'name': category.name,
            'products': [build_product(product, None) for product in Product.objects.get_product_info_for_user(user).filter(category=category).iterator()]
        } for category in ProductCategory.objects.filter(section=section, product__isnull=False).distinct().order_by('rank').iterator()]
    }



