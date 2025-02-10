from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator
from django.http import JsonResponse
import json 
from .models import User,Post,Follow,Like

def edit(request,post_id):
    if request.method =="POST":
        data=json.loads(request.body)
        edit_post =Post.objects.get(pk=post_id)
        edit_post.content = data["content"]
        edit_post.save()
        return JsonResponse({"message":"like removed"})


def remove_like(request,post_id):
    post=Post.objects.get(pk=post_id)
    user= User.objects.get(pk=request.user.id)
    like= Like(user=user,post=post)
    like.delete()
    return JsonResponse({"message":"like added"}) 
    

def add_like(request,post_id):
    post=Post.objects.get(pk=post_id)
    user= User.objects.get(pk=request.user.id)
    newLike= Like(user=user,post=post)
    newLike.save()
    return JsonResponse({"message":"like added"})

def index(request):
    allpost= Post.objects.all().order_by("id").reverse()

    # pagination
    paginator = Paginator(allpost,10)
    page_number = request.GET.get('page')
    posts_of_the_page=paginator.get_page(page_number)

    allLikes=Like.objects.all()
    whoYouLiked=[]
    try:
         for like in allLikes:
             if like.user.id==request.user.id:
                 whoYouLiked.append(like.post.id)
    except:
        whoYouLiked=[]


    return render(request, "network/index.html", {
        "allpost": allpost,
        "posts_of_the_page":posts_of_the_page,
        "whoYouLiked":whoYouLiked,

    })

def new_post(request):
    if request.method=="POST":
        content=request.POST['content']
        user=User.objects.get(pk=request.user.id)
        post=Post(content=content , user=user)
        post.save()
        return HttpResponseRedirect(reverse(index))
    

def profile(request,user_id):
    user=User.objects.get(pk=user_id)

    allpost= Post.objects.filter(user=user).order_by("id").reverse()
    following=Follow.objects.filter(user= user)
    followers=Follow.objects.filter(user_follower= user)
    try:
        checkFollow= followers.filter(user=User.objects.get(pk=request.user.id))
        if len(checkFollow) !=0:
          isFollowing=True
        else:
          isFollowing=False

    except:
          isFollowing=False



    # pagination
    paginator = Paginator(allpost,10)
    page_number = request.GET.get('page')
    posts_of_the_page=paginator.get_page(page_number)


    return render(request, "network/profile.html", {
            "allpost": allpost,
            "posts_of_the_page":posts_of_the_page,
            "username":user.username,
            "following":following,
            "followers":followers,
            "isFollowing":isFollowing,
            "user_profile":user,

    })




def following(request):
    # Ensure the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if the user is not authenticated

    # Get the current user
    currentuser = request.user

    # Get the users that the current user is following
    following_users = Follow.objects.filter(user=currentuser).values_list('user_follower', flat=True)

    # Filter posts to only include those from users the current user is following
    following_posts = Post.objects.filter(user__in=following_users).order_by('-id')

    # Paginate the posts
    paginator = Paginator(following_posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    posts_of_the_page = paginator.get_page(page_number)

    # Render the template with the paginated posts
    return render(request, "network/following.html", {
        "posts_of_the_page": posts_of_the_page,
    })




def follow(request):
    
    userfollow= request.POST['userfollow']
    currentUser =User.objects.get(pk=request.user.id)
    userfollowData=User.objects.get(username=userfollow)
    f=Follow(user=currentUser,user_follower=userfollowData)
    f.save()
    user_id=userfollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id':user_id}))


def unfollow(request):
    userfollow= request.POST['userfollow']
    currentUser =User.objects.get(pk=request.user.id)
    userfollowData=User.objects.get(username=userfollow)
    f=Follow.objects.get(user=currentUser,user_follower=userfollowData)
    f.delete()
    user_id=userfollowData.id
    return HttpResponseRedirect(reverse(profile, kwargs={'user_id':user_id}))

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
