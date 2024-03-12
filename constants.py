EVENT_CHANCES = {
    'order': 0.5,
    'seat_change': 0.1,
    'menu_change': 0.1,
    'bill': 0.1,
    'staff_illness': 0.05,
    'staff_leave': 0.005,
    'staff_hire': 0.005,
    'staff_fire': 0.005,
    'item_has_note': 0.1,
    'booking_cancels': 0.03,
    'booking_has_comment': 0.2,
    'customer_wants_another_round': 0.4
}

ITEM_NOTES = ['No ice', 'no fruit', 'no glass', 'no straw']

ACTION_TYPES = [
    'create',
    'approve',
    'delete',
    'update',
    'update_approve',
    'update_bill_items',
    'discount',
    'refund',
    'void',
    'payment'
]

"""
Comments have probability
    1. Has dog: 20%
    2. Gluten free: 10%
    3. Vegetarian: 10%
    4. Vegan: 20%
    5. Birthday: 20%
    6. Anniversary: 20%
"""

BOOKING_COMMENTS = ['Has dog', 'Gluten free', 'Vegetarian', 'Vegan', 'Birthday', 'Anniversary']
BOOKING_WEIGHTS = [2, 1, 1, 2, 2, 2]

