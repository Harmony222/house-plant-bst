from django.shortcuts import render, redirect
from django.views import View
from .models import Trade, Message, TradeItem
from .forms import TradeForm, MessageForm, TradeResponseForm
from django.db.models import Q
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()


class CreateTrade(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = TradeForm()
            context = {'form': form}
            return render(request, 'trade/create_trade.html', context)
        else:
            return redirect('user:profile')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = TradeForm(request.POST)
            username = request.POST.get('username')
            try:
                recipient = User.objects.get(username=username)
                print(f'create_trade_recipient: {recipient.username}')
                if Trade.objects.filter(seller=request.user,
                                        buyer=recipient).exists():
                    trade = Trade.objects.filter(seller=request.user,
                                                 buyer=recipient)[0]
                    return redirect('trade:trade', pk=trade.pk)
                elif Trade.objects.filter(seller=recipient,
                                          buyer=request.user).exists():
                    trade = Trade.objects.filter(seller=recipient,
                                                 buyer=request.user)[0]
                    return redirect('trade:trade', pk=trade.pk)
                if form.is_valid():
                    sender_trade = Trade(
                        buyer=request.user,
                        seller=recipient,
                        trade_status='SE'
                    )
                    sender_trade.save()
                    trade = sender_trade
                    return redirect('trade:trade', pk=trade.pk)
            except Exception as e:
                print("ERROR saving trade status: " + str(e))
                return redirect('create_trade')
        else:
            return redirect('user:profile')


class OrderHistory(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            trades = Trade.objects \
                .filter(Q(seller=request.user) | Q(buyer=request.user))
            trades_pending = Trade.objects \
                .filter(trade_status='SE') \
                .filter(Q(seller=request.user) | Q(buyer=request.user))
            trades_closed = Trade.objects \
                .exclude(trade_status='SE') \
                .filter(Q(seller=request.user) | Q(buyer=request.user))
            context = {
                'trades': trades,
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
                form = TradeResponseForm(request.POST)
                if form.is_valid():
                    print('here')
                    trade.trade_status = request.POST.get('trade_response')
                    trade.response_date = datetime.now()
                    print(f'trade.trade_status: {trade.trade_status}')
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
            trade_response_form = TradeResponseForm()
            trade = Trade.objects.get(pk=pk)
            trade_item_list = TradeItem.objects.filter(trade__pk__contains=pk)
            message_list = Message.objects.filter(trade__pk__contains=pk)
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
