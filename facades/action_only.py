import models.action as A


def add_action(cur, db, staff_id, bill_id, approved, action_type, approval_id='NULL', approved_at='NULL'):
    actions = A.Actions(cur, db)
    new_action = actions.add(bill_id, staff_id, approved, approval_id, action_type, approved_at)

    return new_action
