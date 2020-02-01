from .title import Title


class DebugItem:
    def __init__(self, class_ref, group_name = None):
        self.class_ref = class_ref
        self.group_name = group_name
        self.debug = False

    def debug_enable(self, batch, group = None):
        self.debug = True
        self.class_ref.debug_enable(batch, group)

    def debug_disable(self):
        self.debug = False
        self.class_ref.debug_disable()


class Debug:
    def __init__(self, batch, group=None):
        self._enabled_items = []
        self._groups = {}
        self._dynamic_variables = {}
        self._titles = {}
        self._show_dynamic_variables = False

        self._batch = batch
        self._group = group

    def update(self):
        """update dynamic variable values"""
        if self._show_dynamic_variables:
            if len(self._titles) > 0:
                for name in self._titles.keys():
                    # value can be list of variables added together, or just one
                    if type(self._dynamic_variables) == list:
                        val = 0

                        for item in self._dynamic_variables:
                            val += item()

                        self._titles[name].update_text("{}: {}".format(name, val))
                    else:
                        self._titles[name].update_text("{}: {}".format(name, self._dynamic_variables[name]()))
        else:
            if len(self._titles) > 0:
                for name in self._titles.keys():
                    self._titles[name].update_text("")

    def enable(self, item):
        """enable debug for a single item"""
        if type(item) != DebugItem:
            item = DebugItem(item)

        if item not in self._enabled_items:
            self._enabled_items.append(item)
            item.debug_enable(self._batch, self._group)

    def disable(self, item):
        """disable debug for a single item, if it is already enabled"""
        if item in self._enabled_items:
            item.debug_disable()
            self._enabled_items.remove(item)

    def toggle(self, item):
        """toggle debug for a single item"""
        if not item.debug:
            self.enable(item)
        else:
            self.disable(item)

    def add_group(self, group, name):
        """add a group of items that can all be enabled / disabled together"""
        if name not in self._groups.keys():
            if type(group) == list:
                new_group = []
                for item in group:
                    new_group.append(DebugItem(item, group_name = name))
                self._groups[name] = new_group
            else:
                group = DebugItem(group, group_name=name)
                self._groups[name] = group
        else:
            raise ValueError("Group {} already exists!".format(name))

    def enable_group(self, group_name):
        """enable debug for all items in specified group"""
        if group_name not in self._groups.keys():
            raise ValueError("Group {} does not exist!".format(group_name))
        else:
            group = self._groups[group_name]

            # if group is not a list
            if type(group) != list:
                self.enable(group)
            else:
                for item in group:
                    self.enable(item)

    def disable_group(self, group_name):
        """disable debug for all items in specified group"""
        if group_name not in self._groups.keys():
            raise ValueError("Group {} does not exist!".format(group_name))
        else:
            group = self._groups[group_name]

            # if group is not a list
            if type(group) != list:
                self.disable(group)
            else:
                for item in group:
                    self.disable(item)

    def toggle_group(self, group_name):
        """toggle debug for all items in specified group"""
        if group_name not in self._groups.keys():
            raise ValueError("Group {} does not exist!".format(group_name))
        else:
            group = self._groups[group_name]

            # if group is not a list
            if type(group) != list:
                self.toggle(group)
            else:
                for item in group:
                    self.toggle(item)

    def delete_group(self, group_name):
        """delete a group from list of groups, disable debug as well"""
        if group_name not in self._groups.keys():
            raise ValueError("Group {} does not exist!".format(group_name))
        else:
            self.disable_group(group_name)
            self._groups.pop(group_name)

    def enable_all(self):
        """enable debug for every group"""
        self.enable_dynamic_variables()

        if len(self._groups) == 0:
            raise ValueError("No groups to enable!")
        else:
            for group_name in self._groups.keys():
                self.enable_group(group_name)

    def disable_all(self):
        """disable debug for every item"""
        self.disable_dynamic_variables()

        if len(self._enabled_items) == 0:
            raise ValueError("No items to disable!")
        else:
            for group_name in self._groups.keys():
                self.disable_group(group_name)

            # leftover items that aren't in groups
            for item in self._enabled_items:
                self.disable(item)

    def toggle_all(self):
        """toggle debug for every item in a group"""
        self.toggle_dynamic_variables()

        for group_name in self._groups.keys():
            self.toggle_group(group_name)

    def delete_all(self):
        """delete all groups"""
        for group_name in self._groups.keys():
            self.delete_group(group_name)

    def dynamic_variable(self, name, getter_func, pos, size=30, anchor_x='center', anchor_y='center'):
        """create a text display for a changing variable, or list of variables to add together"""
        self._dynamic_variables[name] = getter_func
        self._titles[name] = Title("", pos, size=size, batch=self._batch, group=self._group,
                                   anchor_x=anchor_x, anchor_y=anchor_y)

    def enable_dynamic_variables(self):
        self._show_dynamic_variables = True

    def disable_dynamic_variables(self):
        self._show_dynamic_variables = False

    def toggle_dynamic_variables(self):
        if self._show_dynamic_variables:
            self._show_dynamic_variables = False
        else:
            self._show_dynamic_variables = True
