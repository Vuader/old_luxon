from luxon.utils.html import Menu
from luxon import g

class UIMenu(object):
    """Class UIMenu.

    Used to generate Menu objects to add items
    for a Tachyonic Menu.
    """
    def __init__(self):
        self._items = []

    def add(self, path_name, href='#', view=None, **kwargs):
        self._items.append((path_name, view, href, kwargs))

    def render(self, css_menu='menu menu-horizontal menu-top-theme'):
        req = g.current_request
        root_menu = Menu(css_menu)

        def render_item(menu, path_name, href, **kwargs):
            if len(path_name) == 1:
                # FORMAT URL to be under application.
                if href != '#' and ':' not in href:
                    href = "%s/%s" % (req.app, href.strip('/'))
                # Render link.
                menu.link(path_name[0], href=href, **kwargs)
            elif len(path_name) > 1:
                # Get Submenu.
                submenu = menu.submenu(path_name[0])
                # Render for Submenu.
                render_item(submenu, path_name[1:], href, **kwargs)

        has_policy_engine = hasattr(req, 'policy')
        # Run through items.
        for item in self._items:
            path_name, view, href, kwargs = item
            if (view is None or (has_policy_engine and
                                 req.policy.validate(view))):
                path_name = path_name.strip('/').split('/')
                render_item(root_menu, path_name, href, **kwargs)
        return str(root_menu)

    def __len__(self):
        return len(self._itmes)

    def hasitems(self):
        if len(self._items) > 0:
            return True
        else:
            return False
