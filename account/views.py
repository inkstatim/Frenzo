from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm, MessageForm
from .models import Profile, Friendship, Message
from django.contrib import messages


# Create your views here.
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Создать новый объект пользователя,
            # но пока не сохранять его
            new_user = user_form.save(commit=False)
            # Установить выбранный пароль
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            # Создать профиль пользователя
            Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html', {'user_form': user_form, 'profile_form': profile_form})


@login_required
def profile(request, username):
    user = get_object_or_404(User, username=username)
    recipient_id = user.id  # Используйте id пользователя в качестве recipient_id
    return render(request, 'account/profile.html', {'user': user, 'recipient_id': recipient_id})


@login_required
def follow(request, username):
    user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        if request.user != user:
            if request.user.profile.following.filter(username=username).exists():
                request.user.profile.following.remove(user)
                user.profile.followers.remove(request.user)
            else:
                request.user.profile.following.add(user)
                user.profile.followers.add(request.user)

        return redirect('profile', username=username)

    return HttpResponse("Invalid request")


def user_list(request):
    users = User.objects.all()
    return render(request, 'account/user_list.html', {'users': users})


@login_required
def send_friend_request(request, to_user_id):
    from_user = request.user
    to_user = get_object_or_404(User, id=to_user_id)
    friendship, created = Friendship.objects.get_or_create(from_user=from_user, to_user=to_user)
    if created:
        pass
    # Если объект Friendship был только что создан, можно выполнить дополнительные действия, если необходимо

    return redirect('profile', username=to_user.username)


def accept_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id, to_user=request.user)
    friendship.status = 'accepted'
    friendship.save()
    # Здесь можно выполнить дополнительные действия, связанные с принятием запроса на дружбу

    return redirect('profile', username=friendship.from_user.username)


@login_required
def reject_friend_request(request, friendship_id):
    friendship = get_object_or_404(Friendship, id=friendship_id, to_user=request.user)
    friendship.status = 'rejected'
    friendship.save()
    # Здесь можно выполнить дополнительные действия, связанные с отклонением запроса на дружбу

    return redirect('profile', username=friendship.from_user.username)


@login_required
def friend_list(request):
    # Логика для получения списка друзей
    friends = request.user.profile.following.all()
    return render(request, 'account/friend_list.html', {'friends': friends})


@login_required
def create_message(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    form = MessageForm(request.POST or None)
    if form.is_valid():
        message = form.save(commit=False)
        message.sender = request.user
        message.recipient = recipient
        message.save()
        return redirect('conversation', recipient_id=recipient_id)
    return render(request, 'account/create_message.html', {'form': form, 'recipient_id': recipient_id})


@login_required
def conversation(request, recipient_id):
    recipient = get_object_or_404(User, id=recipient_id)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=recipient) | Q(sender=recipient, recipient=request.user)).order_by('timestamp')
    form = MessageForm()

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            form = MessageForm()  # Очистка формы после успешной отправки

    context = {'recipient': recipient, 'messages': messages, 'form': form}
    return render(request, 'account/conversation.html', context)

@login_required
def followers_view(request, username):
    user = User.objects.get(username=username)
    followers = user.profile.followers.all()
    return render(request, 'account/followers.html', {'followers': followers})

@login_required
def following_view(request, username):
    user = User.objects.get(username=username)
    following = user.profile.following.all()
    return render(request, 'account/following.html', {'following': following})
