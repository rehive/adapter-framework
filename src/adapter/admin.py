from django.contrib import admin

from .models import User, AdminAccount, Transaction


class CustomModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        self.list_display = [field.name for field in model._meta.fields]
        super(CustomModelAdmin, self).__init__(model, admin_site)


class UserAdmin(CustomModelAdmin):
    pass


class AdminAccountAdmin(CustomModelAdmin):
    pass


class TransactionAdmin(CustomModelAdmin):
    pass

admin.site.register(User, UserAdmin)
admin.site.register(AdminAccount, AdminAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
