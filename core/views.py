from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, View
from .models import Item, OrderItem, Order,BillingAddress
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm


# Create your views here.
def homepage(request):
    items = Item.objects.all()
    context = {'items': items}
    return render(request, 'core/home-page.html', context)


class HomeView(ListView):
    model = Item
    template_name = 'core/home-page.html'
    context_object_name = 'items'
    paginate_by = 10


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {'object': order}
            return render(self.request, 'core/order_summary.html', context)
        except ObjectDoesNotExist:

            messages.error(self.request, 'You do not have an active order')
            return redirect("/")


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        context = {'form': form}
        return render(self.request, 'core/checkout-page.html', context)

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip_code = form.cleaned_data.get('zip_code')
                #same_billing_address = form.cleaned_data.get(
                # 'same_billing_address')
                #save_info = form.cleaned_data.get('save_info')
                #payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip_code=zip_code
                )
                billing_address.save()
                order.billing_address=billing_address
                order.save()
                return redirect('core:checkout-page')
            messages.warning(self.request, 'Failed checkout')
            return redirect('core:checkout-page')

        except ObjectDoesNotExist:
            messages.error(self.request, 'You do not have an active order')
            return redirect("core:order-summary")




def products_page(request):
    context = {}
    return render(request, 'core/product.html', context)


class ItemDetailView(DetailView):
    model = Item
    template_name = 'core/product.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item,
                                                          user=request.user,
                                                          ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'Item quantity was updated')
            return redirect('core:order-summary')
        else:
            messages.info(request, 'Item was added to cart')
            order.items.add(order_item)
            return redirect('core:order-summary')
    else:
        order_date = timezone.now()
        order = Order.objects.create(user=request.user,
                                     ordered_date=order_date)
        order.items.add(order_item)
        messages.info(request, 'Item was added to cart')
        return redirect('core:order-summary')


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            messages.warning(request, 'Item was removed from cart')
            order.items.remove(order_item)

            return redirect('core:order-summary')
        else:
            messages.info(request, 'Item was not in your cart')
            return redirect('core:products-page', slug=slug)
    else:
        # add msg that user doesent have order
        messages.info(request, 'You do not have an active order')
        return redirect('core:products-page', slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.warning(request, 'Item quantity was updated')

            return redirect('core:order-summary')
        else:
            messages.info(request, 'Item was not in your cart')
            return redirect('core:products-page', slug=slug)
    else:
        # add msg that user doesent have order
        messages.info(request, 'You do not have an active order')
        return redirect('core:products-page', slug=slug)
