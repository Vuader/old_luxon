# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
from luxon.structs.htmldoc import HTMLDoc
from luxon.structs.models.fields import String
from luxon.structs.models.fields import Boolean
from luxon.structs.models.fields import DateTime
from luxon.structs.models.fields import Enum
from luxon.utils.timezone import format_datetime

def select(name, options, selected, empty=False, cls=None, onchange=None,
           disabled=False, readonly=False):
    html = HTMLDoc()

    if disabled or readonly:
        input = html.create_element('input')
        input.set_attribute('type', 'text')
        input.set_attribute('id', name)
        input.set_attribute('name', name)
        input.set_attribute('disabled')
        input.set_attribute('value', selected)
        input.set_attribute('class', 'form-control')
        return input

    select = html.create_element('select')
    select.set_attribute('name', name)
    select.set_attribute('id', name)

    if onchange is not None:
        select.set_attribute('onchange', onchange)

    if cls is not None:
        select.set_attribute('class', cls)

    if empty is True:
        option = select.create_element('option')
        option.set_attribute('value', '')
        option.append('')

    if options is not None:
        for opt in options:
            if isinstance(options, (list, tuple,)):
                if isinstance(opt, (list, tuple,)):
                    try:
                        option = select.create_element('option')
                        option.set_attribute('value', opt[0])
                        option.append(opt[1])
                        if opt[1] == selected:
                            option.set_attribute('selected')
                    except IndexError:
                        raise ValueError('Malformed values for HTML select')
                else:
                    if opt is not None:
                        option = select.create_element('option')
                        option.set_attribute('value', opt)
                        if opt == selected:
                            option.set_attribute('selected')
                        option.append(opt)
            elif isinstance(options, dict):
                    option = select.create_element('option')
                    option.set_attribute('value', opt)
                    if opt == selected:
                        option.set_attribute('selected')
                    option.append(options[opt])
    return html

class Menu(object):
    """CSS HTML Menu.

    This class is used to define and generate a simple menu driven by css.

    Requires following css are bare minimum.

    .menu {
        white-space: nowrap;
        padding: 0;
        margin: 0;
    }

    ol.menu, .menu ol {
        list-style: none;
    }

    .menu li, .menu ol, .menu a {
        position: relative;
        padding: 0;
        margin: 0;
    }

    .menu li ol {
        display: none;
        z-index: 1000000;
    }

    .menu li:hover > ol {
        display: block;
    }

    .menu-horizontal {
        float: left;
        width: 100%;
    }

    .menu-horizontal li {
        float: left;
        position: relative;
    }

    .menu-horizontal li a {
        display: block;
    }

    .menu-horizontal ol ol {
        left: 100%;
        top: 0;
    }

    .menu-horizontal li:hover > ol {
        position: absolute;
    }

    .menu-horizontal li:hover li { float: none; }

    ol.menu-vertical, .menu-vertical ol {
        width: 150px;
    }

    .menu-vertical a {
        display: block;
        width: 100%;
        overflow: hidden;
    }

    .menu-vertical li {
        width: 175px;
    }

    .menu-vertical a {
        width: 150px;
    }

    .menu-vertical li:hover > ol {
        position: absolute;
        top: 0;
        left: 175px;
    }

    ol.menu-theme, .menu-theme li {
      background: #000000;
      font-size: 14px;
    }

    .menu-theme li a {
        font-family: helvetica, arial, sans-serif;
        text-decoration: none;
        color: #9d9d9d;
        font-size: 14px;
        padding-top: 15px;
        padding-bottom: 15px;
        padding-left: 10px;
        padding-right: 15px;
    }

    .menu-theme li:hover > a {
        color:#000000;
        background: #cccccc;
    }

    However css needed is already included in Photonic by default.

    Returns html menu.
    """
    def __init__(self, css_menu='menu menu-vertical menu-theme'):
        self._html_object = HTMLDoc()
        self._ol = self._html_object.create_element('ol')
        if css_menu is not None:
            self._ol.set_attribute('class', css_menu)

        self.submenus = {}

    def submenu(self, name, image=None):
        """Create new submenu item.

        Add submenu on menu and returns submenu for adding more items.

        Args:
            name (str): Name of submenu item.

        Returns meny object.
        """
        # Create new menu for submenu.
        if name in self.submenus:
            return self.submenus[name]
        else:
            submenu = self.__class__(css_menu=None)
            # Add Submenu to submenu cache.
            self.submenus[name] = submenu

            li = self._ol.create_element('li')
            a = li.create_element('a')
            a.set_attribute('href','#')
            if image is not None:
                img = a.create_element('img')
                img.set_attribute('alt', name)
                img.set_attribute('title', name)
                img.set_attribute('src', image)
            else:
                a.append(name)
                span = a.create_element('span')
                span.set_attribute('class', 'caret')
            li.append(submenu._html_object)

            return submenu

    def link(self, name, href='#', image=None, **kwargs):
        """Add submenu item.

        Args:
            name (str): Menu item name.
            href (str): Url for link. (default '#')

        Kwargs:
            Kwargs are used to additional flexibility.
            Kwarg key and values are used for properties of <a> attribute.
        """
        li = self._ol.create_element('li')
        a = li.create_element('a')
        a.set_attribute('href', href)
        for kwarg in kwargs:
            a.set_attribute(kwarg, **kwargs)
        if image is not None:
            img = a.create_element('img')
            img.set_attribute('alt', name)
            img.set_attribute('title', name)
            img.set_attribute('src', image)
        else:
            a.append(name)

    def __str__(self):
        return str(self._html_object)

def datatable(id, columns):
    """Under construction datatables"""
    raise NotImplementedError('Not Completed')

    html = HTMLDoc()
    table = html.create_element('table')
    thead = table.create_element('thead')
    for column in columns:
        tr = thead.create_element('tr')
        th = tr.create_element('th')
        th.append(column.title())

    tfoot = table.create_element('tfoot')
    for column in columns:
        tr = tfoot.create_element('tr')
        th = tr.create_element('th')
        th.append(column.title())

    tbody = table.create_element('tbody')
    tbody.set_attribute('id', id)
    script = html.create_element('script')

def form(model, values=None, readonly=False):
    html = HTMLDoc()
    fields = model.fields
    if values is None and not isinstance(model, type):
        values = model.dict
    elif values is None:
        values = {}

    for field in fields:
        obj = fields[field]
        if obj.hidden is False and obj.internal is False:
            value = values.get(field)
            if value is None:
                value = obj.default

            if hasattr(value, '__call__'):
                value = value()

            form_group = html.create_element('div')
            form_group.set_attribute('class', 'form-group')
            label = form_group.create_element('label')
            label.set_attribute('class', 'control-label col-sm-2')
            label.set_attribute('for', 'field')
            if obj.label is not None:
                label.append(obj.label)
            else:
                label.append(field)
            div = form_group.create_element('div')
            div.set_attribute('class', 'col-sm-10')

            if obj.readonly is True:
                readonly = True
            else:
                readonly = False

            if isinstance(obj, Enum):
                div.append(select(field, obj.enum, value, cls="select",
                                  readonly=readonly))
            elif isinstance(obj, DateTime):
                if value is not None:
                    value = format_datetime(value)
                input = div.create_element('input')
                input.set_attribute('type', 'text')
                input.set_attribute('class', 'form-control')
                input.set_attribute('id', field)
                input.set_attribute('name', field)
                if readonly is True:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.placeholder is not None:
                    input.set_attribute('placeholder', obj.placeholder)
                if value is not None:
                    input.set_attribute('value', value)
                if obj.readonly:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.null is False:
                    input.set_attribute('required')
                if obj.placeholder:
                    input.set_attribute('placeholder', obj.placeholder)
            elif isinstance(obj, Boolean):
                input = div.create_element('input')
                input.set_attribute('type', 'checkbox')
                input.set_attribute('id', field)
                input.set_attribute('name', field)
                if readonly is True:
                    input.set_attribute('disabled')
                if value is True:
                    input.set_attribute('checked')
                input.set_attribute('value', 'true')

            elif isinstance(obj, String):
                input = div.create_element('input')
                input.set_attribute('type', 'text')
                input.set_attribute('class', 'form-control')
                input.set_attribute('id', field)
                input.set_attribute('name', field)
                if readonly is True:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.placeholder is not None:
                    input.set_attribute('placeholder', obj.placeholder)
                if value is not None:
                    input.set_attribute('value', value)
                if obj.readonly:
                    input.set_attribute('readonly')
                    input.set_attribute('disabled')
                if obj.null is False:
                    input.set_attribute('required')
                if obj.placeholder:
                    input.set_attribute('placeholder', obj.placeholder)
            else:
                pass

    return html
