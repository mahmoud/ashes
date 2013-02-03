from __future__ import unicode_literals

from ashes import AshesEnv, Template
from tests import dust_site_tests
from tests.core import OPS

DEFAULT_WIDTH = 70


def get_line(title, items, twidth=20, talign='>', width=DEFAULT_WIDTH):
    if len(title) > twidth:
        title = title[:twidth - 3] + '...'
    rwidth = width - twidth
    items = items or []
    pw = rwidth / len(items)
    tmpl = '{title:{talign}{twidth}}' + ('{:^{pw}}' * len(items))
    return tmpl.format(title=title,
                       talign=talign,
                       twidth=twidth,
                       pw=pw,
                       *items)


def get_grid(width=DEFAULT_WIDTH):
    lines = ['']
    col_names = [dt.op_name for dt in OPS]
    headings = get_line('Dust.js site refs', col_names, talign='^')
    lines.append(headings)
    rstripped_width = len(headings.rstrip())
    lines.append('-' * (rstripped_width + 1))

    env = AshesEnv()
    for tc in dust_site_tests:
        env.register(Template(tc.name, tc.template, env=env, lazy=True))

    for tc in dust_site_tests:
        tres = tc.get_test_result(env)
        lines.append(get_line(tres.name, tres.get_symbols()))
    return '\n'.join(lines + [''])


def main(width=DEFAULT_WIDTH):
    print get_grid()


if __name__ == '__main__':
    main()
