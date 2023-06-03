from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from posts.froms import CommentForm
from posts.models import Post, Comment
from .forms import LoginForm, UserRegistrationForm, UserEditForm, \
    ProfileEditForm, MessageForm
from .models import Profile, Friendship, Message
from django.contrib import messages


class UserLoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'account/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'],
                                password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user
        following = user.profile.following.all()
        posts = Post.objects.filter(author__in=following)
        comment_form = CommentForm()
        comments = {}

        for post in posts:
            comments[post.id] = Comment.objects.filter(post=post)[:3]

        return render(request, 'account/dashboard.html', {'posts': posts, 'comment_form': comment_form, 'comments': comments})



class UserRegistrationView(View):
    def get(self, request):
        user_form = UserRegistrationForm()
        return render(request, 'account/register.html', {'user_form': user_form})

    def post(self, request):
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html', {'new_user': new_user})

        # Если форма недействительна, верните пользователю форму с ошибками
        return render(request, 'account/register.html', {'user_form': user_form})


class UserEditView(LoginRequiredMixin, View):
    def get(self, request):
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
        return render(request, 'account/edit.html',
                      {'user_form': user_form, 'profile_form': profile_form})

    def post(self, request):
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                       data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('dashboard')
        else:
            messages.error(request, 'Error updating your profile')
        return redirect('dashboard')


class ProfileView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)
        recipient_id = user.id
        return render(request, 'account/profile.html',
                      {'user': user, 'recipient_id': recipient_id})


class FollowView(LoginRequiredMixin, View):
    def post(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.user != user:
            if request.user.profile.following.filter(
                    username=username).exists():
                request.user.profile.following.remove(user)
                user.profile.followers.remove(request.user)
            else:
                request.user.profile.following.add(user)
                user.profile.followers.add(request.user)
        return redirect('profile', username=username)


class UserListView(View):
    def get(self, request):
        users = User.objects.all()
        return render(request, 'account/user_list.html', {'users': users})


class SendFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, to_user_id):
        from_user = request.user
        to_user = get_object_or_404(User, id=to_user_id)
        friendship, created = Friendship.objects.get_or_create(
            from_user=from_user, to_user=to_user)
        if created:
            pass
        return redirect('profile', username=to_user.username)

    def post(self, request, to_user_id):
        from_user = request.user
        to_user = get_object_or_404(User, id=to_user_id)
        friendship, created = Friendship.objects.get_or_create(
            from_user=from_user, to_user=to_user)
        if created:
            pass
        return redirect('profile', username=to_user.username)


class AcceptFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, id=friendship_id,
                                       to_user=request.user)
        friendship.status = 'accepted'
        friendship.save()
        return redirect('profile', username=friendship.from_user.username)


class RejectFriendRequestView(LoginRequiredMixin, View):
    def get(self, request, friendship_id):
        friendship = get_object_or_404(Friendship, id=friendship_id,
                                       to_user=request.user)
        friendship.status = 'rejected'
        friendship.save()
        return redirect('profile', username=friendship.from_user.username)


class FriendListView(LoginRequiredMixin, View):
    def get(self, request):
        friends = request.user.profile.following.all()
        return render(request, 'account/friend_list.html',
                      {'friends': friends})


class CreateMessageView(LoginRequiredMixin, View):
    def get(self, request, recipient_id):
        form = MessageForm()
        return render(request, 'account/create_message.html',
                      {'form': form, 'recipient_id': recipient_id})

    def post(self, request, recipient_id):
        recipient = get_object_or_404(User, id=recipient_id)
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            return redirect('conversation', recipient_id=recipient_id)
        return render(request, 'account/create_message.html',
                      {'form': form, 'recipient_id': recipient_id})


class ConversationView(LoginRequiredMixin, View):
    def get(self, request, recipient_id):
        recipient = get_object_or_404(User, id=recipient_id)
        messages = Message.objects.filter(
            Q(sender=request.user, recipient=recipient) |
            Q(sender=recipient, recipient=request.user)).order_by('timestamp')
        form = MessageForm()
        return render(request, 'account/conversation.html',
                      {'recipient': recipient, 'messages': messages,
                       'form': form})

    def post(self, request, recipient_id):
        recipient = get_object_or_404(User, id=recipient_id)
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = recipient
            message.save()
            form = MessageForm()
        messages = Message.objects.filter(
            Q(sender=request.user, recipient=recipient) |
            Q(sender=recipient, recipient=request.user)).order_by('timestamp')
        return render(request, 'account/conversation.html',
                      {'recipient': recipient, 'messages': messages,
                       'form': form})


class FollowersView(LoginRequiredMixin, View):
    def get(self, request, username):
        user = User.objects.get(username=username)
        followers = user.profile.followers.all()
        return render(request, 'account/followers.html',
                      {'followers': followers})


class FollowingView(LoginRequiredMixin, View):
    def get(self, request, username):
        user = User.objects.get(username=username)
        following = user.profile.following.all()
        return render(request, 'account/following.html',
                      {'following': following})
