class Redirect(Exception):

    def __init__(self, redirect_to, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

        self.redirect_to = redirect_to
