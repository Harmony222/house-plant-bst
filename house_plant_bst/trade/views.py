from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
# from django.conf import settings
from django.views import View
from .models import Thread, Message
from .forms import ThreadForm, MessageForm
from django.db.models import Q
# User = settings.AUTH_USER_MODEL
from django.contrib.auth.models import User


class CreateThread(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = ThreadForm()
            context = {
                'form': form
            }
            return render(request, 'trade/create-thread.html', context)
        else:
            return redirect('user:profile')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = ThreadForm(request.POST)
            username = request.POST.get('username')
            try:
                recipient = User.objects.get(username=username)
                if Thread.objects.filter(user=request.user,
                                         recipient=recipient).exists():
                    thread = Thread.objects.filter(user=request.user,
                                                   recipient=recipient)[0]
                    return redirect('thread', pk=thread.pk)
                elif Thread.objects.filter(user=recipient,
                                           recipient=request.user).exists():
                    thread = Thread.objects.filter(user=recipient,
                                                   recipient=request.user)[0]
                    return redirect('thread', pk=thread.pk)
                if form.is_valid():
                    sender_thread = Thread(
                        user=request.user,
                        recipient=recipient
                    )
                    sender_thread.save()
                    thread_pk = sender_thread.pk
                    return redirect('thread', pk=thread_pk)
            except:
                return redirect('create-thread')
        else:
            return redirect('user:profile')


class ListThreads(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            threads = Thread.objects.filter(Q(user=request.user) | Q(recipient=request.user))
            context = {'threads': threads}
            return render(request, 'trade/list-threads.html', context)
        else:
            return redirect('user:profile')


class CreateMessage(View):
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            thread = Thread.objects.get(pk=pk)
            if thread.recipient == request.user:
                recipient = thread.user
            else:
                recipient = thread.recipient
                message = Message(
                    thread=thread,
                    sender_user=request.user,
                    recipient_user=recipient,
                    body=request.POST.get('message'),
                )
                message.save()
                return redirect('thread', pk=pk)
        else:
            return redirect('user:profile')


class ThreadView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            form = MessageForm()
            thread = Thread.objects.get(pk=pk)
            message_list = Message.objects.filter(thread__pk__contains=pk)
            context = {
                'thread': thread,
                'form': form,
                'message_list': message_list
            }
            return render(request, 'trade/thread.html', context)
        else:
            return redirect('user:profile')