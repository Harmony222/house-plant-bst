from django.shortcuts import render, redirect
from django.views import View
from .models import Trade, Message, TradeItem
from plant.models import UserPlant
from .forms import TradeForm, MessageForm, TradeResponseForm
from django.db.models import Q
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


def _trade_exists(seller, buyer, seller_plant):
    existing_trades = Trade.objects.filter(
        seller=seller,
        buyer=buyer,
    )
    if existing_trades:
        for trade in existing_trades:
            trade_items = trade.get_trade_items
            for item in trade_items:
                if item.user_plant == seller_plant:
                    return trade.id
    return None


def _plant_is_available(user_plant_obj):
    return user_plant_obj.quantity > 0


def _trade_plants_are_available(seller_plant, buyer_plants):
    # check that the seller and buyer plants are available
    if not _plant_is_available(seller_plant):
        return None
    buyer_plants_list = []
    for buyer_plant in buyer_plants:
        if _plant_is_available(buyer_plant):
            buyer_plants_list.append(buyer_plant)
    if not buyer_plants:
        return None
    return buyer_plants_list


def _create_new_trade_and_items(seller, buyer, seller_plant, buyer_plants):
    buyer_plants = _trade_plants_are_available(seller_plant, buyer_plants)
    if not buyer_plants:
        return None
    new_trade = Trade(
        buyer=buyer,
        seller=seller,
        trade_status='SE'
    )
    new_trade.save()

    seller_trade_item = TradeItem(
        trade=new_trade,
        user_plant=seller_plant,
        quantity=1
    )
    seller_trade_item.save()

    for buyer_plant in buyer_plants:
        buyer_trade_item = TradeItem(
            trade=new_trade,
            user_plant=buyer_plant,
            quantity=1
        )
        buyer_trade_item.save()

    return new_trade.id


class CreateTrade(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            create_trade_form = TradeForm(
                user=request.user,
                seller_plant=UserPlant.objects.get(pk=3)
            )
            context = {'form': create_trade_form}
            return render(request, 'trade/create_trade.html', context)
        else:
            return redirect('user:profile')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = TradeForm(
                request.POST,
                user=request.user,
                seller_plant=UserPlant.objects.get(pk=3)
            )
            if form.is_valid():
                seller_plant = form.cleaned_data['seller_plant']
                seller = seller_plant.user
                buyer = request.user
                try:
                    existing_trade_id = _trade_exists(seller, buyer,
                                                      seller_plant)
                    if existing_trade_id is not None:
                        return redirect('trade:trade',
                                        pk=existing_trade_id)

                    trade_id = _create_new_trade_and_items(
                        seller,
                        buyer,
                        seller_plant,
                        form.cleaned_data['user_plants_for_trade']
                    )
                    if trade_id is None:
                        return redirect('plant:marketplace_plants')
                    else:
                        return redirect('trade:trade', pk=trade_id)
                except Exception as e:
                    print("ERROR saving trade: " + str(e))
            return redirect('trade:create_trade')
        else:
            return redirect('user:profile')


class OrderHistory(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            trades_pending = Trade.objects \
                .filter(trade_status='SE') \
                .filter(Q(seller=request.user) | Q(buyer=request.user))
            trades_closed = Trade.objects \
                .exclude(trade_status='SE') \
                .filter(Q(seller=request.user) | Q(buyer=request.user))
            context = {
                'trades_pending': trades_pending,
                'trades_closed': trades_closed
            }
            return render(request, 'trade/order_history.html', context)
        else:
            return redirect('user:profile')


class TradeResponse(View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            trade = Trade.objects.get(pk=pk)
            if trade.seller == request.user:
                print(request.POST)
                seller = Trade.objects.get(pk=pk).seller
                buyer_trade_item_list = TradeItem.objects.filter(
                    trade__pk__contains=pk
                ).exclude(
                    user_plant__user=seller
                )
                form = TradeResponseForm(
                    request.POST,
                    items=buyer_trade_item_list
                )
                if form.is_valid():
                    # parse response
                    parsed_trade_response_tokens = request.POST.\
                        get('trade_response').split()
                    trade.trade_status = (
                        parsed_trade_response_tokens[0]
                    )
                    if trade.trade_status=='AC':
                        # decrement quantity of chosen trade item
                        chosen_trade_item_id = parsed_trade_response_tokens[1]
                        chosen_trade_item = TradeItem.objects\
                            .get(pk=chosen_trade_item_id)
                        chosen_trade_item.chosen_flag = True
                        chosen_trade_item.save()
                        chosen_user_plant = chosen_trade_item.user_plant
                        chosen_user_plant.quantity -= 1
                        chosen_user_plant.save()
                    trade.response_date = datetime.now()
                    trade.save()
            return redirect('trade:trade', pk=trade.pk)
        else:
            return redirect('user:profile')


class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            trade = Trade.objects.get(pk=pk)
            if trade.seller == request.user:
                recipient = trade.buyer
            else:
                recipient = trade.seller
            form = MessageForm(request.POST)
            if form.is_valid():
                message = Message(
                    sender=request.user,
                    recipient=recipient,
                    trade=trade,
                    message=request.POST.get('message'),
                )
                message.save()
            return redirect('trade:trade', pk=pk)
        else:
            return redirect('user:profile')


class TradeView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            message_form = MessageForm()
            trade = Trade.objects.get(pk=pk)
            trade_item_list = TradeItem.objects.filter(trade__pk__contains=pk)
            seller = Trade.objects.get(pk=pk).seller
            buyer_trade_item_list = trade_item_list.exclude(
                user_plant__user=seller
            )
            message_list = Message.objects.filter(trade__pk__contains=pk)
            trade_response_form = TradeResponseForm(
                items=buyer_trade_item_list
            )
            context = {
                'trade': trade,
                'message_form': message_form,
                'trade_response_form': trade_response_form,
                'trade_item_list': trade_item_list,
                'message_list': message_list
            }
            return render(request, 'trade/trade.html', context)
        else:
            return redirect('user:profile')
