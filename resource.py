from datetime import timedelta
from abc import ABC, abstractmethod

from duration import Duration


class ResourceRequirement:

    def __init__(self, class_type, resource_type=None, quantity=None, org=None, dept=None, role=None):
        self.class_type = class_type
        self.resource_type = resource_type
        self.quantity = quantity
        self.org = org
        self.dept = dept
        self.role = role

    @classmethod
    def physical(cls, resource_type, quantity):
        return cls('physical', resource_type=resource_type, quantity=quantity)

    @classmethod
    def human(cls, quantity=0, org=None, dept=None, role=None):
        return cls('human', quantity=quantity, org=org, dept=dept, role=role)

    @classmethod
    def from_list(cls, resource_list):
        if not resource_list:
            return None
        class_list = []
        for item in resource_list:
            if item['class_type'] == 'human':
                class_list.append(cls.human(quantity=item['qty'], org=item['org'], dept=item['dept'], role=item['role']))
            elif item['class_type'] == 'physical':
                class_list.append(cls.physical(resource_type=item['type'], quantity=item['qty']))
            else:
                print('Resource class not supported.')
                raise TypeError
        return class_list


class Resource(ABC):
    pass


class HumanResource(Resource):
    def __init__(self, org, dept, role, availability):
        self.org = org
        self.dept = dept
        self.role = role
        self.availability = availability
        self.busy = False
        self.busy_until = None
        self.current_process_id = None
        self.current_activity_id = None

    def use(self, start_time, duration, process_id, activity_id):
        if not self.busy:
            self.busy = True
            self.busy_until = start_time + timedelta(seconds=duration)
            self.current_process_id = process_id
            self.current_activity_id = activity_id
        else:
            print("Can't use a busy resource")
            raise RuntimeError


class PhysicalResource(Resource):
    def __init__(self, type, quantity, delay):
        self.type = type
        self.quantity = quantity
        self.delay = Duration(delay)

    def get_quantity(self):
        return self.quantity

    def _add_quantity(self, amount):
        self.quantity += amount

    def recharge(self, amount):
        if amount >= 0:
            self._add_quantity(amount)

    def use(self, amount):
        if 0 <= amount <= self.get_quantity():
            self._add_quantity(-amount)
        else:
            print("Can't use more than the current quantity")
            raise AttributeError



