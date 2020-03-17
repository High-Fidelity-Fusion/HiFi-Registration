from django.test import TestCase
from registration.models import *
from django.core.exceptions import SuspiciousOperation


def setup_test_data():
    category_1 = ProductCategory.objects.create(name='Friday Classes', section='DANCE')
    slot_1 = ProductCategorySlot.objects.create(name='11amFriday', category=category_1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description')
    product.category_slots.set([slot_1])
    registration1 = Registration.objects.create()
    user_session1 = UserSession.objects.create()
    Order.objects.create(registration=registration1, user_session=user_session1)
    registration2 = Registration.objects.create()
    user_session2 = UserSession.objects.create()
    Order.objects.create(registration=registration2, user_session=user_session2)
    APFund.objects.create(contribution=2000, notes='notes')

class OrderTestCase(TestCase):
    def setUp(self):
        setup_test_data()

    def test_add_item__simple_case(self):
        order = Order.objects.first()
        product = Product.objects.first()
        registration = Registration.objects.first()

        result = order.add_item(product, 1)

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

    def test_add_item__two_quantity(self):
        order = Order.objects.first()
        product = Product.objects.first()

        result = order.add_item(product, 2)

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

        order.add_item(product, 1)
        result = order.add_item(product, 1)

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
            order.add_item(product, 3)
        order.add_item(product, 2)
        with self.assertRaises(SuspiciousOperation):
            order.add_item(product, 1)

    def test_add_item__out_of_stock(self):
        order = Order.objects.first()
        product = Product.objects.first()
        product.max_quantity_per_reg = 100
        product.save()

        result = order.add_item(product, 6)
        self.assertEqual(result, False)
        result = order.add_item(product, 5)
        self.assertEqual(result, True)
        result = order.add_item(product, 1)
        self.assertEqual(result, False)

    def test_add_item__slot_conflict(self):
        slot = ProductCategorySlot.objects.first()
        order = Order.objects.first()
        product = Product.objects.first()
        conflicting_product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 2, price=2000, title='title', subtitle='subtitle', description='description')
        conflicting_product.category_slots.set([slot])

        order.add_item(product, 1)
        with self.assertRaises(SuspiciousOperation):
            order.add_item(conflicting_product, 1)

        slot.is_exclusionary = False
        slot.save()
        order.add_item(conflicting_product, 1)

    def test_add_item__is_submitted(self):
        order = Order.objects.first()
        product = Product.objects.first()
        order.user_session = None
        order.save()

        self.assertEqual(order.is_submitted, True)
        self.assertEqual(Registration.objects.first().is_submitted, True)
        with self.assertRaises(SuspiciousOperation):
            order.add_item(product, 1)

    def test_remove_item__full_quantity(self):
        order = Order.objects.first()
        product = Product.objects.first()
        order.add_item(product, 1)

        order.remove_item(product, 1)

        self.assertEqual(OrderItem.objects.count(), 0)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 0)
        self.assertEqual(order.accessible_price, 0)

    def test_remove_item__partial_quantity(self):
        order = Order.objects.first()
        product = Product.objects.first()
        order.add_item(product, 2)

        order.remove_item(product, 1)

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
        order.add_item(product, 1)

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
        order.add_item(product, 1)
        order.claim_accessible_pricing()
        order2 = Order.objects.last()
        order2.add_item(product, 1)

        result = order2.claim_accessible_pricing()

        self.assertEqual(result, False)
        order2.refresh_from_db()
        self.assertEqual(order2.is_accessible_pricing, False)

    def test_claim_accessible_pricing__partially_ineligible(self):
        order = Order.objects.first()
        product = Product.objects.first()
        ineligible_product = Product.objects.create(is_ap_eligible=False, total_quantity=5, max_quantity_per_reg = 2, price=1000, title='title', subtitle='subtitle', description='description')
        order.add_item(product, 1)
        order.add_item(ineligible_product, 1)

        result = order.claim_accessible_pricing()

        self.assertEqual(result, True)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 3000)
        self.assertEqual(order.accessible_price, 1000)
        self.assertEqual(order.is_accessible_pricing, True)

    def test_claim_accessible_pricing__fully_ineligible(self):
        order = Order.objects.first()
        ineligible_product = Product.objects.create(is_ap_eligible=False, total_quantity=5, max_quantity_per_reg = 2, price=1000, title='title', subtitle='subtitle', description='description')
        order.add_item(ineligible_product, 1)

        result = order.claim_accessible_pricing()

        self.assertEqual(result, True)
        order.refresh_from_db()
        self.assertEqual(order.original_price, 1000)
        self.assertEqual(order.accessible_price, 1000)
        self.assertEqual(order.is_accessible_pricing, False)




