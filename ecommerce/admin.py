from django.contrib import admin, messages
from django.contrib.admin import DateFieldListFilter
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django import forms
from ecommerce.models import Customer, Order, Product, OrderItem, Address

# --------- Custom Forms

class OrderInlineForm(forms.ModelForm):
    cancel_order = forms.BooleanField(required=False, label="Cancel Order")

    class Meta:
        model = Order
        fields = '__all__'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('cancel_order'):
            if instance.order_status == "active":
                instance.order_status = "canceled"
                if self.request:
                    messages.success(self.request, f'Order #{instance.id} has been canceled.')
            elif instance.order_status == "completed":
                if self.request:
                    messages.warning(self.request, f'Order #{instance.id} is already completed and cannot be canceled.')
            else:
                if self.request:
                    messages.info(self.request, f'Order #{instance.id} has been already canceled.')
        
        if commit:
            instance.save()
        return instance
    

class DisabledCheckboxForm(forms.ModelForm):
    disabled = forms.BooleanField(required=False, label="Diable Address")

    class Meta:
        model = Address
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('disabled'):
            if not instance.disabled_on:
                instance.disabled_on = timezone.now()
        else:
            instance.disabled_on = None
        
        if commit:
            instance.save()
        return instance


# ---------- Inlines

class OrderInline(admin.TabularInline):
    model = Order
    form = OrderInlineForm
    fields = ("view_order_link", "address", 'order_status', "total_amount", "created_on", "cancel_order")
    readonly_fields = ("view_order_link", "total_amount", "created_on",)
    extra = 0

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        formset.form.request = request
        return formset

    def view_order_link(self, obj):
        if obj.id:
            url = reverse('admin:ecommerce_order_change', args=[obj.id])
            return format_html('<a href="{}">View Order #{}</a>', url, obj.id)
        return "-"



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("view_orderitem_link", "product", "quantity", "total_item_price")
    readonly_fields = ("view_orderitem_link", "total_item_price",)
    extra = 0

    def view_orderitem_link(self, obj):
        if obj.id:
            url = reverse('admin:ecommerce_orderitem_change', args=[obj.id])
            return format_html('<a href="{}">View Order Item #{}</a>', url, obj.id)
        return "-"


class AddressInline(admin.TabularInline):
    model = Address
    form = DisabledCheckboxForm
    fields = ("view_address_link", "name", "phone", "address_line_1", "address_line_2", "landmark", "pincode", "disabled")
    readonly_fields = ("view_address_link",)
    extra = 0

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.filter(disabled_on__isnull=True)

    def view_address_link(self, obj):
        if obj.id:
            url = reverse('admin:ecommerce_address_change', args=[obj.id])
            return format_html('<a href="{}">View Address #{}</a>', url, obj.id)
        return "-"


# ---------- Admin Models

@admin.register(Customer)
class Customer(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'mobile', 'email', 'created_on', 'updated_on')
    search_fields = ('first_name', 'last_name', 'mobile', 'email')
    readonly_fields = ('created_on', 'updated_on')
    list_filter = (("created_on", DateFieldListFilter),)
    inlines = [OrderInline, AddressInline]

    fieldsets = (
        ( ('Name Details'), {
            'fields': ('first_name', 'last_name'),
            'classes': ('form-row',),
        }),
        ( ('Contact Details'), {
            'fields': ('mobile', 'email'),
            'classes': ('form-row',),
        }),
        ( ('Metadata'), {
            'fields': ('created_on', 'updated_on'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Order)
class Order(admin.ModelAdmin):
    list_display = ('id', 'customer', 'address', 'total_amount', 'order_status', 'created_on')
    search_fields = ('customer__first_name', 'customer__last_name', 'address__pincode')
    readonly_fields = ('total_amount', 'created_on')
    list_filter = (("created_on", DateFieldListFilter),)
    inlines = [OrderItemInline]

    actions = ['cancel_order']

    def cancel_order(self, request, queryset):
        print(queryset)
        for order in queryset:
            if order.order_status == "active":
                order.order_status = "canceled"
                order.save()
                self.message_user(request, f'Order #{order.id} has been canceled.', level=messages.SUCCESS)
            elif order.order_status == "completed":
                self.message_user(request, f'Order #{order.id} is already completed and cannot be canceled.', level=messages.WARNING)
            else:
                self.message_user(request, f'Order #{order.id} has been already canceled.', level=messages.INFO)
    
    cancel_order.short_description = "Cancel selected orders"


@admin.register(Product)
class Product(admin.ModelAdmin):
    list_display = ('id', 'name', 'price')
    search_fields = ('name',)


@admin.register(OrderItem)
class OrderItem(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'total_item_price', 'created_on')
    list_filter = ('created_on',)
    readonly_fields = ('created_on', 'total_item_price')


@admin.register(Address)
class Address(admin.ModelAdmin):
    list_display = ('id', 'customer', 'name', 'phone', 'address_line_1', 'pincode', 'disabled_on')
    readonly_fields = ("disabled_on",)

