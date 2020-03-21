from ..forms import *


# router
# serves up next modelform based on registration object data, and user input
# has two types of subroutine for each modelform: route and prep.
# route determines which page to show next
# prep returns the new modelform and appropriate navigation button layout
def router(*args):
    f = None

    # if arguments are passed, split the registration object and navigation direction
    if args:
        reg_obj = args[0]
        current_page = args[1]
        direction = args[2]
        if 'policy_form' in current_page:
            f = route_policy(reg_obj, direction)
        elif 'accessibility_form' in current_page:
            f = route_accessibility(reg_obj, direction)

    # if no arguments are passed, assume we are starting a new form.
    else:
        f = policy_form()  # currently, the first page is policy_form, but that will change.

    # update current page info to reflect new modelform type
    current_page = f.formtype()

    # determine which navigation buttons to show on this page
    if 'policy_form' in current_page:
        context = {'next': 'next'}
    elif 'accessibility_form' in current_page:
        context = {'prev': 'prev', 'submit': 'submit'}
    else:
        context = {'prev': 'prev', 'next': 'next'}
    context['form'] = f
    context['current_page'] = current_page
    return context


def route_policy(reg_obj, direction):
    if 'next' in direction:
        f = accessibility_form(instance=reg_obj)
        return f


def route_accessibility(reg_obj, direction):
    if 'prev' in direction:
        f = policy_form(instance=reg_obj)
        return f


# modelform selector
# Identifies which modelform needs to be saved based on the request.POST data
def mf_sel(request_post, current_page, *args):
    instance = None
    if args:
        instance = args[0]

    # Instantiate correct modelform object using appropriate model instance and populate it with post data
    # We need the name of a field that is unique to establish which modelform to use.
    # Since we do not repeat fields during registration, any field will do.
    # policy_form() instantiates a modelform of type policy_form.
    # Once instantiated, the object has fields.
    # policy_form().fields returns a dictionary of the field names and fields.
    # We are interested in the names of the fields, so we take the keys of the dictionary and omit the values:
    # policy_form().fields.keys()
    # iter() turns those keys into an array through which we can iterate
    # next() iterates once, to the first object, which is the name of the first field in the modelform
    if next(iter(policy_form().fields.keys())) in request_post:
        f = policy_form(request_post, instance=instance)
    elif next(iter(accessibility_form().fields.keys())) in request_post:
        f = accessibility_form(request_post, instance=instance)
    elif next(iter(tmpedit().fields.keys())) in request_post:
        f = tmpedit(request_post, instance=instance)
    return f
