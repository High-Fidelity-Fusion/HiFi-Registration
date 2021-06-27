from .order_item import OrderItem
from .product_slot import ProductSlot
from django.db import models
from django.db.models import Sum, F, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.contrib.postgres.aggregates import ArrayAgg


class ProductManager(models.Manager):
    def get_product_info_for_user(self, user, event):
        pending_order_items = OrderItem.objects.filter(order__registration__user=user, order__session__isnull=False, product=OuterRef('pk'))
        purchased_order_items = OrderItem.objects.filter(order__registration__user=user, order__session__isnull=True, product=OuterRef('pk')).order_by().values('product').annotate(sum=Sum('quantity')).values('sum')
        all_other_products_for_user = OrderItem.objects.filter(order__registration__user=user).exclude(product=(OuterRef(OuterRef('pk')))).values('product')
        conflicts_with_order_agg = ProductSlot.objects.filter(is_exclusionary=True, product=OuterRef('pk')).filter(product__in=Subquery(all_other_products_for_user)).order_by().values('is_exclusionary').annotate(pks=ArrayAgg('pk')).values('pks')
        return self.filter(is_visible=True, event=event). \
            annotate(quantity_purchased=Coalesce(Subquery(purchased_order_items), 0)). \
            annotate(quantity_claimed=Coalesce(Subquery(pending_order_items.values('quantity')[:1]), 0)). \
            annotate(slot_conflicts=Coalesce(Subquery(conflicts_with_order_agg), []))
