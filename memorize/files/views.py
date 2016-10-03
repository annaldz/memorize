"""Handling and managing files. Uploading, downloading, browsing, opening, sharing, removing  """
from django.shortcuts import render, redirect
from files.forms import SendFileForm, ShareForm, NewDirForm, AddImageForm
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse, StreamingHttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.servers.basehttp import FileWrapper
from django.core.files import File
from django.db import transaction
from files.models import FileStorage, File, FileShares, Directory, DirShares
import os
from django.utils import timezone
from django.contrib import messages
from django.http import Http404


STORAGE_LOCATION = 'files/static/files/storage/'

def handle_uploaded_file(in_file, file_hash):
    #opening new file for writing(destination) 
    # and rewrite in_file(file uplaoded by the user) chunk by chunk
    with open(STORAGE_LOCATION + file_hash, 'wb+') as destination:
        for chunk in in_file.chunks():
            destination.write(chunk)

@transaction.atomic
def send_file(request,picture='False'): #picture value describes if file is profile picture
    if request.method == 'POST':
        if picture == 'True':
            sendfile_form = AddImageForm(request.POST, request.FILES)
        else:
            sendfile_form = SendFileForm(request.POST, request.FILES)
        if sendfile_form.is_valid():
            file_storage_entry = FileStorage()
            if picture == 'True':
                file_storage_entry.is_pic = True
        
            file_entry = File()
            in_file  = request.FILES['file']
           #Set object fields
            file_storage_entry.name  = in_file.name
            file_storage_entry.size  = in_file.size
            file_storage_entry.orig_owner = request.user
            file_entry.owner = request.user
            timestamp = timezone.now()
            file_storage_entry.upload_t = timestamp
            file_entry.created_t = timestamp
            file_storage_entry.file_type = in_file.content_type
            file_entry.dir_id = Directory.objects.get(id = request.session['current_dir'])
        
            #Save in database
            try:
                with transaction.atomic():
                    file_storage_entry.save()
                    file_entry.file_id = file_storage_entry
                    file_entry.save()
            except:
                messages.error(request, 'Unable to save to the database!')
                return render(request, 'files/send_file.html', {'sendfile_form': sendfile_form})

            #Save file in STORAGE_LOCATION
            try:
                handle_uploaded_file(in_file, file_storage_entry.file_hash)
            except:
                messages.error(request, 'Unable to save the file!')
                return render(request, 'files/send_file.html', {'sendfile_form': sendfile_form})
            # Redirecting if successful
            if picture == 'True':
                
                return redirect('profile')
            else:
                messages.success(request, 'File saved!')
                return redirect('file_browser')
        # If form is invalid
        else:
            if picture == 'True':
                sendfile_form = AddImageForm()
                messages.error(request, 'Wrong file type. You have to choose the picture.')
                return render(request, 'files/add_pic.html', {'sendfile_form': sendfile_form})
            else:
                sendfile_form = SendFileForm()
                messages.error(request, 'Wrong file type or empty file.')
                return render(request, 'files/send_file.html', {'sendfile_form': sendfile_form})
    # If request method is not POST
    else:
        if picture == 'True':
            sendfile_form = AddImageForm()
            return render(request, 'files/add_pic.html', {'sendfile_form': sendfile_form})
        else:
            sendfile_form = SendFileForm()
            return render(request, 'files/send_file.html', {'sendfile_form': sendfile_form})

@login_required
def download_file(request, in_download_hash):
    #Select file object
    try:
        file_entry = File.objects.filter(download_hash = in_download_hash, owner = request.user)[0]
    except IndexError:
        messages.warning(request,'You cannot download the file, because you are not file owner')
        return redirect('file_browser')
    file_storage = file_entry.file_id
    file_location = STORAGE_LOCATION + file_storage.file_hash

    wrapper = FileWrapper(open(file_location,'rb'))
    response = HttpResponse(wrapper, content_type=file_storage.file_type)
    response['Content-Length'] = file_storage.size
    response['Content-Disposition'] = "attachment; filename=" + file_storage.name
    return response
   

@transaction.atomic
def delete_file_data(in_remove_hash):
    #Looking for file object to remove
    file_entry = File.objects.get(download_hash = in_remove_hash)
    #Looking for file storage object to remove if decreased counter = 0
    file_storage = file_entry.file_id
    file_location = STORAGE_LOCATION + file_storage.file_hash
    file_storage.counter -= 1

    try:
        with transaction.atomic():
            file_entry.delete()
            if (file_storage.counter == 0):
                file_storage.delete()
                os.remove(file_location)
            else:
                file_storage.save()
    except:
        raise Exception("Connot remove the file")

@login_required
def remove_file(request, in_remove_hash):
    file_entry = File.objects.get(download_hash = in_remove_hash)
    if (request.user != file_entry.owner):
        raise Http404

    try: #Call function that removes 
        delete_file_data(in_remove_hash)
    except:
        messages.error(request, 'Can not delete the file!')
        return redirect('file_browser')

    messages.success(request, 'File deleted')
    return redirect('file_browser')

@login_required
def share_assets(request):
    if request.method == 'POST':
        share_form = ShareForm(request.POST)
        if share_form.is_valid() and request.session['share_asset_entry'] and request.session['share_asset_type']:
            shared_username = share_form.cleaned_data['username']
            try:
                user = User.objects.filter(username = shared_username)[0]
            except IndexError:
                messages.warning(request, 'User with this username does not exists')
                return redirect('file_browser')
            if request.user == user:
                messages.warning(request, 'You cannot share file with yourself!')
                return redirect('file_browser')
                

            asset_entry = None
            share_entry = None
            prev_entries = None
            #Checking if file or dir is shared
            if (request.session['share_asset_type'] == 'f'):
                asset_entry = File.objects.get(download_hash = request.session['share_asset_entry'])
                share_entry = FileShares()
                prev_entries = FileShares.objects.filter(share_id = asset_entry, shared_with = user)
            elif (request.session['share_asset_type'] == 'd'):
                asset_entry = Directory.objects.get(hash = request.session['share_asset_entry'])
                share_entry = DirShares()
                prev_entries = DirShares.objects.filter(share_id = asset_entry, shared_with = user)
            else:
                return HttpResponse("Wrong Type")

            if (request.user != asset_entry.owner):
                raise Http404
            #Checking if file has been shared with user
            if (len(prev_entries) != 0):
                messages.warning(request, 'The file has been already shared!')
                return redirect('file_browser')
            #Set object fields and save to database
            share_entry.shared_with = user
            share_entry.created_t = timezone.now()
            share_entry.share_id = asset_entry
            share_entry.save()

            messages.success(request, 'File shared')
            return redirect('file_browser')
        else:
            messages.warning(request, 'Username cannot be an empty string')
            return redirect('file_browser')
    else:
        return HttpResponse("YOU SHALL NOT PASS!")

@login_required
def share_assets_wrapper(request, in_share_hash):
    request.session['share_asset_entry'] =  in_share_hash
    asset_entry = None
    #Checking if shared type is file or dir

    try:
        try:
            asset_entry = File.objects.get(download_hash = in_share_hash)
            request.session['share_asset_type'] = 'f'
        except:
            asset_entry = Directory.objects.get(hash = in_share_hash)
            request.session['share_asset_type'] = 'd'
    except:
            del request.session['share_asset_entry']
            del request.session['share_asset_type']
            messages.error(request, 'Wrong arguments')
            return redirect('file_browser')
    #Create user list
    user_list=User.objects.all().values_list('username')
    share_form = ShareForm(data_list=user_list)
    return render(request, 'files/share_file.html', {'share_form': share_form, 'asset_entry': asset_entry, 'asset_type': request.session['share_asset_type']})

def unshare(request, in_share_hash):
    try:
        request.session['share_asset_type']
    except KeyError:
        request.session['share_asset_type']= 'n'
    #Checking the type of shared file
    try:
        try:
            asset_entry = File.objects.get(download_hash = in_share_hash)
            share_obj = File.objects.filter(download_hash = in_share_hash)[0]
            request.session['share_asset_type'] = 'f'
        except:
            asset_entry = Directory.objects.get(hash = in_share_hash)
            share_obj= Directory.objects.filter(hash = in_share_hash)[0]
            request.session['share_asset_type'] = 'd'
    except:
        del request.session['share_asset_type']
        messages.error(request, 'Wrong Type')
        return redirect('file_browser')
    #Filter FileShare object and delete it  
    try:
        if request.session['share_asset_type'] == 'f':
            share = FileShares.objects.filter(share_id=share_obj,shared_with=request.user)[0]
        else:
            share = DirShares.objects.filter(share_id=share_obj,shared_with=request.user)[0]
        share.delete()
    except:
        messages.error(request, 'Cannot unshare')
        return redirect('file_browser')
    messages.success(request,'File unshared')
    return redirect('file_browser')

def new_dir(request):
    if request.method == 'POST':
        new_dir_form = NewDirForm(request.POST)
        if new_dir_form.is_valid():
            dir_name = new_dir_form.cleaned_data['dir_name']

            new_dir = Directory()
            #Set object fields
            current_dir = Directory.objects.get(id =  request.session['current_dir'])
            new_dir.parent_id = current_dir
            new_dir.owner = request.user
            new_dir.created_t = timezone.now()
            new_dir.dir_name = dir_name

            if (current_dir.full_path != '/'):
                new_dir.full_path = current_dir.full_path + '/' + dir_name
            else:
                new_dir.full_path = current_dir.full_path + dir_name
            #Save to database
            new_dir.save()
            messages.success(request, 'Directory created')
            return redirect('file_browser')
        else:
            return render(request, 'files/new_dir.html', {'new_dir_form': new_dir_form})
            
    else:
        new_dir_form = NewDirForm()
        return render(request, 'files/new_dir.html', {'new_dir_form': new_dir_form})

@transaction.atomic
def remove_dir(request, in_remove_hash):
    directory = Directory.objects.get(hash = in_remove_hash)
    if (request.user != directory.owner):
        raise Http404

    dir_files = File.objects.filter(owner = request.user, dir_id = directory)
    #Remove all files that directory is dir to remove 
    try:
        with transaction.atomic():
            for dir_file_entry in dir_files:
                delete_file_data(dir_file_entry.download_hash)
    #Remove directory
            directory.delete()
    except:
        messages.error(request, 'Could not delete the files!')
        return redirect('file_browser')

    messages.success(request, 'Directory deleted.')
    return redirect('file_browser')

def change_dir(request, in_dir_hash, is_share = 'False'):
    directory = Directory.objects.get(hash = in_dir_hash)
    request.session['current_dir'] = directory.id
    #Checking if dir.now is shared or regular dir and set session values
    if is_share == 'True':
        request.session['current_dir_is_share'] = 'True'
        return redirect('file_browser')    
    else:
        request.session['current_dir_is_share'] = 'False'
        return redirect('file_browser') 

def file_browser(request):
    try:
        request.session['current_dir']
    except KeyError:
        request.session['current_dir'] = request.user.profile.home_dir.id
    try:
        request.session['current_dir_is_share']
    except KeyError:
        request.session['current_dir_is_share'] = 'False'
    #Check if current dir or parent, grandparent etc was actually shared with request user
    if request.session['current_dir_is_share'] == 'True':
        try:
            directory = Directory.objects.filter(id = request.session['current_dir'])[0]
        except:
            messages.error(request, 'Cannot find current dir')
            request.session['current_dir'] = request.user.profile.home_dir.id
            request.session['current_dir_is_share'] = 'False'
            return redirect('file_browser')
        dir_or_parent_shared = False
        while directory.parent_id:
            try:
                dir_shares_object = DirShares.objects.filter(share_id=directory, shared_with=request.user)[0]
                request.session['shared_parent_dir'] = dir_shares_object.share_id.id
                dir_or_parent_shared = True
                break
            except:
                try:
                    directory = Directory.objects.filter(id = directory.parent_id.id)[0]
                except:
                    messages.error(request, 'Cannot find current dir parent')
                    request.session['current_dir'] = request.user.profile.home_dir.id
                    request.session['current_dir_is_share'] = 'False'
                    return redirect('file_browser')
        #If current dir or parent, grandparent etc was actually shared with request user set dir and file lists        
        if dir_or_parent_shared == True:
                
            dir_now = Directory.objects.get(id = request.session['current_dir'])
            dir_list  = Directory.objects.filter(parent_id = dir_now)
            file_list = File.objects.filter(dir_id = dir_now)
            return render(request, 'files/browser.html', {'dir_now': dir_now, 'dir_list': dir_list, 'file_list': file_list,'is_share_dir': request.session['current_dir_is_share']})
        else: #If current dir or parent, grandparent is not shared with request user return to home dir 
            request.session['current_dir'] = request.user.profile.home_dir.id
            request.session['current_dir_is_share'] = 'False'
            return redirect('file_browser')
    else: #If directory is not shared directory
        dir_now = Directory.objects.get(id = request.session['current_dir'])

        dir_list  = Directory.objects.filter(owner = request.user, parent_id = dir_now)
        file_list = File.objects.filter(owner = request.user, dir_id = dir_now)

        shared_list = FileShares.objects.filter(shared_with = request.user)
        dir_shared_list = DirShares.objects.filter(shared_with = request.user)
        return render(request, 'files/browser.html', {'dir_now': dir_now, 'dir_list': dir_list, 'file_list': file_list, 'shared_list': shared_list, 'dir_shared_list': dir_shared_list,'is_share_dir': request.session['current_dir_is_share']})

def open_file(request,in_open_hash):
   
    file_entry = File.objects.get(download_hash = in_open_hash)
    file_storage_entry = file_entry.file_id
    file_hash = file_storage_entry.file_hash
    file_content = file_storage_entry.file_type
    file_location = STORAGE_LOCATION + str(file_hash)
    data = open(file_location, "rb").read()
    return HttpResponse(data, content_type=file_content)

