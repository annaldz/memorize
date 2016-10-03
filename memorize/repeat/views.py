"""Creating lists and flashcards, removing, revising, viewing and setting session flashcard limits """
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from .models import List, Flashcard
from django.utils import timezone
from datetime import timedelta
from .forms import ListForm, FlashcardForm, LimitForm
from django.contrib import messages


@login_required
def arrange_list(request):
    lists = List.objects.filter(owner=request.user).order_by('name')
    return render(request, 'repeat/list.html', {'lists': lists})

@login_required
def list(request):
   # Upadate status for all user lists
    lists = List.objects.filter(owner=request.user)
    for list_object in lists: #Empty status is defult for new list
        try:
            most_difficult_flashcard = Flashcard.objects.filter(list_id=list_object.id).order_by('-difficulty')[0]
            least_difficult_flashcard = Flashcard.objects.filter(list_id=list_object.id).order_by('difficulty')[0]
        except IndexError:
            list_object.status = 'e'
            list_object.save()
            continue
        list_object.status = 'n' #Normal status -default for lists that has any flashcards
        list_object.save()
        if most_difficult_flashcard.difficulty > 128.0 and least_difficult_flashcard.difficulty > 1.0:
            list_object.status = 'h' #Hard status for lists that difficulty (1,128+n>, n>0 or (x,1000+n>, n>1, x <= 1000+n  
            list_object.save()
        if most_difficult_flashcard.difficulty > 1000.0: 
            list_object.status = 'h'
            list_object.save()
        if most_difficult_flashcard.difficulty < 0.2:
            list_object.status = 's' #Simple status for lists that difficulty (x,0.2-n>, n>0, x <= 0.2-n
            list_object.save()
        date_count = timezone.now() - timedelta(days=70)
        try:
            if date_count > most_difficult_flashcard.repeat_date:
                list_object.status = 'o' #Old status for lists that most difficult flashcard repeat date was 70 days ago  
                list_object.save()
        except TypeError:
            if date_count > most_difficult_flashcard.created_date:
                list_object.status = 'o'#For lists that are not repeated, old ststus if created date was 70 days ago(not for empty lists)
                list_object.save()
        date_count_2 = timezone.now() - timedelta(days=130)
        try:
            if date_count_2 > most_difficult_flashcard.repeat_date:
                list_object.status = 'x' #Extra old status for lists that most difficult flashcard repeat date was 130 days ago
                list_object.save()
        except TypeError:
            if date_count_2 > most_difficult_flashcard.created_date:
                list_object.status = 'x' #For lists that are not repeated, extra old ststus if created date was 130 days ago(not for empty lists)
                list_object.save()
    return arrange_list(request)
            
             

@login_required
def see_list(request, pk):
    list_object = get_object_or_404(List, pk=pk)
    if (request.user != list_object.owner):
        raise Http404
    flashcards = Flashcard.objects.filter(list_id = pk).order_by('question') 
    return render(request, 'repeat/see_list.html', {'list_object': list_object, 'flashcards': flashcards })

@login_required
def rep(request, pk):
    list_object = get_object_or_404(List, pk=pk)
    if (request.user != list_object.owner):
        raise Http404
    flashcards = Flashcard.objects.filter(list_id = pk).order_by('difficulty') 
    return render(request, 'repeat/revise.html', {'list_object': list_object, 'flashcards': flashcards })

@login_required
def add_list(request,template_name="repeat/add_list.html"):
    if request.method == "POST":
        form = ListForm(data=request.POST)
        if form.is_valid():
            list_name =  form.cleaned_data['name']
            #Create new list object and set its fields
            new_list=List()
            new_list.owner=request.user
            new_list.name=list_name
            try:
                new_list.save()
            except:
                messages.warning(request, 'Cannot save to database.')
                return redirect('add_list')
            return HttpResponseRedirect('/repeat/')
        else:
            messages.warning(request, 'Form is invalid. Try again with valid data.')
            return redirect('add_list')
    else:
        form = ListForm()
        return render(request, template_name, {'form' : form })

@login_required
def remove_list(request, pk):
    try:
        list_object= List.objects.filter(pk=pk)[0] #Raise Http404 if list does not exists or is not request user list
    except IndexError:
        raise Http404
        
    if (request.user != list_object.owner):
        raise Http404
    try:
            list_object.delete() #Try to delete list object
    except:
        raise Http404
    messages.success(request, 'List deleted')
    return redirect('list') 

@login_required
def remove_flashcard(request, pk):
    try:
        flashcard_object= Flashcard.objects.filter(pk=pk)[0] #Raise Http404 if flashcard does not exists or is not in any request user list
    except IndexError:
        raise Http404
        
    if (request.user != flashcard_object.list_id.owner):
        raise Http404
    try:
            flashcard_object.delete() #Try to delete flashcard object
    except:
        raise Http404
    messages.success(request, 'Flashcard deleted')
    return redirect('see_list', flashcard_object.list_id.id) 
        
@login_required
def add_flashcard(request, pk, template_name="repeat/add_flashcard.html"):
    if request.method == "POST":
        form = FlashcardForm(data=request.POST)
        if form.is_valid():
            flashcard_question =  form.cleaned_data['question']
            flashcard_answer = form.cleaned_data['answer']
            new_flashcard=Flashcard()
            new_flashcard.question = flashcard_question
            new_flashcard.answer = flashcard_answer
            new_flashcard.list_id= List.objects.get(id = pk)
            new_flashcard.save()
            return see_list(request,pk)
        else:
            return render(request, template_name, {'form' : form })
    else:
        form = FlashcardForm()
        return render(request, template_name, {'form' : form })
@login_required
def revise (request, pk, template_name="repeat/revise.html",final_template="repeat/final.html",no_flashcard_template="repeat/no_flashcard.html"):
    list_object = get_object_or_404(List, pk=pk)
    if (request.user != list_object.owner):
        raise Http404
    pk_str = str(pk)

    # Checking if flashcard counter exists
    if not pk_str in request.session:
        request.session[pk_str] = str(0) #Set flashcard counter for this session to 0

    #Checking if counter achieves limit
    elif list_object.limit <= int(request.session[pk_str]):
        return render(request,final_template)
    status = pk_str + '_status'
    
    #Checking if flashcards' status exists
    try:
        request.session[status]
    except KeyError:
        request.session[status] = str(0) #Set flashcard status to 0

    flashcard_status = request.session[status]
    
    list_id_current_flashcard = pk_str + '_current_flashcard'
    list_id_parent_flashcard = pk_str + '_parent_flashcard'
    #Checking if parent flashcard for this list exists
    try:
        request.session[list_id_parent_flashcard]
    except KeyError:
        try:
            parent_flashcard = Flashcard.objects.filter(list_id = pk).order_by('-repeat_date')[0]
            request.session[list_id_parent_flashcard] = str(parent_flashcard.id)
        except IndexError:
            return render(request,no_flashcard_template, {'list_object':list_object, 'pk': pk })
    
    pid_flashcard = int(request.session[list_id_parent_flashcard])
 
    #Select flashcard depending on status, exclude parent flashcard
    try:
        if int(request.session[status]) < 5:
            #For flashcard status form 0 to 4 select the oldest flashacards
            flashcard = Flashcard.objects.filter(list_id = pk).filter().exclude(pk=pid_flashcard).order_by('repeat_date')[0]
        elif int(request.session[status]) < 6:
            #For flashcard status = 5, the oldest flashcard form most difficult flashcards
            flashcard2 = Flashcard.objects.filter(list_id = pk).exclude(pk = pid_flashcard).order_by('-difficulty')[0]
            flashcard = Flashcard.objects.filter(list_id = pk).exclude(pk = pid_flashcard).filter(difficulty = flashcard2.difficulty).order_by('repeat_date')[0]      
        elif int(request.session[status]) < 8: 
            #For flashcard status from 6 to 7 select most difficult flashcard
            flashcard = Flashcard.objects.filter(list_id = pk).exclude(pk = pid_flashcard).order_by('-difficulty')[0]
    except IndexError:
        try:
            flashcard = Flashcard.objects.filter(list_id = pk).filter().order_by('repeat_date')[0] 
        except IndexError:
            return render(request,no_flashcard_template,{'list_object':list_object, 'pk': pk })
    #Update flashcard status
    if int(request.session[status]) < 7:
        stat = int(request.session[status])
        stat = stat + 1
        request.session[status] = str(stat)
    else:
        request.session[status] = str(1)
    
    #Set current flashcard for this list
    request.session[list_id_current_flashcard] = str(flashcard.pk)
    return render(request, template_name, {'list_object':list_object, 'flashcard':flashcard, 'pk': pk, 'flashcard_status':flashcard_status})
    
def update_flashcard(request,list_pk, answer_value, flashcard_pk):
    parent_flashcard = str(list_pk) + '_parent_flashcard'
    current_flashcard = str(list_pk) + '_current_flashcard'
    pk_str = str(list_pk)
    #Update flashcard counter for this session
    try:
        counter = request.session[pk_str]
        counter_int = int(counter)
        counter_int = counter_int + 1
        counter = str(counter_int)
        request.session[pk_str] = counter
    except KeyError:
        request.session[pk_str] = str(0)
    try:
        request.session[current_flashcard]  
    except KeyError:
        messages.error(request, 'Cannot find current flashcard')
        return redirect('list')
    try:
        updated_flashcard = Flashcard.objects.get(id = flashcard_pk)
        flashcard_list = List.objects.get(id=list_pk)
    except error:
        raise Http404
    if (request.user != flashcard_list.owner):
        raise Http404

    if updated_flashcard.difficulty < 0.0002: #The least possible difficulty is 0.0002
        updated_flashcard.difficulty = 0.0002 
    elif updated_flashcard.difficulty > 1.0: #Difficulties bigger then 1 should be rounded
        updated_flashcard.difficulty = round(updated_flashcard.difficulty, 1)
    
    #Upadate flashcard difficulty depending on answer value
    if answer_value == '3':
        updated_flashcard.difficulty *= 0.5 #Value 3(simple), division by 2
    else:
        updated_flashcard.difficulty *= float(answer_value) # Value 1(hard) - difficulty stays the same; Value 2(wrong) - multiplication by 2

    updated_flashcard.repeat_date = timezone.now() #Upadate repeat date
    updated_flashcard.save() #Save to database

    try:
        request.session[parent_flashcard]
    except KeyError:
        parent_flashcard_object = Flashcard.objects.filter(list_id = pk).order_by('-repeat_date')[0]
        request.session[parent_flashcard] = str(parent_flashcard_object.id)

    request.session[parent_flashcard] = request.session[current_flashcard] #Update parent flashcard
    #Revise again  
    return revise(request, list_pk)

def limit(request, pk):
    if request.method == "POST":
        form = LimitForm(data=request.POST)
        if form.is_valid():
            try:
                #Select list object
                list_object = List.objects.filter(owner=request.user, pk = pk)[0]
            except IndexError:
                messages.error(request, 'This list is not yours.')
                return redirect('list')
            #Update limit and save to database
            list_object.limit = form.cleaned_data['limit']   
            list_object.save()
            return redirect('list')
        else:
            return render(request, 'repeat/change_limit.html', {'form' : form })
            
    else:
        form = LimitForm()
        return render(request, 'repeat/change_limit.html', {'form' : form })

