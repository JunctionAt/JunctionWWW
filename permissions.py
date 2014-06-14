# NONE OF THESE ARE ACTUALLY PULLED FROM HERE YET, DO NOT CHANGE

avatar_reset = 'avatar.reset'


class PermissionHolderMixin(object):
    """
    This mixin should be inherited by objects that holds permissions.
    """

    def get_permissions(self):
        """
        This method is the only one that needs to be implemented by permission holders. Values are not cached, this
        needs to be managed by the implementation.
        :return: A list of permissions the holder has access to.
        """
        raise NotImplementedError("Classes using PermissionHolderMixin should implement get_permissions(self)")

    def has_permission(self, permission):
        """
        Check if the holder has access to the supplied permission. Gets permissions by calling self.get_permissions().
        :param permission:
        :return: True if the holder has access to the permission, false if not.
        """
        node = unicode(permission)
        permissions = self.get_permissions()

        # Start off by checking for negative permissions.
        for permission in permissions:
            if permission.startswith(u"-"):
                if permission.endswith(u"*"):
                    if node.startswith(permission[1:-1]):
                        return False
                else:
                    if permission[1:] == node:
                        return False

        # Then check positive permissions.
        for permission in permissions:
            if permission.endswith(u"*"):
                if node.startswith(permission[:-1]):
                    return True
            else:
                if permission == node:
                    return True

        # We didn't find the role.
        return False

    def can(self, alias):
        """
        This method will look up the supplied alias in 'permissions.role_bindings' and make sure the holder has all the
        permissions in it.
        :param alias: The alias to look up.
        :return: True if the holder has all permissions in the alias, false if not.
        """
        roles = role_bindings[alias]
        for role in roles:
            if not self.has_permission(role):
                return False
        return True


# Not sure if this is a good idea, I am welcome to input.
# The idea is that instead of checking for permission nodes everywhere in the code (quickly turns into a mess, we need
# to look around the code to check what permission nodes to use where), we define all nodes in this file. Instead of
# giving templates access to this file directly, they can use aliases (binds a role -> an action that the ui needs to
# do). Instead of doing {% if current_user.has_permission('alt.view') %}, we can now do
# {% if current_user.can("show alts"). As I said previously, I am not sure if this makes sense to do, but I will try
# it out.
class RoleBindingManager(dict):
    def add(self, alias, roles):
        self[alias] = roles

role_bindings = RoleBindingManager()

# Alts
role_bindings.add("view alts", ['alt.view'])
role_bindings.add("graph alts", ['alt.view'])

# Bans and Appeals
role_bindings.add("manage ban appeals", ['ban.appeal.manage'])
role_bindings.add("edit appeal replies", ['ban.appeal.manage.edit_reply'])
role_bindings.add("watch appeals", ['ban.appeal.watch'])
role_bindings.add("edit ban reasons", ['ban.edit'])