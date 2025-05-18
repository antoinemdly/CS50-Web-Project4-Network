from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
import datetime

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

import json


from .models import User,Post


def index(request):
    return render(request, "network/index3.html")

def following(request):
    return render(request, "network/following")

@csrf_exempt
# @login_required
def posts(request, category):
    if request.method == "GET":
        response_data = {}
        if category == 'all':
            posts = Post.objects.order_by("-date").all()
        elif category == 'following':
            if not request.user.is_authenticated:
                return HttpResponseRedirect(reverse("login"))
            user = get_object_or_404(User, id=request.user.id)
            followed = user.followed.all()
            posts = Post.objects.filter(user__in=followed).order_by('-date')
                
            # return JsonResponse([people.serialize() for people in followed], safe=False)
        else:
            if User.objects.filter(username=category).exists():
                user = User.objects.get(username=category)
                posts = Post.objects.filter(user=user)

                response_data = {
                    'followers' : user.followers.count(),
                    'following' : user.followed.count()
                }

                if request.user == user:
                    response_data.update({'IsSelf':True})
            else:

                return JsonResponse({"error": "incorrect posts category or user doesn't exist"}, status=400)
        
        page_number = request.GET.get('page')

        if page_number:
            p = Paginator(posts, 10)
            current_page = p.page(page_number)
            print(current_page.number)
            posts = current_page.object_list
            print(posts)

            data = {
                'has_next': current_page.has_next(),
                'has_previous': current_page.has_previous(),
                'num_pages': p.num_pages,
                'current_page': current_page.number,
                'posts': [post.serialize() for post in posts],
            }
            response_data.update(data) 
            
            return JsonResponse(response_data, safe=False)

        return JsonResponse([post.serialize() for post in posts], safe=False)

    elif request.method == 'POST':
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse("login"))
        if category == 'new_post':
            data = json.loads(request.body)
            if data['content'].strip() == "":
                return JsonResponse({"error": "Content requiered"}, status=400)
            post = Post(user=request.user,content=data['content'],date=datetime.datetime.now())
            post.save()

            print(data['content'])
            return JsonResponse({"message": "a POST request"}, status=200)
    else:
        return JsonResponse({"error": "Not a POST request"}, status=400)

@csrf_exempt
def api(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if data.get('authenticated') is not None:
            if request.user.is_authenticated:
                return JsonResponse(True, safe=False)
            else:
                return JsonResponse(False, safe=False)
        if data.get('followed') is not None:
            user = data.get('followed')

            try:
                query_user = User.objects.get(username=user)
            except User.DoesNotExist:
                return JsonResponse({"message": "The user doesn't exist"}, status=400)
            
            followed_users = request.user.followed.all()
            response = query_user in followed_users
            
            return JsonResponse(response, safe=False)
        if data.get('isMyPost') is not None:
            user = data.get('isMyPost')
            try:
                query_user = User.objects.get(username=user)
            except User.DoesNotExist:
                return JsonResponse({"message": "The user doesn't exist"}, status=400)
            response = (query_user == request.user)
            return JsonResponse(response, safe=False)
        if data.get('isLiked') is not None:
            user = data.get('isLiked')
            post_id = data.get('post_id')

            try:
                query_user = User.objects.get(username=user)
            except User.DoesNotExist:
                return JsonResponse({"message": "The user doesn't exist"}, status=400)
            
            try:
                    query_post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return JsonResponse({"message": "The Post doesn't exist"}, status=400)
            
            users_liked = query_post.like_count.all()

            response = (request.user in users_liked)

            return JsonResponse(response, safe=False)


    elif request.method == 'PUT':
        data = json.loads(request.body)
        if data.get('unfollow') is not None:
            user = data.get('unfollow')
            try:
                    query_user = User.objects.get(username=user)
            except User.DoesNotExist:
                return JsonResponse({"message": "The user doesn't exist"}, status=400)

            try:
                request.user.followed.remove(query_user)
            except ValueError:
                return JsonResponse({"message": "User not followed"}, status=400)
            return JsonResponse({"message": "User Unfollowed"}, status=200)
        elif data.get('follow') is not None:
            user = data.get('follow')
            try:
                query_user = User.objects.get(username=user)
            except User.DoesNotExist:
                return JsonResponse({"message": "The user doesn't exist"}, status=400)

            try:
                request.user.followed.add(query_user)
            except ValueError:
                return JsonResponse({"message": "User already followed ???"}, status=400)
            return JsonResponse({"message": "User successfully Followed"}, status=200)
        elif data.get('edit_post') is not None:
            post_id = data.get('post_id')
            content = data.get('edit_post')

            try:
                    query_post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return JsonResponse({"message": "The Post doesn't exist"}, status=400)
            
            # If the user making the edit is not the user of the post
            if query_post.user != request.user:
                return JsonResponse({"message": "Trying to edit a post of another user"}, status=400)

            query_post.content = content
            query_post.save()

            return JsonResponse({"message": "Post edited successfully"}, status=200)

        elif data.get('like') is not None:
            post_id = data.get('like')

            try:
                query_post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return JsonResponse({"message": "The Post doesn't exist"}, status=400)
            
            query_post.like_count.add(request.user)

            return JsonResponse({"message": "Post liked successfully"}, status=200)

        elif data.get('unlike') is not None:
            post_id = data.get('unlike')

            try:
                query_post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return JsonResponse({"message": "The Post doesn't exist"}, status=400)
            
            query_post.like_count.remove(request.user)

            return JsonResponse({"message": "Post unliked successfully"}, status=200)

    return JsonResponse({"message": "Incorrect API request"}, status=400)

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
