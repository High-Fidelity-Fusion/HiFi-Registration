from registration.models import *

def insert_data():
    event1 = Event.objects.create(name='Event #1', slug='event1', policies='## Code of Conduct\nBe **excellent** to each other n that good stuff.\n## Yay', requires_vaccination=False)
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
    product = Product.objects.create(total_quantity=9999999, max_quantity_per_reg = 3, price=1500, title='Cypress Test Product Multi', description='description', category=category, is_ap_eligible=False, event=event1)

    category = ProductCategory.objects.create(name='Dance Passes', section='DANCE', is_slot_based=False, rank=3, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Friday', subtitle='theme: rebecca black', description='description', category=category, is_compable=True, event=event1)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Saturday', subtitle='theme: Satyrday', description='description', category=category, is_compable=True, event=event1)
    product = Product.objects.create(total_quantity=9999999, max_quantity_per_reg = 1, price=2000, title='Cypress Test Product Single', description='description', category=category, is_compable=True, event=event1)
    APFund.objects.create(contribution=100000, notes='notes', event=event1)

    event2 = Event.objects.create(name='Event #2', slug='event2', requires_vaccination=True)
    category = ProductCategory.objects.create(name='Dance Tickets', section='DANCE', is_slot_based=False, rank=2, event=event2)
    product = Product.objects.create(total_quantity=5, max_quantity_per_reg = 1, price=2000, title='Friday', subtitle='theme: space face', description='description', category=category, is_compable=True, event=event2)
    SiteConfig.objects.create(site_name='Test Registration Site')


# This is used for manual testing data
def setup_cypress_test_data():
    Order.objects.all().delete()
    Product.slots.through.objects.all().delete()
    Product.objects.all().delete()
    ProductCategory.objects.all().delete()
    ProductSlot.objects.all().delete()
    APFund.objects.all().delete()
    Registration.objects.all().delete()
    Event.objects.all().delete()
    SiteConfig.objects.all().delete()
    User.objects.filter(email__startswith='cy_test_').delete()

    insert_data()