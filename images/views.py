import redis
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from actions.utils import create_action
from django.conf import settings

from .forms import ImageCreateForm
from .models import Image

# Connect to Redis
r = redis.Redis(host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB)

# Create your views here.
@login_required
def image_create(request):
    if request.method == 'POST':
        # form is sent
        form = ImageCreateForm(request.POST)
        if form.is_valid():
            # form data valid
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # assign current user to image
            new_image.user = request.user
            new_image.save()
            create_action(request.user, 'bookmarked image', new_image)
            messages.success(request, 'Image linked successfully')
            # redirect to newly created item view
            return redirect(new_image.get_absolute_url())
    else:
        # build the form with data provided by Javascript
        form = ImageCreateForm(data=request.GET)
    return render(request, 'images/image/create.html',
                  {'section': 'images', 'form': form})

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == 'like':
                image.users_like.add(request.user)
                create_action(request.user, 'likes', image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status': 'ok'})
        except Image.DoesNotExist:
            pass
    return JsonResponse({'status': 'error'})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    # increment total image views by 1 (Redis)
    total_views = r.incr(f'image:{image.id}:views')
    return render(request, 'images/image/detail.html',
                  {'section': 'images', 'image': image,
                  'total_views': total_views})

@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get('page')
    images_only = request.GET.get('images_only')
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        # if page is not an integer deliver first page
        images = paginator.page(1)
    except EmptyPage:
        if images_only:
            # if page out of range return last page of results
            return HttpResponse('')
    if images_only:
        return render(request, 'images/image/list_images.html',
                      {'section': 'images', 'images': images})
    return render(request, 'images/image/list.html',
                  {'section': 'images', 'images': images})
