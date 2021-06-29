from django.test import TestCase
from registration.models import *
from registration.models.helpers import with_is_paid
from django.core.exceptions import SuspiciousOperation
from django.contrib.sessions.models import Session
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.db.models import Max, Min
import random
import string

def random_string():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))

def coin_flip():
    return random.choice([False, True])

def clean_db():
    Order.objects.all().delete()
    Registration.objects.all().delete()
    Product.slots.through.objects.all().delete()
    Product.objects.all().delete()
    ProductCategory.objects.all().delete()
    ProductSlot.objects.all().delete()
    APFund.objects.all().delete()
    Session.objects.all().delete()
    CompCode.objects.all().delete()
    Payment.objects.all().delete()
    Event.objects.all().delete()

def setup_test_data():
    event1 = Event.objects.create(name='Event #1', slug='event1')
    category_1 = ProductCategory.objects.create(name='Friday Classes', section='DANCE', rank=3, event=event1)
    slot_1 = ProductSlot.objects.create(name='11amFriday', rank=3, display_name='timeDay', event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description', category=category_1, event=event1)
    product.slots.set([slot_1])
    user1 = User.objects.create_user(email='asdf@asdf.asdf')
    registration1 = Registration.objects.create(user=user1, event=event1)
    session1 = Session.objects.create(pk='a', expire_date=timezone.now())
    Order.objects.create(registration=registration1, session=session1)
    registration2 = Registration.objects.create(event=event1)
    session2 = Session.objects.create(pk='b', expire_date=timezone.now())
    Order.objects.create(registration=registration2, session=session2)
    APFund.objects.create(contribution=2001, notes='notes', event=event1)
    CompCode.objects.create(type=CompCode.STAFF, max_uses=1, event=event1)

def setup_products_no_delete():
    event1 = Event.objects.create(name='Event #1', slug='event1', policies='## Code of Conduct\nBe **excellent** to each other n that good stuff.\n## Yay')
    slot1 = ProductSlot.objects.create(name='Friday1pm', rank=3, display_name='1pm', event=event1)
    slot2 = ProductSlot.objects.create(name='Friday11am', rank=2, display_name='11am', event=event1)

    category = ProductCategory.objects.create(name='Teacher Training', section='CLASS', is_slot_based=False, rank=2, event=event1)
    expensive_product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=200000, title='Expensive Training', subtitle='subtitle', description='description', category=category, event=event1)
    multi_slot_product1 = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Full Weekend Teacher Training', subtitle='subtitle', description='description', category=category, event=event1)
    multi_slot_product1.slots.add(slot1)
    multi_slot_product1.slots.add(slot2)

    category = ProductCategory.objects.create(name='Friday', section='CLASS', rank=3, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Dance like a Baby Giraffe', subtitle='featuring a real baby giraffe!', description='description', category=category, event=event1)
    product.slots.add(slot1)
    product = Product.objects.create(total_quantity=0, max_quantity_per_reg = 1, price=2000, title='Dance like you are Out of Stock', subtitle='subtitle', description='description', category=category, event=event1)
    product.slots.add(slot1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Ants in your Pants', subtitle='teacher: Ant Man', description='We are going to put literal ants in your literal pants.', category=category, event=event1)
    product.slots.add(slot2)
    multi_slot_product2 = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Long Class', subtitle='subtitle', description='description', category=category, event=event1)
    multi_slot_product2.slots.add(slot1)
    multi_slot_product2.slots.add(slot2)

    category = ProductCategory.objects.create(name='Clothing', section='MERCH', is_slot_based=False, rank=2, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 3, price=1500, title='t-shirt', subtitle='subtitle', description='description', category=category, is_ap_eligible=False, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 10, price=1500, title='hoodie', subtitle='subtitle', description='description', category=category, is_ap_eligible=False, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 2, price=1500, title='AP hoodie', subtitle='subtitle', description='description', category=category, is_ap_eligible=True, event=event1)

    category = ProductCategory.objects.create(name='Dance Passes', section='DANCE', is_slot_based=False, rank=3, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Friday', subtitle='theme: rebecca black', description='description', category=category, is_compable=True, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Saturday', subtitle='theme: Satyrday', description='description', category=category, is_compable=True, event=event1)
    APFund.objects.create(contribution=100000, notes='notes', event=event1)

    event2 = Event.objects.create(name='Event #2', slug='event2')
    category = ProductCategory.objects.create(name='Dance Tickets', section='DANCE', is_slot_based=False, rank=2, event=event2)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Friday', subtitle='theme: space face', description='description', category=category, is_compable=True, event=event2)


# This is used for manual testing data
def setup_products():
    Order.objects.all().delete()
    Product.slots.through.objects.all().delete()
    Product.objects.all().delete()
    ProductCategory.objects.all().delete()
    ProductSlot.objects.all().delete()
    APFund.objects.all().delete()
    Registration.objects.all().delete()
    Event.objects.all().delete()

    setup_products_no_delete()

def get_random(cls):
    max_id = cls.objects.all().aggregate(max_id=Max("pk"))['max_id']
    min_id = cls.objects.all().aggregate(min_id=Min("pk"))['min_id']
    pk = random.randint(min_id, max_id)
    return cls.objects.get(pk=pk)


# Case 1:
# NUM_PRODUCTS = 50
# NUM_REGISTRATIONS = 500
# ORDER_ITEMS_PER_ORDER = 20
# Results:
# Classes page load latency = 5 seconds
# Add item latency = 0.75 seconds
# Claim AP = 0.5 seconds
def setup_performance_test(NUM_PRODUCTS, NUM_REGISTRATIONS, ORDER_ITEMS_PER_ORDER):
    # 2 orders are created per registration, ~50% of orders are AP, ~25% of orders are unsubmitted

    Order.objects.all().delete()
    Registration.objects.all().delete()
    Product.slots.through.objects.all().delete()
    Product.objects.all().delete()
    ProductCategory.objects.all().delete()
    ProductSlot.objects.all().delete()
    APFund.objects.all().delete()
    Session.objects.all().delete()
    CompCode.objects.all().delete()
    Payment.objects.all().delete()
    Event.objects.all().delete()

    # create products
    event1 = Event.objects.create(name='Event #1', slug='event1')
    category = ProductCategory.objects.create(name='Passes', section='CLASS', rank=3, event=event1)
    slot1 = ProductSlot.objects.create(name='slot1', rank=3, display_name='1pm', event=event1)
    slot2 = ProductSlot.objects.create(name='slot2', rank=2, display_name='1pm', event=event1)
    slot3 = ProductSlot.objects.create(name='slot3', rank=2, display_name='1pm', event=event1)

    for i in range(NUM_PRODUCTS):
        p = Product.objects.create(total_quantity=5000, max_quantity_per_reg = 1, price=2000, title='title', subtitle='subtitle', description='description', category=category, event=event1)

        if i % 3 == 0:
            p.slots.add(slot1)
        elif i % 3 == 1:
            p.slots.add(slot3)
        else:
            p.slots.add(slot2)
    first_p = Product.objects.first().pk
    last_p = Product.objects.first().pk

    # create users/registrations
    APFund.objects.create(contribution=300000000, notes='notes', event=event1)
    for i in range(NUM_REGISTRATIONS):
        user = User.objects.create_user(email=random_string() + '@asdf.asdf')
        registration = Registration.objects.create(user=user, event=event1)
        session = Session.objects.create(pk=random_string(), expire_date=timezone.now() + relativedelta(weeks=+2))

        order = Order.objects.create(registration=registration, session=session)
        for i in range(1, ORDER_ITEMS_PER_ORDER + 1):
            try:
                order.add_item(random.randrange(first_p, last_p-1), 1)
            except:
                continue
        if coin_flip():
            order.claim_accessible_pricing()
        else:
            order.donation = 1000
        order.session = None
        order.save()

        order = Order.objects.create(registration=registration, session=session)
        for i in range(1, ORDER_ITEMS_PER_ORDER + 1):
            try:
                order.add_item(random.randrange(first_p, last_p-1), 1)
            except:
                continue
        if coin_flip():
            order.claim_accessible_pricing()
        else:
            order.donation = 1000
        if coin_flip():
            order.session = None
        order.save()




class OrderTestCase(TestCase):
    def setUp(self):
        setup_test_data()

    def test_add_item__simple_case(self):
        order = Order.objects.first()
        product = Product.objects.first()
        registration = Registration.objects.first()

        result = order.add_item(product.pk, 1)

        self.assertEqual(result, True)
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.unit_price, 2000)
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.total_price, 2000)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 2000)
        self.assertEqual(order.accessible_price, 2000)
        self.assertEqual(order.is_accessible_pricing, False)
        self.assertEqual(order.is_submitted, False)
        self.assertEqual(registration.is_accessible_pricing, False)
        self.assertEqual(registration.is_submitted, False)

    def test_delete_order(self):
        order = Order.objects.first()
        product = Product.objects.first()
        registration = Registration.objects.first()

        self.assertEqual(product.available_quantity, 5)

        result = order.add_item(product.pk, 1)
        order.refresh_from_db()
        product.refresh_from_db()

        self.assertEqual(product.available_quantity, 4)

        order.delete()
        product.refresh_from_db()

        self.assertEqual(product.available_quantity, 5)


    def test_add_item__two_quantity(self):
        order = Order.objects.first()
        product = Product.objects.first()

        result = order.add_item(product.pk, 2)

        self.assertEqual(result, True)
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.unit_price, 2000)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.total_price, 4000)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 4000)
        self.assertEqual(order.accessible_price, 4000)
        self.assertEqual(order.is_accessible_pricing, False)

    def test_add_item__called_twice(self):
        order = Order.objects.first()
        product = Product.objects.first()

        order.add_item(product.pk, 1)
        result = order.add_item(product.pk, 1)

        self.assertEqual(result, True)
        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.unit_price, 2000)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.total_price, 4000)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 4000)
        self.assertEqual(order.accessible_price, 4000)
        self.assertEqual(order.is_accessible_pricing, False)

    def test_add_item__too_much_quantity(self):
        order = Order.objects.first()
        product = Product.objects.first()

        with self.assertRaises(SuspiciousOperation):
            order.add_item(product.pk, 3)
        order.add_item(product.pk, 2)
        with self.assertRaises(SuspiciousOperation):
            order.add_item(product.pk, 1)

    def test_add_item__out_of_stock(self):
        order = Order.objects.first()
        product = Product.objects.first()
        product.max_quantity_per_reg = 100
        product.save()

        result = order.add_item(product.pk, 6)
        self.assertEqual(result, False)
        result = order.add_item(product.pk, 5)
        self.assertEqual(result, True)
        result = order.add_item(product.pk, 1)
        self.assertEqual(result, False)

    def test_add_item__slot_conflict(self):
        slot = ProductSlot.objects.first()
        order = Order.objects.first()
        product = Product.objects.first()
        conflicting_product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        conflicting_product.slots.set([slot])

        order.add_item(product.pk, 1)
        with self.assertRaises(SuspiciousOperation):
            order.add_item(conflicting_product.pk, 1)

        slot.is_exclusionary = False
        slot.save()
        order.add_item(conflicting_product.pk, 1)

    def test_add_item__is_submitted(self):
        order = Order.objects.first()
        product = Product.objects.first()
        order.session = None
        order.save()

        self.assertEqual(order.is_submitted, True)
        self.assertEqual(Registration.objects.first().is_submitted, True)
        with self.assertRaises(SuspiciousOperation):
            order.add_item(product.pk, 1)

    def test_add_item__comped(self):
        comp_code = CompCode.objects.first()
        registration = Registration.objects.create(event=Event.objects.first())
        registration.comp_code = comp_code
        registration.save()
        order = Order.objects.create(registration=registration, session=Session.objects.create(pk='test_add_item__comped', expire_date=timezone.now()))
        non_compable_product = Product.objects.first()
        compable_product = Product.objects.create(is_compable=True, total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())

        order.add_item(non_compable_product.pk, 1)
        order.add_item(compable_product.pk, 1)

        self.assertEqual(order.original_price, 2000)
        self.assertEqual(order.accessible_price, 2000)
        self.assertEqual(order.is_accessible_pricing, False)

    def test_remove_item__full_quantity(self):
        order = Order.objects.first()
        product = Product.objects.first()
        order.add_item(product.pk, 1)

        order.remove_item(product.pk, 1)

        self.assertEqual(OrderItem.objects.count(), 0)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 0)
        self.assertEqual(order.accessible_price, 0)

    def test_remove_item__partial_quantity(self):
        order = Order.objects.first()
        product = Product.objects.first()
        order.add_item(product.pk, 2)

        order.remove_item(product.pk, 1)

        self.assertEqual(OrderItem.objects.count(), 1)
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.unit_price, 2000)
        self.assertEqual(order_item.quantity, 1)
        self.assertEqual(order_item.total_price, 2000)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 2000)
        self.assertEqual(order.accessible_price, 2000)

    def test_claim_accessible_pricing(self):
        order = Order.objects.first()
        product = Product.objects.first()
        order.add_item(product.pk, 1)

        result = order.claim_accessible_pricing()
        order.session = None
        order.save()

        self.assertEqual(result, True)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 2000)
        self.assertEqual(order.accessible_price, 0)
        self.assertEqual(order.is_accessible_pricing, True)
        self.assertEqual(Registration.objects.first().is_accessible_pricing, True)

    def test_claim_accessible_pricing__fund_insufficient(self):
        product = Product.objects.first()
        order = Order.objects.first()
        order.add_item(product.pk, 1)
        order.claim_accessible_pricing()
        order2 = Order.objects.last()
        order2.add_item(product.pk, 1)

        result = order2.claim_accessible_pricing()

        self.assertEqual(result, False)
        order2.refresh_from_db()
        self.assertEqual(order2.is_accessible_pricing, False)

    def test_claim_accessible_pricing__partially_ineligible(self):
        order = Order.objects.first()
        product = Product.objects.first()
        ineligible_product = Product.objects.create(is_ap_eligible=False, total_quantity=5, max_quantity_per_reg = 2, price=1000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        order.add_item(product.pk, 1)
        order.add_item(ineligible_product.pk, 1)

        result = order.claim_accessible_pricing()

        self.assertEqual(result, True)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 3000)
        self.assertEqual(order.accessible_price, 1000)
        self.assertEqual(order.is_accessible_pricing, True)

    def test_claim_accessible_pricing__fully_ineligible(self):
        order = Order.objects.first()
        ineligible_product = Product.objects.create(is_ap_eligible=False, total_quantity=5, max_quantity_per_reg = 2, price=1000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        order.add_item(ineligible_product.pk, 1)

        result = order.claim_accessible_pricing()

        self.assertEqual(result, True)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 1000)
        self.assertEqual(order.accessible_price, 1000)
        self.assertEqual(order.is_accessible_pricing, False)

class ProductTestCase(TestCase):
    def setUp(self):
        setup_test_data()

    def test_get_product_info_for_user(self):
        #Arrange
        event3 = Event.objects.create(name='Event 3', slug='event3')
        event3_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title3', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=event3)
        product = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        complete_order = Order.objects.create(registration=registration, session=Session.objects.create(pk='product_test', expire_date=timezone.now()))

        incomplete_order.add_item(product.pk, 1)
        complete_order.add_item(product.pk, 1)
        complete_order.session = None
        complete_order.save()

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user, Event.objects.first())
        product_result = product_info.get(pk=product.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)

        #Assert
        self.assertEqual(product_info.filter(pk=product.pk).count(), 1)
        self.assertEqual(product_info.filter(pk=event3_product.pk).count(), 0)
        self.assertEqual(product_result.quantity_purchased, 1)
        self.assertEqual(unclaimed_product_result.quantity_purchased, 0)
        self.assertEqual(product_result.quantity_claimed, 1)
        self.assertEqual(unclaimed_product_result.quantity_claimed, 0)
        self.assertEqual(product_result.available_quantity, 3)
        self.assertEqual(unclaimed_product_result.available_quantity, 5)

    def test_get_product_info_for_user__empty_cart(self):
        #Arrange
        product = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        registration = Registration.objects.first()

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user, Event.objects.first())
        product_result = product_info.get(pk=product.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)

        #Assert
        self.assertEqual(product_info.filter(pk=product.pk).count(), 1)
        self.assertEqual(product_result.quantity_purchased, 0)
        self.assertEqual(unclaimed_product_result.quantity_purchased, 0)
        self.assertEqual(product_result.quantity_claimed, 0)
        self.assertEqual(unclaimed_product_result.quantity_claimed, 0)
        self.assertEqual(product_result.available_quantity, 5)
        self.assertEqual(unclaimed_product_result.available_quantity, 5)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(unclaimed_product_result.slot_conflicts, [])

    def test_get_product_info_for_user__multi_slot_products_with_conflict(self):
        #Arrange
        slot1 = ProductSlot.objects.create(name='1pm', rank=3, event=Event.objects.first())
        slot2 = ProductSlot.objects.create(name='11am', rank=2, event=Event.objects.first())
        category = ProductCategory.objects.create(name='Teacher Training', section='CLASS', is_slot_based=False, rank=2, event=Event.objects.first())
        product1 = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Full Weekend Teacher Training', subtitle='subtitle', description='description', category=category, event=Event.objects.first())
        product1.slots.add(slot1)
        product1.slots.add(slot2)
        product2 = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Long Class', subtitle='subtitle', description='description', category=category, event=Event.objects.first())
        product2.slots.add(slot1)
        product2.slots.add(slot2)

        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        incomplete_order.add_item(product1.pk, 1)

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user, Event.objects.first())
        product_result = product_info.get(pk=product1.pk)
        product_result2 = product_info.get(pk=product2.pk)

        #Assert
        self.assertEqual(product_info.filter(pk=product1.pk).count(), 1)
        self.assertEqual(product_result.quantity_purchased, 0)
        self.assertEqual(product_result.quantity_claimed, 1)
        self.assertEqual(product_result.available_quantity, 4)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(product_result2.quantity_purchased, 0)
        self.assertEqual(product_result2.quantity_claimed, 0)
        self.assertEqual(product_result2.available_quantity, 5)
        self.assertEqual(product_result2.slot_conflicts, [slot1.pk, slot2.pk])

    def test_get_product_info_for_user__product_does_not_conflict(self):
        #Arrange
        product_slot = ProductSlot.objects.first()
        product = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        complete_order = Order.objects.create(registration=registration, session=Session.objects.create(pk='product_test', expire_date=timezone.now()))

        incomplete_order.add_item(product.pk, 1)
        complete_order.add_item(product.pk, 1)
        complete_order.session = None
        complete_order.save()

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user, Event.objects.first())

        #Assert
        product_result = product_info.get(pk=product.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(unclaimed_product_result.slot_conflicts, [])

    def test_get_product_info_for_user__product_conflicts_with_cart(self):
        #Arrange
        product_slot = ProductSlot.objects.first()
        product_in_cart = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        unclaimed_product.slots.set([product_slot])
        incomplete_order.add_item(product_in_cart.pk, 1)

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user, Event.objects.first())

        #Assert
        product_result = product_info.get(pk=product_in_cart.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(unclaimed_product_result.slot_conflicts, [product_slot.pk])

    def test_get_product_info_for_user__product_conflicts_with_purchases(self):
        #Arrange
        product_slot = ProductSlot.objects.first()
        product_purchased = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first(), event=Event.objects.first())
        registration = Registration.objects.first()

        complete_order = Order.objects.create(registration=registration, session=Session.objects.create(pk='product_test', expire_date=timezone.now()))
        complete_order.add_item(product_purchased.pk, 1)
        complete_order.session = None
        complete_order.save()

        complete_order = Order.objects.create(registration=registration, session=Session.objects.create(pk='product_test2', expire_date=timezone.now()))
        complete_order.add_item(product_purchased.pk, 1)
        complete_order.session = None
        complete_order.save()

        unclaimed_product.slots.set([ProductSlot.objects.first()])

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user, Event.objects.first())

        #Assert
        product_result = product_info.get(pk=product_purchased.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(unclaimed_product_result.slot_conflicts, [product_slot.pk])

class RegistrationTestCase(TestCase):
    def setUp(self):
        setup_test_data()

    def test_with_outstanding_balances__unfinished_order(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, 0)

    def test_with_outstanding_balances__positive_balance_without_payments(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, 1000)



    def test_with_outstanding_balances__positive_balance(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=250, registration=registration)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, 750)



    def test_with_outstanding_balances__zero_balance(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        Invoice.objects.create(due_date=timezone.now(), amount=2000, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=1000, registration=registration)
        Payment.objects.create(stripe_session_id=random_string(), amount=2000, registration=registration)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, 0)

    def test_with_outstanding_balances__negative_balance(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=1500, registration=registration)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, -500)

class InvoiceTestCase(TestCase):
    def setUp(self):
        setup_test_data()

    def test_is_paid__no_payments(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        invoice1 = Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        invoice2 = Invoice.objects.create(due_date=timezone.now(), amount=1001, order=order, pay_at_checkout=True)
        invoice3 = Invoice.objects.create(due_date=timezone.now(), amount=1002, order=order)

        # Act
        invoices = with_is_paid(Invoice.objects.all())

        result1 = invoices.get(pk=invoice1.pk)
        result2 = invoices.get(pk=invoice2.pk)
        result3 = invoices.get(pk=invoice3.pk)

        # Assert
        self.assertEqual(result1.pay_at_checkout_invoices, 1001)
        self.assertEqual(result1.prior_pay_later_invoices, 0)
        self.assertEqual(result1.sum_of_payments, 0)
        self.assertEqual(result1.unpaid_amount_through_this, 2001)
        self.assertEqual(result1.unpaid_amount, 1000)
        self.assertEqual(result1.is_paid, False)

        self.assertEqual(result2.pay_at_checkout_invoices, 0)
        self.assertEqual(result2.prior_pay_later_invoices, 0)
        self.assertEqual(result2.sum_of_payments, 0)
        self.assertEqual(result2.unpaid_amount_through_this, 1001)
        self.assertEqual(result2.unpaid_amount, 1001)
        self.assertEqual(result2.is_paid, False)

        self.assertEqual(result3.pay_at_checkout_invoices, 1001)
        self.assertEqual(result3.prior_pay_later_invoices, 1000)
        self.assertEqual(result3.sum_of_payments, 0)
        self.assertEqual(result3.unpaid_amount_through_this, 3003)
        self.assertEqual(result3.unpaid_amount, 1002)
        self.assertEqual(result3.is_paid, False)

    def test_is_paid__paid_at_checkout(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        invoice1 = Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        invoice2 = Invoice.objects.create(due_date=timezone.now(), amount=1001, order=order, pay_at_checkout=True)
        invoice3 = Invoice.objects.create(due_date=timezone.now(), amount=1002, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=1001, registration=registration)

        # Act
        invoices = with_is_paid(Invoice.objects.all())

        result1 = invoices.get(pk=invoice1.pk)
        result2 = invoices.get(pk=invoice2.pk)
        result3 = invoices.get(pk=invoice3.pk)

        # Assert
        self.assertEqual(result1.unpaid_amount, 1000)
        self.assertEqual(result1.is_paid, False)

        self.assertEqual(result2.unpaid_amount, 0)
        self.assertEqual(result2.is_paid, True)

        self.assertEqual(result3.unpaid_amount, 1002)
        self.assertEqual(result3.is_paid, False)

    def test_is_paid__with_partial(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        invoice1 = Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        invoice2 = Invoice.objects.create(due_date=timezone.now(), amount=1001, order=order, pay_at_checkout=True)
        invoice3 = Invoice.objects.create(due_date=timezone.now(), amount=1002, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=1001, registration=registration)
        Payment.objects.create(stripe_session_id=random_string(), amount=500, registration=registration)

        # Act
        invoices = with_is_paid(Invoice.objects.all())

        result1 = invoices.get(pk=invoice1.pk)
        result2 = invoices.get(pk=invoice2.pk)
        result3 = invoices.get(pk=invoice3.pk)

        # Assert
        self.assertEqual(result1.unpaid_amount, 500)
        self.assertEqual(result1.is_paid, False)

        self.assertEqual(result2.unpaid_amount, 0)
        self.assertEqual(result2.is_paid, True)

        self.assertEqual(result3.unpaid_amount, 1002)
        self.assertEqual(result3.is_paid, False)

    def test_is_paid__with_one_later_payment(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        invoice1 = Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        invoice2 = Invoice.objects.create(due_date=timezone.now(), amount=1001, order=order, pay_at_checkout=True)
        invoice3 = Invoice.objects.create(due_date=timezone.now(), amount=1002, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=1001, registration=registration)
        Payment.objects.create(stripe_session_id=random_string(), amount=1000, registration=registration)

        # Act
        invoices = with_is_paid(Invoice.objects.all())

        result1 = invoices.get(pk=invoice1.pk)
        result2 = invoices.get(pk=invoice2.pk)
        result3 = invoices.get(pk=invoice3.pk)

        # Assert
        self.assertEqual(result1.unpaid_amount, 0)
        self.assertEqual(result1.is_paid, True)

        self.assertEqual(result2.unpaid_amount, 0)
        self.assertEqual(result2.is_paid, True)

        self.assertEqual(result3.unpaid_amount, 1002)
        self.assertEqual(result3.is_paid, False)

    def test_is_paid__fully_paid(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        invoice1 = Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        invoice2 = Invoice.objects.create(due_date=timezone.now(), amount=1001, order=order, pay_at_checkout=True)
        invoice3 = Invoice.objects.create(due_date=timezone.now(), amount=1002, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=1001, registration=registration)
        Payment.objects.create(stripe_session_id=random_string(), amount=2002, registration=registration)

        # Act
        invoices = with_is_paid(Invoice.objects.all())

        result1 = invoices.get(pk=invoice1.pk)
        result2 = invoices.get(pk=invoice2.pk)
        result3 = invoices.get(pk=invoice3.pk)

        # Assert
        self.assertEqual(result1.unpaid_amount, 0)
        self.assertEqual(result1.is_paid, True)

        self.assertEqual(result2.unpaid_amount, 0)
        self.assertEqual(result2.is_paid, True)

        self.assertEqual(result3.unpaid_amount, 0)
        self.assertEqual(result3.is_paid, True)

    def test_is_paid__over_paid(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        order.session = None
        order.save()
        invoice1 = Invoice.objects.create(due_date=timezone.now(), amount=1000, order=order)
        invoice2 = Invoice.objects.create(due_date=timezone.now(), amount=1001, order=order, pay_at_checkout=True)
        invoice3 = Invoice.objects.create(due_date=timezone.now(), amount=1001, order=order, pay_at_checkout=True)
        invoice4 = Invoice.objects.create(due_date=timezone.now(), amount=1002, order=order)
        invoice5 = Invoice.objects.create(due_date=timezone.now(), amount=1002, order=order)
        Payment.objects.create(stripe_session_id=random_string(), amount=1001, registration=registration)
        Payment.objects.create(stripe_session_id=random_string(), amount=10000, registration=registration)

        # Act
        invoices = with_is_paid(Invoice.objects.all())

        result1 = invoices.get(pk=invoice1.pk)
        result2 = invoices.get(pk=invoice2.pk)
        result3 = invoices.get(pk=invoice3.pk)
        result4 = invoices.get(pk=invoice4.pk)
        result5 = invoices.get(pk=invoice5.pk)

        # Assert
        self.assertEqual(result1.unpaid_amount, 0)
        self.assertEqual(result1.is_paid, True)

        self.assertEqual(result2.unpaid_amount, 0)
        self.assertEqual(result2.is_paid, True)

        self.assertEqual(result3.unpaid_amount, 0)
        self.assertEqual(result3.is_paid, True)

        self.assertEqual(result4.unpaid_amount, 0)
        self.assertEqual(result4.is_paid, True)

        self.assertEqual(result5.unpaid_amount, 0)
        self.assertEqual(result5.is_paid, True)
