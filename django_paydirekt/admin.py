from django.contrib import admin

from .models import PaydirektCheckout


class PaydirektCheckoutAdmin(admin.ModelAdmin):
    list_display = ('checkout_id', 'status')
    list_filter = ('status',)
    ordering = ('-created_at',)
    fields = ('checkout_id', 'status')

admin.site.register(PaydirektCheckout, PaydirektCheckoutAdmin)
