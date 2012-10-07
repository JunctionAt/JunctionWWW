from flask.ext.principal import Permission, RoleNeed

# Only put Permission type instantiations here

edit_roles_permission = Permission(RoleNeed('edit_roles'))
show_logs_permission = Permission(RoleNeed('show_logs'))
