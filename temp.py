class Foo:
    def __init__(self, bar: str, zing: bool):
        # Set attributes
        self._bar = bar
        self._zing = zing

    @property
    def bar(self):
        # Init bar property
        return self._bar

    @bar.getter
    def bar(self):
        # Make bar uppercase
        return self._bar.upper()

    @bar.setter
    def bar(self, new_bar):
        # Only allow bar to be up to 6 characters long
        if len(new_bar) > 6:
            print('Bar too long!')
        else:
            self._bar = new_bar

    @property
    def zing(self):
        # Init zing property
        return self._zing

    @zing.setter
    def zing(self, new_zing):
        # Check if new_zing is a boolean
        if type(new_zing) is not bool:
            print('Zing must be a boolean!')
        else:
            # Update zing with new zing
            self._zing = new_zing

    @property
    def no_edit(self):
        # Init a immutable property
        return 'Hi'


new_foo = Foo('John', False)
print(new_foo.bar)  # Goes to Foo.bar.getter
# JOHN

new_foo.bar = '1234567'  # Goes to Foo.bar.setter
# Bar too long!

print(new_foo.bar)  # Goes to Foo.bar.getter
# JOHN

new_foo.bar = 'Steve'  # Goes to Foo.bar.setter

print(new_foo.bar)
# STEVE

print(new_foo.zing)  # Goes to Foo.zing, as there is no getter
# False

new_foo.zing = 'Hi'  # Goes to Foo.zing.setter
# Zing must be a boolean!

new_foo.zing = True  # Goes to Foo.zing.setter

print(new_foo.zing)
# True

print(new_foo.no_edit)  # Go to Foo.no_edit

new_foo.no_edit = ''  # Try to go to Foo.no_edit.setter
# AttributeError: property 'no_edit' of 'Foo' object has no setter
