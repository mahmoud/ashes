from __future__ import unicode_literals

from .core import AshesTest

heading = 'comparator helpers'

class const_eq(AshesTest):
    template = 'The pen is {@eq key="blue" value="blue"}blue{/eq}!'
    json_context = '{}'
    rendered = 'The pen is blue!'


class const_ne(AshesTest):
    template = 'The pen is {@ne key="black" value="black"}blue{:else}black{/ne}!'
    json_context = '{}'
    rendered = 'The pen is black!'


class const_gt(AshesTest):
    template = 'Mahmoud ate {@gt key="4" value=2}hella{:else}a reasonable number of{/gt} bananas!'
    json_context = '{}'
    rendered = 'Mahmoud ate hella bananas!'


class const_gte(AshesTest):
    template = 'Mahmoud ate {@gte key=2 value=3}hella{:else}a reasonable number of{/gte} bananas!'
    json_context = '{}'
    rendered = 'Mahmoud ate a reasonable number of bananas!'


class const_lt(AshesTest):
    template = 'Kyle {@lt key="2" value=3}does not even lift{:else}totally lifts{/lt}, bro.'
    json_context = '{}'
    rendered = 'Kyle does not even lift, bro.'


class const_lte(AshesTest):
    template = 'Kyle {@lte key="3" value=2}does not even lift{:else}totally lifts{/lte}, bro.'
    json_context = '{}'
    rendered = 'Kyle totally lifts, bro.'
