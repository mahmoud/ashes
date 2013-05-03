from __future__ import unicode_literals

from .core import AshesTest

heading = 'comparator helpers'


class eq_const(AshesTest):
    template = '{@eq key="blue" value="blue"}Blue{/eq}, the color of her eyes.'
    json_context = '{}'
    rendered = 'Blue, the color of her eyes.'


class ne_const(AshesTest):
    template = '{@ne key="green" value="green"}Blue{:else}Green{/ne}, the color of her eyes.'
    json_context = '{}'
    rendered = 'Green, the color of her eyes.'


class gt_const(AshesTest):
    template = 'Mahmoud ate {@gt key="4" value=2}hella{:else}a reasonable number of{/gt} bananas!'
    json_context = '{}'
    rendered = 'Mahmoud ate hella bananas!'


class gte_const(AshesTest):
    template = 'Mahmoud ate {@gte key=2 value=3}hella{:else}a reasonable number of{/gte} bananas!'
    json_context = '{}'
    rendered = 'Mahmoud ate a reasonable number of bananas!'


class lt_const(AshesTest):
    template = 'Kyle {@lt key="2" value=3}does not even lift{:else}totally lifts{/lt}, bro.'
    json_context = '{}'
    rendered = 'Kyle does not even lift, bro.'


class lte_const(AshesTest):
    template = 'Kyle {@lte key="3" value=2}does not even lift{:else}totally lifts{/lte}, bro.'
    json_context = '{}'
    rendered = 'Kyle totally lifts, bro.'


class eq_var(AshesTest):
    template = 'Ben is an {@eq key=enabler value="enabled"}enabler{/eq}.'
    json_context = '{"enabler": "enabled"}'
    rendered = 'Ben is an enabler.'

class ne_var(AshesTest):
    template = 'Ben is {@ne key=enabler value="disabled"}an enabler{:else}a good influence for all the boys and girls who go to bed on time{/ne}.'
    json_context = '{"enabler": "enabled"}'
    rendered = 'Ben is an enabler.'


class gt_var(AshesTest):
    template = 'Mahmoud ate {@gt key=banana_count value=2}hella{:else}a reasonable number of{/gt} bananas for dinner!'
    json_context = '{"banana_count": 4}'
    rendered = 'Mahmoud ate hella bananas for dinner!'


class gte_var(AshesTest):
    template = 'Mahmoud ate {@gte key=banana_count value=3}hella{:else}a reasonable number of{/gte} bananas!'
    json_context = '{"banana_count": 2}'
    rendered = 'Mahmoud ate a reasonable number of bananas!'


class lt_var(AshesTest):
    template = 'Kyle {@lt key=gym_memberships value=3}does not even lift{:else}totally lifts{/lt}, bro.'
    json_context = '{"gym_memberships": 2}'
    rendered = 'Kyle does not even lift, bro.'


class lte_var(AshesTest):
    template = 'Kyle {@lte key=gym_memberships value=2}does not even lift{:else}totally lifts{/lte}, bro.'
    json_context = '{"gym_memberships": 30}'
    rendered = 'Kyle totally lifts, bro.'
