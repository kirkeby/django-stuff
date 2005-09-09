from django.middleware import admin

class AdminUserRequired(admin.AdminUserRequired):
    """Admin middleware. If a view-function has the admin_required
    property, access will be granted only to valid users with the
    "is_staff" flag set."""

    def process_view(self, request, view_func, param_dict):
        """Make sure the user is logged in and is a valid admin user
        before allowing any access to views with the admin_required
        property."""

        if getattr(view_func, 'admin_required', 0):
            return admin.AdminUserRequired.process_view(self, request, view_func, param_dict)

