from django.test import TestCase
from registration.models import *
from django.core.exceptions import SuspiciousOperation
from django.contrib.sessions.models import Session
from django.utils import timezone
from datetime import datetime

def clean_db():
    Product.slots.through.objects.all().delete()
    Product.objects.all().delete()
    ProductCategory.objects.all().delete()
    ProductSlot.objects.all().delete()
    Order.objects.all().delete()
    Registration.objects.all().delete()
    APFund.objects.all().delete()
    Session.objects.all().delete()
    CompCode.objects.all().delete()

def setup_test_data():
    category_1 = ProductCategory.objects.create(name='Friday Classes', section='DANCE', rank=3)
    slot_1 = ProductSlot.objects.create(name='11amFriday', rank=3)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description', category=category_1)
    product.slots.set([slot_1])
    user1 = User.objects.create_user(email='asdf@asdf.asdf')
    registration1 = Registration.objects.create(user=user1)
    session1 = Session.objects.create(pk='a', expire_date=timezone.now())
    Order.objects.create(registration=registration1, session=session1)
    registration2 = Registration.objects.create()
    session2 = Session.objects.create(pk='b', expire_date=timezone.now())
    Order.objects.create(registration=registration2, session=session2)
    APFund.objects.create(contribution=2000, notes='notes')
    CompCode.objects.create(type=CompCode.STAFF, max_uses=1)

def setup_products():
    Order.objects.all().delete()
    Product.slots.through.objects.all().delete()
    Product.objects.all().delete()
    ProductCategory.objects.all().delete()
    ProductSlot.objects.all().delete()

    slot1 = ProductSlot.objects.create(name='1pm', rank=3)
    slot2 = ProductSlot.objects.create(name='11am', rank=2)

    category = ProductCategory.objects.create(name='Teacher Training', section='CLASS', is_slot_based=False, rank=2)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Full Weekend Teacher Training', subtitle='subtitle', description='description', category=category)
    product.slots.add(slot1)
    product.slots.add(slot2)

    category = ProductCategory.objects.create(name='Friday', section='CLASS', rank=3)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Dance like a Baby Giraffe', subtitle='featuring a real baby giraffe!', description='description', category=category)
    product.slots.add(slot1)
    product = Product.objects.create(total_quantity=0, max_quantity_per_reg = 1, price=2000, title='Dance like you are Out of Stock', subtitle='subtitle', description='description', category=category)
    product.slots.add(slot1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Ants in your Pants', subtitle='teacher: Ant Man', description='We are going to put literal ants in your literal pants.', category=category)
    product.slots.add(slot2)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Long Class', subtitle='subtitle', description='description', category=category)
    product.slots.add(slot1)
    product.slots.add(slot2)

    category = ProductCategory.objects.create(name='Clothing', section='MERCH', is_slot_based=False, rank=2)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 3, price=1500, title='t-shirt', subtitle='subtitle', description='description', category=category, is_ap_eligible=False)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 10, price=1500, title='hoodie', subtitle='subtitle', description='description', category=category, is_ap_eligible=False)

    category = ProductCategory.objects.create(name='Dance Passes', section='DANCE', is_slot_based=False, rank=3)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Friday', subtitle='theme: rebecca black', description='description', category=category, is_compable=True)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Saturday', subtitle='theme: Satyrday', description='description', category=category, is_compable=True)

class OrderTestCase(TestCase):
    def setUp(self):
        clean_db()
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
        conflicting_product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
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
        registration = Registration.objects.create()
        registration.comp_code = comp_code
        registration.save()
        order = Order.objects.create(registration=registration, session=Session.objects.create(pk='test_add_item__comped', expire_date=timezone.now()))
        non_compable_product = Product.objects.first()
        compable_product = Product.objects.create(is_compable=True, total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first())

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
        ineligible_product = Product.objects.create(is_ap_eligible=False, total_quantity=5, max_quantity_per_reg = 2, price=1000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
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
        ineligible_product = Product.objects.create(is_ap_eligible=False, total_quantity=5, max_quantity_per_reg = 2, price=1000, title='title', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
        order.add_item(ineligible_product.pk, 1)

        result = order.claim_accessible_pricing()

        self.assertEqual(result, True)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 1000)
        self.assertEqual(order.accessible_price, 1000)
        self.assertEqual(order.is_accessible_pricing, False)

class ProductTestCase(TestCase):
    def setUp(self):
        clean_db()
        setup_test_data()

    def test_get_product_info_for_user(self):
        #Arrange
        product = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        complete_order = Order.objects.create(registration=registration, session=Session.objects.create(pk='product_test', expire_date=timezone.now()))

        incomplete_order.add_item(product.pk, 1)
        complete_order.add_item(product.pk, 1)
        complete_order.session = None
        complete_order.save()

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user)
        product_result = product_info.get(pk=product.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)

        #Assert
        self.assertEqual(product_info.filter(pk=product.pk).count(), 1)
        self.assertEqual(product_result.quantity_purchased, 1)
        self.assertEqual(unclaimed_product_result.quantity_purchased, 0)
        self.assertEqual(product_result.quantity_claimed, 1)
        self.assertEqual(unclaimed_product_result.quantity_claimed, 0)
        self.assertEqual(product_result.available_quantity, 3)
        self.assertEqual(unclaimed_product_result.available_quantity, 5)

    def test_get_product_info_for_user__empty_cart(self):
        #Arrange
        product = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
        registration = Registration.objects.first()

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user)
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
        setup_products()
        products = Product.objects.filter(slots=ProductSlot.objects.first()).filter(slots=ProductSlot.objects.last())
        product1 = products.first()
        product2 = products.last()
        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        incomplete_order.add_item(product1.pk, 1)

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user)
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
        self.assertEqual(product_result2.slot_conflicts, [ProductSlot.objects.last().pk, ProductSlot.objects.first().pk])

    def test_get_product_info_for_user__product_does_not_conflict(self):
        #Arrange
        product_slot = ProductSlot.objects.first()
        product = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        complete_order = Order.objects.create(registration=registration, session=Session.objects.create(pk='product_test', expire_date=timezone.now()))

        incomplete_order.add_item(product.pk, 1)
        complete_order.add_item(product.pk, 1)
        complete_order.session = None
        complete_order.save()

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user)

        #Assert
        product_result = product_info.get(pk=product.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(unclaimed_product_result.slot_conflicts, [])

    def test_get_product_info_for_user__product_conflicts_with_cart(self):
        #Arrange
        product_slot = ProductSlot.objects.first()
        product_in_cart = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
        registration = Registration.objects.first()
        incomplete_order = registration.order_set.first()
        unclaimed_product.slots.set([product_slot])
        incomplete_order.add_item(product_in_cart.pk, 1)

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user)

        #Assert
        product_result = product_info.get(pk=product_in_cart.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(unclaimed_product_result.slot_conflicts, [product_slot.pk])

    def test_get_product_info_for_user__product_conflicts_with_purchase(self):
        #Arrange
        product_slot = ProductSlot.objects.first()
        product_purchased = Product.objects.first()
        unclaimed_product = Product.objects.create(total_quantity=5, max_quantity_per_reg=2, price=2000, title='title2', subtitle='subtitle', description='description', category=ProductCategory.objects.first())
        registration = Registration.objects.first()
        complete_order = Order.objects.create(registration=registration, session=Session.objects.create(pk='product_test', expire_date=timezone.now()))

        complete_order.add_item(product_purchased.pk, 1)
        complete_order.session = None
        complete_order.save()

        unclaimed_product.slots.set([ProductSlot.objects.first()])

        #Act
        product_info = Product.objects.get_product_info_for_user(registration.user)

        #Assert
        product_result = product_info.get(pk=product_purchased.pk)
        unclaimed_product_result = product_info.get(pk=unclaimed_product.pk)
        self.assertEqual(product_result.slot_conflicts, [])
        self.assertEqual(unclaimed_product_result.slot_conflicts, [product_slot.pk])

class RegistrationTestCase(TestCase):
    def setUp(self):
        clean_db()
        setup_test_data()

    def test_with_outstanding_balances__positive_balance_without_payments(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        Invoice.objects.create(amount=1000, order=order)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, 1000)



    def test_with_outstanding_balances__positive_balance(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        Invoice.objects.create(amount=1000, order=order)
        Payment.objects.create(amount=250, registration=registration)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, 750)



    def test_with_outstanding_balances__zero_balance(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        Invoice.objects.create(amount=1000, order=order)
        Payment.objects.create(amount=1000, registration=registration)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, 0)

    def test_with_outstanding_balances__negative_balance(self):
        # Arrange
        registration = Registration.objects.first()
        order = registration.order_set.first()
        Invoice.objects.create(amount=1000, order=order)
        Payment.objects.create(amount=1500, registration=registration)

        # Act
        registration = Registration.objects.filter(pk=registration.pk).with_outstanding_balances().get()

        # Assert
        self.assertEqual(registration.outstanding_balance, -500)

