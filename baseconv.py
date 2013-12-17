#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Base(object):
    
    """
    Generic class for representing different bases.
    
    The ``Base`` class holds the information on a particular numerical base,
    such as the *words* and the *name*. The name exists solely for convenience
    when using the library in the interactive interpreter.
    
    The words are what make up a base. Decimal, for example, uses 10 words;
    these are (in order) `0`, `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, and `9`.
    Binary has only `0` and `1`. Any other numbers, strings or even arbitrary
    objects can be used as words, but order is important; if, for example, you
    use [`1`, `0`] as the word list for binary, all of the numbers you receive
    will be printed the wrong way; if, for example, you try to convert
    1010011010 into decimal, you will get 357 instead of the actual value 666.
    
    You may also optionally attach a ``format`` attribute to an instance of
    ``Base``. This should be a function which accepts one argument, a
    ``Number`` instance, and returns a string representation of that number.
    For example, the ``HEXADECIMAL`` base in the top-level of this module
    has a formatter which will prefix the hex representation of a number with
    ``'0x'``.
    
    Here is an example of how to create a base, taken from the actual 
    ``HEXADECIMAL`` variable found in the top-level of this module::
    
        >>> from baseconv import *
        >>> HEXADECIMAL = Base('0123456789ABCDEF', name='HEXADECIMAL')
        >>> HEXADECIMAL.format = (
        ... lambda n: '0x' + ''.join(map(str, n.values)))
    
    ``Base`` instances also feature a method called ``from_decimal`` which
    supports creating a ``Number`` instance, in the given base, from a decimal
    number (i.e. a Python ``int`` instance). Here is an example of how to use
    ``from_decimal``:
        
        >>> from baseconv import *
        >>> num = BINARY.from_decimal(666)
        >>> print num
        0b1010011010
    """
    
    def __init__(self, words, name=''):
        self.__words = words
        if not name:
            # Make a sensible default. Because it's nice to have a name.
            name = 'base%d' % (self.length,)
        self.name = name
    
    def __call__(self, values):
        # Remember, ``self`` is the base, not the number.
        return Number(self, values=values, indices=False)
    
    def __repr__(self):
        return 'Base(%r, %r)' % (self.words, self.name)
    
    def __get_words(self):
        return self.__words
    
    def __get_length(self):
        return len(self.words)
    
    def from_decimal(self, decimal):
        """Convert a Python ``int`` into a ``Number`` of this base."""
        # Get a ``DECIMAL`` instance, and just change its base.
        new = self([])
        new.decimal = decimal
        return new
    
    words = property(__get_words)
    length = property(__get_length)


class Number(object):
    
    """
    Represent a specific number in a base, and provide methods for conversion.
    
    The ``Number`` class holds a representation of a number in a particular
    base. This base is an instance of the ``Base`` class, and the number is
    accessible through several descriptors:
        
        ``decimal``
            The ``decimal`` attribute holds a Python ``int`` (or ``long``)
            with the value of the number in base-10, which is the typical
            counting system. ``decimal`` may be set to a value also, which
            will update the number to represent the new value.
        
        ``indices``
            Indices represent a number in a particular base. For example, if
            a base's words are ``a``,``b``, ``c`` and ``d``, the number
            ``dbbca`` would be represented by the list ``[3, 1, 1, 2, 0]``.
            The integers in this list all point to positions within the base's
            word list. Internally, all numbers are stored like this.
        
        ``values``
            This is similar to the index representation, only it uses the
            actual values from the base's word list; following on from the
            previous example, ``[3, 1, 1, 2, 0]`` would be replaced by
            ``['d', 'b', 'b', 'c', 'a']``.
    
    The base of a number can be accessed via the ``base`` descriptor.
    Accessing this will return the instance of the base. You can also convert
    a number's base by changing it's ``base`` attribute::
    
        >>> from baseconv import *
        >>> num = Number(BINARY, '1010011010')
        >>> print num
        0b1010011010
        >>> num.base = DECIMAL
        >>> print num
        666
        >>> num.base = HEXADECIMAL
        >>> print num
        0x29A
    
    Hint: as a shortcut to instantiating a ``Number`` instance with a base and
    list of values, you can call the ``Base`` instance. For example::
        
        >>> from baseconv import *
        >>> num1 = Number(BINARY, '1010011010')
        >>> num2 = BINARY('1010011010')
        >>> num1.decimal == num2.decimal
        True
    
    
    """
    
    def __init__(self, base, values=[], indices=False):
        """
        Initialize a ``Number`` instance.
        
        This function takes a ``Base`` instance, an optional list of values,
        and a flag specifying whether those values are actually words from the
        base or indices of words in the base's wordlist.
        
        The first positional argument should be a ``Base`` instance. Several
        common bases are provided in the top-level of this module; these are
        ``BINARY``, ``DECIMAL``, ``HEXADECIMAL`` and ``OCTAL``. Note that
        ``Base`` instances are callable; ``base.__call__(values)`` is the same
        as ``Number(base, values=values, indices=False)``.
        
        The ``values`` keyword is the list of words which represent the
        number. They will be checked for validity, and invalid numbers will
        raise an ``AssertionError``. With the ``indices`` keyword argument set
        to ``True``, the value list should be a list of integers, each of
        which will represent a position within the given base's wordlist.
        """
        self.__base = base
        if indices:
            self.indices = values
        else:
            self.values = values
    
    def __repr__(self):
        return 'Number(%s, %r)' % (self.base.name, self.values)
    
    def __str__(self):
        # This allows bases to define their own ways of printing numbers. For
        # example, hexadecimal is shown as '0xf0ff0f', etc.
        if hasattr(self.base, 'format'):
            return self.base.format(self)
        return ''.join(map(str, self.values))
    
    def zfill(self, length):
        """
        Show a number with at least a certain number of zeros before.
        
        This is pretty much the same as 
        """
        s = str(self)
        while len(s) < length:
            if len(self.base.words[0]) > (length - len(s)):
                return s
            s = self.base.words[0] + s
        return s
    
    def __get_base(self):
        return self.__base
    
    def __set_base(self, base):
        # Pretty simple; the number's decimal value won't change, and then the
        # other parts will fall into place when re-setting this via the
        # descriptor.
        old_decimal = self.decimal + 0
        self.__base = base
        self.decimal = old_decimal
    
    def __get_decimal(self):
        decimal = 0
        for index, value in enumerate(reversed(self.__indices)):
            decimal += value * (self.base.length ** index)
        return decimal

    def __set_decimal(self, decimal):
        indices = []
        # Copy it to stop this method from mutating another variable.
        number = decimal + 0
        while number:
            indices.insert(0, number % self.base.length)
            number = number // self.base.length
        self.indices = indices
    
    def __get_indices(self):
        return self.__indices
    
    def __set_indices(self, indices):
        new_indices = []
        for index in indices:
            # Check that the index is valid within the base's wordlist.
            if index >= self.base.length:
                raise KeyError('Index')
            new_indices.append(index)
        self.__indices = new_indices
    
    def __get_values(self):
        values = map(self.base.words.__getitem__, self.indices)
        # Make sure all words in the base are single characters. Otherwise,
        # joining the list could give an erroneous representation.
        if all(isinstance(x, basestring) for x in self.base.words) and set(
            map(len, self.base.words)) == set([1]):
            # If all is OK, we return a string.
            return ''.join(values)
        # If this is going to be a problem, act safely and return a list.
        return values
            
    
    def __set_values(self, values):
        indices = []
        for value in values:
            # Check the value for validity.
            if value not in self.base.words:
                raise ValueError('%r not in wordlist for %r' %
                    (value, self.base))
            # We're assuming that the base's wordlist has no duplicates.
            indices.append(self.base.words.index(value))
        self.__indices = indices
    
    base = property(__get_base, __set_base)
    decimal = property(__get_decimal, __set_decimal)
    indices = property(__get_indices, __set_indices)
    values = property(__get_values, __set_values)


DECIMAL = Base('0123456789', 'DECIMAL')

BINARY = Base('01', 'BINARY')
BINARY.format = (
    lambda n: '0b' + ''.join(map(str, n.values)))

HEXADECIMAL = Base('0123456789ABCDEF', 'HEXADECIMAL')
HEXADECIMAL.format = (
    lambda n: '0x' + ''.join(map(str, n.values)))

OCTAL = Base('01234567', 'OCTAL')
OCTAL.format = (
    lambda n: '0o' + ''.join(map(str, n.values)))

ALPHA_LOWER = Base('abcdefghijklmnopqrstuvwxyz', 'ALPHA_LOWER')
ALPHA_UPPER = Base('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'ALPHA_UPPER')
ALPHA = Base('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz', 'ALPHA')
BYTES = Base(''.join(chr(i) for i in xrange(256)), 'BYTES')

if __name__ == '__main__':
    import doctest
    doctest.testmod()
