from django.shortcuts import render, redirect
from django.views import View
from .models import Trade, Message, TradeItem
from order.models import Address
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
                seller_plant=seller_plant,
                is_for_shipping=seller_plant.is_for_shipping,
                is_for_pickup=seller_plant.is_for_pickup
            )
            context = {
                'form': create_trade_form,
                'seller_plant_pk': pk
            }
            return render(request, 'trade/create_trade.html', context=context)
        else:
            return redirect('user:profile')

    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            seller_plant = UserPlant.objects.get(pk=pk)
            seller = seller_plant.user
            form = TradeForm(
                request.POST,
                user=request.user,
                seller_plant=seller_plant,
                is_for_shipping=seller_plant.is_for_shipping,
                is_for_pickup=seller_plant.is_for_pickup
            )
            if form.is_valid():
                if 'handling_methods' in form.cleaned_data.keys():
                    handling_methods = form.cleaned_data['handling_methods']
                else:
                    handling_methods = ['shipping'] if \
                        seller_plant.is_for_shipping else ['pickup']
                new_trade_attributes = {
                    'seller_plant': form.cleaned_data['seller_plant'],
                    'seller': seller,
                    'buyer': request.user,
                    'buyer_plants': form.cleaned_data['user_plants_for_trade'],
                    'handling_methods': handling_methods
                }
                # try:
                existing_trade_id = _trade_exists(new_trade_attributes)
                if existing_trade_id is not None:
                    return redirect('trade:trade', pk=existing_trade_id)
                if _plant_is_available(seller_plant):
                    trade_id = _create_new_trade_and_items(
                        new_trade_attributes)
                    if trade_id is None:
                        return redirect('plant:marketplace_plants')
                    else:
                        return redirect('trade:trade', pk=trade_id)
                else:
                    # nice to have: plant no longer available message
                    return redirect('plant:marketplace_plants')
                # except Exception as e:
                print("ERROR saving trade: " + str(e))
            else:
                print(form.errors)  # debug errors
                return redirect('trade:create_trade_new', pk=pk)
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
                    items=buyer_trade_item_list,
                    is_offered_for_shipping=trade.is_offered_for_shipping,
                    is_offered_for_pickup=trade.is_offered_for_pickup
                )
                print(request.POST)
                if form.is_valid():
                    # parse response
                    parsed_trade_response_tokens = request.POST.\
                        get('trade_response').split()
                    trade.trade_status = (
                        parsed_trade_response_tokens[0]
                    )
                    if trade.trade_status == 'AC':
                        # update the accepted_handling_method
                        trade.accepted_handling_method = \
                            request.POST.get('handling_methods')
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
                items=buyer_trade_item_list,
                is_offered_for_shipping=trade.is_offered_for_shipping,
                is_offered_for_pickup=trade.is_offered_for_pickup
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
def _trade_exists(new_trade_attr_dict):
    existing_trades = Trade.objects.filter(
        seller=new_trade_attr_dict["seller"],
        buyer=new_trade_attr_dict["buyer"],
    )
    if existing_trades:
        for trade in existing_trades:
            trade_items = trade.get_trade_items.all()
            for item in trade_items:
                if item.user_plant == new_trade_attr_dict["seller_plant"]:
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


def _create_new_trade_and_items(new_trade_attr_dict):
    buyer = new_trade_attr_dict['buyer']
    seller = new_trade_attr_dict['seller']
    seller_plant = new_trade_attr_dict['seller_plant']
    buyer_plants = new_trade_attr_dict['buyer_plants']
    handling_methods = new_trade_attr_dict['handling_methods']
    is_offered_for_shipping = True if 'shipping_choice' in \
                                      handling_methods else False
    is_offered_for_pickup = True if 'pickup_choice' in \
                                    handling_methods else False
    if seller_plant.is_for_pickup and seller_plant.is_for_shipping:
        accepted_handling_method = 'UN'
    # seller only offered a pickup trade
    elif seller_plant.is_for_pickup:
        accepted_handling_method = 'PI'
        is_offered_for_pickup = True
    # seller only offered a ship trade
    elif seller_plant.is_for_shipping:
        accepted_handling_method = 'SH'
        is_offered_for_shipping = True
    # seller didn't specify, buyer can offer shipping and/or pickup
    else:
        accepted_handling_method = 'UN'

    # add buyer plants if still available
    buyer_plants = _trade_plants_are_available(seller_plant, buyer_plants)
    if not buyer_plants:
        return None
    new_trade = Trade(
        buyer=buyer,
        seller=seller,
        trade_status='SE',
        accepted_handling_method=accepted_handling_method,
        is_offered_for_shipping=is_offered_for_shipping,
        is_offered_for_pickup=is_offered_for_pickup
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
    # if the seller's plant's quantity <= 0, and trade status was 'SE',
    # the trade status is set to unavailable
    seller_trade_item = trade.get_trade_items \
        .filter(user_plant__user=seller)[0]
    if not _plant_is_available(seller_trade_item.user_plant):
        if trade.trade_status == 'SE':
            trade.trade_status = 'UN'
            trade.save()
    # if the trade status was unavailable, but stock was added, then
    # the trade status changes to sent
    if trade.trade_status == 'UN':
        if _plant_is_available(seller_trade_item.user_plant):
            trade.trade_status = 'SE'
            trade.save()


def _buyer_is_seller(user, seller):
    return user == seller
