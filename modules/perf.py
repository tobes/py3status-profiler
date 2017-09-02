class Py3status:
    """
    Module for testing performance.
    This simple module just updates it's output

    It is designed so that it is a predictable load
    """

    cache_timeout = 1
    delay = False
    format = '\?color=fizzbuzz {name} {count}'

    def post_config_hook(self):
        self.count = 0

        # we get the name of the module in a bad way
        self.name = self.py3._module.module_inst

        # have some slightly more unique formats
        count = int(self.name.split('_')[-1])
        if count in [1, 3, 5]:
            self.format = '{} [{}]'.format(count, self.format)

    def output(self):
        self.count += 1

        count = self.count

        # if delay is set we only update the count value every
        # three runs so that the formatter gets the same data
        # as this is a common occurance
        if self.delay:
            count = count // 3

        # we add some color in a similar way to the game fizz buzz
        # the color is made available as fizzbuzz in the formatter
        color = None
        if count % 3 == 0:
            color = self.py3.COLOR_GOOD
        elif count % 5 == 0:
            color = self.py3.COLOR_DEGRADED
        if count % 15 == 0:
            color = '#FF00FF'
        self.color_fizzbuzz = color

        data = {'count': count, 'name': self.name}

        full_text = self.py3.safe_format(self.format, data)

        return {
            'full_text': full_text,
            'cached_until': self.py3.time_in(self.cache_timeout),
        }
