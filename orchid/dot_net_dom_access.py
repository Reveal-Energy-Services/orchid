#
# This file is part of Orchid and related technologies.
#
# Copyright (c) 2017-2020 Reveal Energy Services.  All Rights Reserved.
#
# LEGAL NOTICE:
# Orchid contains trade secrets and otherwise confidential information
# owned by Reveal Energy Services. Access to and use of this information is 
# strictly limited and controlled by the Company. This file may not be copied,
# distributed, or otherwise disclosed outside of the Company's facilities 
# except under appropriate precautions to maintain the confidentiality hereof, 
# and may not be used in any way not expressly authorized by the Company.
#

import toolz.curried as toolz


def dom_property(attribute_name, docstring):
    """
    Return the property of the DOM corresponding to `attribute_name` with doc string.
    :param attribute_name: The name of the original attribute.
    :param docstring: The doc string to be attached to the resulting property.
    :return: The property value from the DOM.
    """

    # This implementation is based on the StackOverflow post:
    # https://stackoverflow.com/questions/36580931/python-property-factory-or-descriptor-class-for-wrapping-an-external-library
    #
    # More importantly, it resolves an issue I was experiencing with PyCharm: when I used `property` directly
    # in the class definition, PyCharm reported "Property 'xyz' could not be read. I think it might have been
    # than I needed to apply `curry` to the "getter method" I also defined in the class in order to pass he
    # attribute name at definition time (because `self` was only available at run-time).
    def getter(self):
        # The function, `thread_last`, from `toolz.curried`, "splices" threads a value (the first argument)
        # through each of the remaining functions as the *last* argument to each of these functions.
        result = toolz.thread_last(
            attribute_name.split('_'),  # split the attribute name into words
            toolz.map(str.capitalize),  # capitalize each word
            lambda capitalized_pieces: ''.join(capitalized_pieces),  # concatenate words
            toolz.partial(getattr, self._adaptee))  # look up this new attribute in the adaptee
        return result

    # Ensure no setter for the DOM properties
    return property(fget=getter, doc=docstring, fset=None)


def transformed_dom_property(attribute_name, docstring, transformer):
    """
    Return the transformed property of the DOM corresponding to `attribute_name`.
    :param attribute_name: The name of the original attribute.
    :param docstring: The doc string to be attached to the resulting property.
    :param transformer: A callable invoked on the value returned by the .NET DOM property.
    :return: The transformed property value from the DOM.
    """

    # This implementation is based on the StackOverflow post:
    # https://stackoverflow.com/questions/36580931/python-property-factory-or-descriptor-class-for-wrapping-an-external-library
    #
    # More importantly, it resolves an issue I was experiencing with PyCharm: when I used `property` directly
    # in the class definition, PyCharm reported "Property 'xyz' could not be read. I think it might have been
    # than I needed to apply `curry` to the "getter method" I also defined in the class in order to pass he
    # attribute name at definition time (because `self` was only available at run-time).
    def getter(self):
        # The function, `thread_last`, from `toolz.curried`, "splices" threads a value (the first argument)
        # through each of the remaining functions as the *last* argument to each of these functions.
        raw_result = toolz.thread_last(
            attribute_name.split('_'),  # split the attribute name into words
            toolz.map(str.capitalize),  # capitalize each word
            lambda capitalized_pieces: ''.join(capitalized_pieces),  # concatenate words
            toolz.partial(getattr, self._adaptee))  # look up this new attribute in the adaptee
        result = transformer(raw_result)
        return result

    # Ensure no setter for the DOM properties
    return property(fget=getter, doc=docstring, fset=None)


def transformed_dom_property_iterator(attribute_name, docstring, transformer):
    """
    Return transformed collection property of the DOM corresponding to `attribute_name` with doc string, `docstring`.
    :param attribute_name: The name of the original attribute.
    :param docstring: The doc string to be attached to the resultant property.
    :param transformer: A callable invoked on the value returned by the .NET DOM property.
    :return: The transformed property iterator from the DOM.
    """

    # This implementation is based on the StackOverflow post:
    # https://stackoverflow.com/questions/36580931/python-property-factory-or-descriptor-class-for-wrapping-an-external-library
    #
    # More importantly, it resolves an issue I was experiencing with PyCharm: when I used `property` directly
    # in the class definition, PyCharm reported "Property 'xyz' could not be read. I think it might have been
    # than I needed to apply `curry` to the "getter method" I also defined in the class in order to pass he
    # attribute name at definition time (because `self` was only available at run-time).
    def getter(self):
        # The function, `thread_last`, from `toolz.curried`, "splices" threads a value (the first argument)
        # through each of the remaining functions as the *last* argument to each of these functions.
        container = toolz.thread_last(
            attribute_name.split('_'),  # split the attribute name into words
            toolz.map(str.capitalize),  # capitalize each word
            lambda capitalized_pieces: ''.join(capitalized_pieces),  # concatenate words
            toolz.partial(getattr, self._adaptee))  # look up this new attribute in the adaptee
        result = toolz.map(transformer, container.Items)
        return result

    # Ensure no setter for the DOM properties
    return property(fget=getter, doc=docstring, fset=None)
