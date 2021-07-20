from .misc import flatten, \
    quote_value


class KeyValuePair:
    def __init__(self, toks):
        self.toks = toks

    @property
    def key(self):
        return self.toks[1]

    @property
    def value(self):
        return self.toks[5]

    def __repr__(self):
        return f'KeyValuePair({self.toks})'

    def __str__(self):
        return flatten([ self.toks[0], quote_value(self.key) ] + self.toks[2:5] +
            [ quote_value(self.value) ] + self.toks[6:])


class KeyValueAppendPair:
    def __init__(self, toks):
        self.toks = toks

    @property
    def key(self):
        return self.toks[1]

    @property
    def value(self):
        return self.toks[5]

    def __repr__(self):
        return f'KeyValueAppendPair({self.toks})'

    def __str__(self):
        return flatten([ self.toks[0], quote_value(self.key) ] + self.toks[2:5] +
            [ quote_value(self.value) ] + self.toks[6:])


class KeyValueToggle:
    def __init__(self, toks):
        self.toks = toks

    @property
    def key(self):
        k = self.toks[1].split('.')
        if k[-1].startswith('no'):
            return '.'.join(k[:-1] + [ k[-1][2:] ])
        else:
            return '.'.join(k)

    @property
    def value(self):
        k = self.toks[1].split('.')
        if k[-1].startswith('no'):
            return False
        else:
            return True

    def __str__(self):
        return flatten(self.toks)


class JailBlock:
    def __init__(self, toks):
        self.sp_1, self.jail_name, self.sp_2, self.curly_open, \
            self.statements, self.sp_3, self.curly_close = toks
        if not isinstance(self.statements, list):
            self.statements = self.statements.asList()

    @classmethod
    def create(cls, jail_name):
        return cls([ '\n', jail_name, ' ', '{', [], '\n', '}' ])

    @property
    def name(self):
        return self.jail_name

    def set_key(self, name, value):
        if isinstance(value, bool):
            self.toggle_key(name, value)
            return

        self.statements.append(KeyValuePair(
            [ '\n  ', name, '', '=', '', value, '', ';' ]
        ))

    def append_key(self, name, value):
        if isinstance(value, bool):
            self.toggle_key(name, value)
            return

        self.statements.append(KeyValueAppendPair(
            [ '\n  ', name, '', '+=', '', value, '', ';' ]
        ))

    def toggle_key(self, name, value):
        if not value:
            name = name.split('.')
            name = '.'.join(name[:-1] + [ 'no' + name[-1] ])

        self.statements.append(KeyValueToggle([ '\n  ', name, '', ';' ]))

    def get_key(self, name):
        res = []
        for s in self.statements:
            if isinstance(s, KeyValuePair) and s.key == name:
                res = [ s.value ]
            elif isinstance(s, KeyValueAppendPair) and s.key == name:
                if isinstance(s.value, list):
                    res += s.value
                else:
                    res.append(s.value)
            elif isinstance(s, KeyValueToggle) and s.key == name:
                res = [ s.value ]
        if len(res) == 0:
            raise KeyError
        if len(res) == 1:
            return res[0]
        return res

    def has_key(self, name):
        try:
            _ = self.get_key(name)
        except KeyError:
            return False
        return True

    def remove_key(self, name):
        if not self.has_key(name):
            raise KeyError
        self.statements = [ s for s in self.statements \
            if s.__class__ not in [ KeyValuePair, KeyValueAppendPair, KeyValueToggle ] \
            or s.key != name ]

    def __str__(self):
        return flatten([ self.sp_1, self.jail_name, self.sp_2 + self.curly_open, \
            self.statements, self.sp_3, self.curly_close ])


class JailConf:
    def __init__(self, toks):
        self.toks = toks[0]
        if not isinstance(self.toks, list):
            self.toks = self.toks.asList()
        self.trailing_space = toks[1]

    @classmethod
    def create(cls):
        return JailConf([ [], '' ])

    @property
    def statements(self):
        return self.toks

    def get_jail_block(self, x):
        for s in self.statements:
            if isinstance(s, JailBlock):
                if s.name == x:
                    return s
        raise KeyError

    def has_jail_block(self, x):
        try:
            _ = self.get_jail_block(x)
            return True
        except KeyError:
            return False

    def remove_jail_block(self, x):
        if not self.has_jail_block(x):
            raise KeyError
        self.toks = [ t for t in self.toks if not isinstance(t, JailBlock) or t.name != x ]

    def add_statement(self, x):
        self.toks.append(x)

    def __str__(self):
        return flatten([ self.toks, self.trailing_space ])
