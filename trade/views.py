from django.shortcuts import render, redirect
from django.views import View
from .models import Trade, Message, TradeItem
from plant.models import UserPlant
from .forms import TradeForm, MessageForm, TradeResponseForm
from django.db.models import Q
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class CreateTrade(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            seller_plant = UserPlant.objects.get(pk=pk)
            seller = seller_plant.user

            if _buyer_is_seller(request.user, seller):
                return redirect('plant:marketplace_plants')

            create_trade_form = TradeForm(
                user=request.user,
                seller_plant=seller_plant
            )
            context = {
                'form': create_trade_form,
                'seller_plant_pk': pk
            }
            return render(request, 'trade/create_trade.html', context)
        else:
            return redirect('user:profile')

    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            form = TradeForm(
                request.POST,
                user=request.user,
                seller_plant=UserPlant.objects.get(pk=pk)
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
            return redirect('trade:create_trade', pk=pk)
        else:
            return redirect('user:profile')


class OrderHistory(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            trades = Trade.objects \
                .filter(Q(seller=request.user) | Q(buyer=request.user))
            for trade in trades:
                _update_unavailable_trades(trade, trade.seller)
            trades_pending = trades.filter(trade_status='SE')
            trades_closed = trades.exclude(trade_status='SE')
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
                seller = Trade.objects.get(pk=pk).seller
                seller_plant = TradeItem.objects.filter(
                    trade__pk=pk,
                    user_plant__user=seller,
                    user_plant__deleted_by_user=False
                )[0]
                buyer_trade_item_list = TradeItem.objects.filter(
                    trade__pk=pk
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
                        # decrement quantity of the seller's user plant
                        seller_plant.user_plant.quantity -= 1
                        seller_plant.user_plant.save()
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
            seller = Trade.objects.get(pk=pk).seller

            _update_unavailable_trades(trade, seller)

            trade_item_list = TradeItem.objects.filter(trade__pk__contains=pk)
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


# helper functions
def _trade_exists(seller, buyer, seller_plant):
    existing_trades = Trade.objects.filter(
        seller=seller,
        buyer=buyer,
    )
    if existing_trades:
        for trade in existing_trades:
            trade_items = trade.get_trade_items.all()
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

    try:
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
    except Exception as e:
        print("ERROR saving trade item: " + str(e))
        new_trade.delete()

    return new_trade.id


def _update_unavailable_trades(trade, seller):
    # if the seller's plant's quantity <= 0, the trade status
    # is set to unavailable
    seller_trade_item = trade.get_trade_items \
        .filter(user_plant__user=seller)[0]
    if not _plant_is_available(seller_trade_item.user_plant):
        trade.trade_status = 'UN'
        trade.save()
    # if the trade status was unavailable, but stock was added, then
    # the trade status changes to sent
    if trade.trade_status == 'UN':
        if _plant_is_available(seller_trade_item.user_plant):
            trade.trade_status = 'SE'
            trade.save()


def _buyer_is_seller(user, seller):
    return user==seller
