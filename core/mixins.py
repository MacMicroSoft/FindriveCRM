from django.contrib.auth.mixins import AccessMixin


class RoleRequiredMixin(AccessMixin):
    required_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        user_role = getattr(request.user, "role", None)

        if user_role not in self.required_roles:
            return self.handle_no_permission()

        return super().dispatch(request, *args, **kwargs)
