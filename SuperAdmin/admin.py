from django.contrib import admin
from SuperAdmin.models import Feedback, MenuItem, PasswordReset

admin.site.register(PasswordReset)
admin.site.register(Feedback)
admin.site.register(MenuItem)