from django.shortcuts import render, redirect
from django.views import View
from .models import Trade, Message, TradeItem
from .forms import TradeForm, MessageForm, TradeResponseForm
from django.db.models import Q
from django.contrib.auth import get_user_model
User = get_user_model()


class CreateTrade(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = TradeForm()
            context = {
                'form': form
            }
            return render(request, 'trade/create_trade.html', context)
        else:
            return redirect('user:profile')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = TradeForm(request.POST)
            username = request.POST.get('username')
            # try:
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
            # except:
                return redirect('trade:create_trade')
        else:
            return redirect('user:profile')


class ListTrades(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            trades = Trade.objects.filter(Q(seller=request.user) | Q(buyer=request.user))
            context = {'trades': trades}
            return render(request, 'trade/list_trades.html', context)
        else:
            return redirect('user:profile')


class SetTradeResponse(View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            trade = Trade.objects.get(pk=pk)
            if trade.seller == request.user:
                form = TradeResponseForm()
                context = {'form': form,}
                return render(request, 'trade/trade.html', context)


                # return render_to_response('trades',
                                           # locals(),
                                           # context_instance=RequestContext(request))
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
            form = MessageForm()
            trade = Trade.objects.get(pk=pk)
            trade_item_list = TradeItem.objects.filter(trade__pk__contains=pk)
            message_list = Message.objects.filter(trade__pk__contains=pk)
            context = {
                'trade': trade,
                'form': form,
                'trade_item_list': trade_item_list,
                'message_list': message_list
            }
            return render(request, 'trade/trade.html', context)
        else:
            return redirect('user:profile')