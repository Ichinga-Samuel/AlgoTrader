def func(self, *, a=1, b=6):
    print(a, b, )
    # self.kwargs['a'] = 9
    return a+b


class Tear:

    def __init__(self, *, function, **kwargs):
        self.function = function
        self.kwargs = kwargs
        self.b = 7

    def __call__(self):
        return self.function(self=self, **self.kwargs)


te = Tear(function=func)
ab = te()
c = te()
print(ab, c)
